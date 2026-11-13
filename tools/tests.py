import json
from io import BytesIO

import pandas as pd
from PyPDF2 import PdfReader
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .Tool_W1_MollierDiagram import (
    adjust_humidity_ratio_for_pressure,
    build_comfort_zone_polygon,
    calculate_comfort_statistics,
    calculate_partial_vapor_pressure,
    heatmapNEN5060,
    mollier_graph,
    pressure_at_height,
)
from .Tool_A4_NLsfB import get_parent_code
from .models import ConceptSfbLink, InstallatieConcept, ProjectMollier, SfbClass
from .services.nl_sfb_concepts import DEFAULT_CONCEPTS, seed_default_concepts
from .services.sfb_scoring import analyse_search_term


class ComfortZonePolygonTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.C_values = mollier_graph()[3]

    def test_default_zone_has_curved_boundaries(self):
        polygon = build_comfort_zone_polygon(
            20, 24, 30, 70, 101325, self.C_values
        )

        self.assertEqual(len(polygon), 34)
        self.assertEqual(polygon[0]["y"], 20)
        self.assertEqual(polygon[16]["y"], 24)
        self.assertEqual(polygon[17]["y"], 24)
        self.assertEqual(polygon[-1]["y"], 20)

    def test_zone_uses_pressure_at_the_selected_altitude(self):
        sea_level_polygon = build_comfort_zone_polygon(
            20, 24, 30, 70, 101325, self.C_values
        )
        high_altitude_pressure = 101325 * (1 - 2.25577e-5 * 3000) ** 5.256
        high_altitude_polygon = build_comfort_zone_polygon(
            20, 24, 30, 70, high_altitude_pressure, self.C_values
        )

        self.assertGreater(
            high_altitude_polygon[0]["x"],
            sea_level_polygon[0]["x"],
        )

    def test_invalid_bounds_are_rejected(self):
        with self.assertRaises(ValueError):
            build_comfort_zone_polygon(
                24, 20, 30, 70, 101325, self.C_values
            )


class ClimateYearPressureTests(TestCase):
    def test_humidity_ratio_is_recalculated_for_altitude_pressure(self):
        source_data = {"x": [8.0]}
        sea_level_pressure = 101325
        high_altitude_pressure = pressure_at_height(2000)

        sea_level_data = adjust_humidity_ratio_for_pressure(
            pd.DataFrame(source_data),
            sea_level_pressure,
        )
        high_altitude_data = adjust_humidity_ratio_for_pressure(
            pd.DataFrame(source_data),
            high_altitude_pressure,
        )

        self.assertGreater(high_altitude_data.loc[0, "x"], sea_level_data.loc[0, "x"])
        self.assertAlmostEqual(
            calculate_partial_vapor_pressure(
                sea_level_data.loc[0, "x"], sea_level_pressure
            ),
            calculate_partial_vapor_pressure(
                high_altitude_data.loc[0, "x"], high_altitude_pressure
            ),
        )


class ComfortStatisticsTests(TestCase):
    def test_vectorized_statistics_preserve_default_results(self):
        _, climate_data = heatmapNEN5060()
        expected = {
            "A": (1693, 7067, 48, 41217, 50, 19.3),
            "B": (3798, 4962, 0, 20917, 0, 43.4),
            "C": (6019, 2741, 0, 7797, 0, 68.7),
        }

        for comfort_class, values in expected.items():
            with self.subTest(comfort_class=comfort_class):
                result = calculate_comfort_statistics(
                    climate_data,
                    comfort_class,
                )
                self.assertEqual(
                    (
                        result["comfort_hours"],
                        result["heating_hours"],
                        result["dehumidification_hours"],
                        result["heat_energy_kwh"],
                        result["dehumidification_kg"],
                        result["comfort_factor"],
                    ),
                    values,
                )


class MollierPdfExportTests(TestCase):
    def test_pdf_defaults_missing_project_details_to_not_determined(self):
        user = User.objects.create_user(username="mollier-pdf-defaults-user")
        self.client.force_login(user)

        response = self.client.post(
            reverse("tools:generate_pdf_W1"),
            {
                "SavePDFButton": "clicked",
                "table_points_json": "[]",
                "table_process_json": "[]",
            },
        )

        self.assertEqual(response.status_code, 200)
        first_page = PdfReader(BytesIO(response.content)).pages[0]
        exported_text = " ".join(first_page.extract_text().split())
        self.assertGreaterEqual(exported_text.count("n.t.b."), 4)

    def test_pdf_includes_project_and_start_condition_inputs(self):
        user = User.objects.create_user(username="mollier-pdf-user")
        self.client.force_login(user)

        response = self.client.post(
            reverse("tools:generate_pdf_W1"),
            {
                "SavePDFButton": "clicked",
                "project_name": "Project & gebouw",
                "project_number": "P-123",
                "season": "Winter",
                "room_name": "LBK hoofdgebouw",
                "qv_var": "12500",
                "Height_var": "350",
                "varStart1": "Tdb",
                "StartInput1": "22.5",
                "varStart2": "RH",
                "StartInput2": "55",
                "table_points_json": "[]",
                "table_process_json": "[]",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        first_page = PdfReader(BytesIO(response.content)).pages[0]
        exported_text = " ".join(first_page.extract_text().split())
        second_page_text = PdfReader(BytesIO(response.content)).pages[1].extract_text()

        for value in (
            "Project & gebouw",
            "P-123",
            "Winter",
            "LBK hoofdgebouw",
            "12.500 m3/h",
            "350 m",
            "Startpunt",
            "Drogeboltemperatuur",
            "22,5",
            "Relatieve luchtvochtigheid",
            "55 %",
        ):
            with self.subTest(value=value):
                self.assertIn(value, exported_text)

        self.assertIn("Informatie over de Processen", second_page_text)
        self.assertIn("Drogeboltemperatuur", second_page_text)

    def test_pdf_tables_fit_all_five_points_and_four_processes(self):
        user = User.objects.create_user(username="mollier-table-user")
        self.client.force_login(user)
        point_rows = [
            ["Punt", "Tdb", "Tnb", "Tdauw", "X", "H", "RH", "Pw", "rho", "Qv"],
            ["", "[C]", "[C]", "[C]", "[g/kg]", "[kJ/kg]", "[%]", "[Pa]", "[kg/m3]", "[m3/h]"],
        ]
        point_rows.extend(
            [[str(point), "20", "15", "10", "8", "40", "50", "1200", "1.2", "10000"]
             for point in range(5)]
        )
        process_rows = [
            ["Proces", "Actie 1", "Actie 2", "Delta T", "Delta X", "Delta H", "P totaal", "P voelbaar", "P latent", "VWF"],
            ["", "", "", "[C]", "[g/kg]", "[kJ/kg]", "[kW]", "[kW]", "[kW]", "[-]"],
        ]
        process_rows.extend(
            [[f"Proces {step}", "Verwarmen", "", "2", "0", "2", "1", "1", "0", "1"]
             for step in range(1, 5)]
        )

        response = self.client.post(
            reverse("tools:generate_pdf_W1"),
            {
                "SavePDFButton": "clicked",
                "table_points_json": json.dumps(point_rows),
                "table_process_json": json.dumps(process_rows),
            },
        )

        self.assertEqual(response.status_code, 200)
        first_page_text = PdfReader(BytesIO(response.content)).pages[0].extract_text()
        for value in ("0", "1", "2", "3", "4", "Proces 1", "Proces 2", "Proces 3", "Proces 4"):
            with self.subTest(value=value):
                self.assertIn(value, first_page_text)


class MollierProjectPersistenceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="mollier-project-user")
        self.client.force_login(self.user)

    def test_save_and_load_project_restores_saved_form_state(self):
        state = {
            "qv_var": "8500",
            "varStart1": "Tdb",
            "StartInput1": "24",
            "currentProces": "2",
        }
        save_response = self.client.post(
            reverse("tools:save_project"),
            data=json.dumps({
                "projectname": "Zomersituatie",
                "sessionstorage": state,
            }),
            content_type="application/json",
        )

        self.assertEqual(save_response.status_code, 200)
        project = ProjectMollier.objects.get(
            user=self.user,
            projectname="Zomersituatie",
        )
        self.assertEqual(project.sessionstorage, state)

        load_response = self.client.post(
            reverse("tools:load_project"),
            data=json.dumps({"project_id": project.pk}),
            content_type="application/json",
        )

        self.assertEqual(load_response.status_code, 200)
        self.assertEqual(load_response.json(), {"status": "ok"})
        self.assertEqual(
            self.client.session["restored_sessionstorage"],
            state,
        )

    def test_delete_project_accepts_json_and_returns_json(self):
        project = ProjectMollier.objects.create(
            user=self.user,
            projectname="Wintersituatie",
            sessionstorage={"qv_var": "10000"},
        )

        response = self.client.post(
            reverse("tools:delete_project"),
            data=json.dumps({"project_id": project.pk}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "deleted"})
        self.assertFalse(ProjectMollier.objects.filter(pk=project.pk).exists())


class MollierExamplePresetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="mollier-example-user")
        self.client.force_login(self.user)

    def test_examples_are_available_without_user_saved_projects(self):
        response = self.client.get(reverse("tools:mollier"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Zomersituatie")
        self.assertContains(response, "Wintersituatie")
        self.assertContains(response, "loadMollierPreset('summer')")
        self.assertContains(response, "loadMollierPreset('winter')")
        self.assertFalse(ProjectMollier.objects.filter(user=self.user).exists())

    def test_example_process_inputs_generate_process_rows(self):
        examples = (
            {
                "currentProces": "1,2,3",
                "comfort_temp_min": "21",
                "comfort_temp_max": "24",
                "comfort_rh_min": "30",
                "comfort_rh_max": "70",
                "qv_var": "10000",
                "varStart1": "Tdb",
                "StartInput1": "32",
                "varStart2": "RH",
                "StartInput2": "40",
                "proces1": "heat_rec",
                "inputproces1_name": "Warmtewiel",
                "Proces1_value4_input": "24",
                "Proces1_value6_input": "50",
                "Proces1_value7_input": "80",
                "Proces1_value8_input": "80",
                "proces2": "cool",
                "proces2_func": "power",
                "inputproces2_name": "Koelbatterij",
                "Proces2_value1_input": "80",
                "Proces2_value2_input": "100",
                "proces3": "heat",
                "proces3_func": "toTemp",
                "inputproces3_name": "Naverwarming",
                "Proces3_value2_input": "16",
            },
            {
                "currentProces": "1,2",
                "comfort_temp_min": "21",
                "comfort_temp_max": "24",
                "comfort_rh_min": "30",
                "comfort_rh_max": "70",
                "qv_var": "10000",
                "varStart1": "Tdb",
                "StartInput1": "-8",
                "varStart2": "AH",
                "StartInput2": "1",
                "proces1": "heat_rec",
                "inputproces1_name": "Warmtewiel",
                "Proces1_value4_input": "21",
                "Proces1_value6_input": "40",
                "Proces1_value7_input": "80",
                "Proces1_value8_input": "80",
                "proces2": "heat",
                "proces2_func": "toTemp",
                "inputproces2_name": "Naverwarming",
                "Proces2_value2_input": "22",
            },
        )
        expected_process_names = (
            ("Warmtewiel", "Koelbatterij", "Naverwarming"),
            ("Warmtewiel", "Naverwarming"),
        )

        for form_data, expected_names in zip(examples, expected_process_names):
            with self.subTest(start=form_data["StartInput1"]):
                response = self.client.post(reverse("tools:mollier"), form_data)

                self.assertEqual(response.status_code, 200)
                for process_name in expected_names:
                    self.assertContains(response, process_name)
                self.assertContains(
                    response,
                    'id="comfortTempMin" name="comfort_temp_min"\n'
                    '                               value="21"',
                )
                self.assertContains(
                    response,
                    'id="comfortTempMax" name="comfort_temp_max"\n'
                    '                               value="24"',
                )
                self.assertContains(
                    response,
                    'id="comfortRhMin" name="comfort_rh_min"\n'
                    '                               value="30"',
                )
                self.assertContains(
                    response,
                    'id="comfortRhMax" name="comfort_rh_max"\n'
                    '                               value="70"',
                )


class NlSfbSearchTests(TestCase):
    def create_class(self, code, description):
        return SfbClass.objects.create(
            classificatie="NL-SfB",
            taal="nl",
            tabel="1",
            code=code,
            code_tekst="",
            omschrijving=description,
        )

    def test_search_matches_plural_and_compound_terms(self):
        self.create_class("57.4", "luchtbehandeling; ventilatoren")

        results = analyse_search_term("ventilator")

        self.assertEqual(results["werktuigbouwkundig"][0]["code"], "57.4")

    def test_search_matches_nl_sfb_code(self):
        self.create_class("57.31", "luchtbehandeling")

        results = analyse_search_term("57.31")

        self.assertEqual(results["werktuigbouwkundig"][0]["code"], "57.31")

    def test_search_uses_configured_concept_synonyms(self):
        sfb_class = self.create_class("56.81", "verwarming; afgifte")
        concept = InstallatieConcept.objects.create(
            naam="radiator",
            synoniemen="verwarmingselement, heater",
        )
        ConceptSfbLink.objects.create(
            concept=concept,
            sfb=sfb_class,
            rol="werktuigbouwkundig",
        )

        results = analyse_search_term("heater")

        self.assertEqual(results["werktuigbouwkundig"][0]["code"], "56.81")

    def test_parent_code_follows_each_nl_sfb_level(self):
        self.assertEqual(get_parent_code("57.3"), "57")
        self.assertEqual(get_parent_code("57.31"), "57.3")
        self.assertEqual(get_parent_code("57.311"), "57.31")

    def test_default_search_concepts_are_seeded_idempotently(self):
        codes = {
            code
            for concept in DEFAULT_CONCEPTS.values()
            for code in concept["links"]
        }
        for code in codes:
            self.create_class(code, f"NL-SfB testclassificatie {code}")

        seed_default_concepts()
        initial_link_count = ConceptSfbLink.objects.count()
        seed_default_concepts()

        self.assertEqual(ConceptSfbLink.objects.count(), initial_link_count)
        ventilation_results = analyse_search_term("ventilatoren")
        toilet_results = analyse_search_term("wc")
        outlet_results = analyse_search_term("stopcontacten")

        self.assertEqual(
            {item["code"] for item in ventilation_results["werktuigbouwkundig"]},
            {"57.21", "57.31"},
        )
        self.assertEqual(toilet_results["bouwkundig"][0]["code"], "74.11")
        self.assertEqual(outlet_results["elektrotechnisch"][0]["code"], "62.12")

    def test_search_api_returns_synonym_matches(self):
        sfb_class = self.create_class("57.31", "luchtbehandeling")
        concept = InstallatieConcept.objects.create(
            naam="Ventilator",
            synoniemen="ventilatoren",
        )
        ConceptSfbLink.objects.create(
            concept=concept,
            sfb=sfb_class,
            rol="werktuigbouwkundig",
        )
        self.client.force_login(User.objects.create_user(username="search-user"))

        response = self.client.get(
            reverse("tools:sfb_search"),
            {"q": "ventilatoren"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["routes"]["werktuigbouwkundig"][0]["code"],
            "57.31",
        )
