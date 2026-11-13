import pandas as pd
from django.test import TestCase

from .Tool_W1_MollierDiagram import (
    adjust_humidity_ratio_for_pressure,
    build_comfort_zone_polygon,
    calculate_partial_vapor_pressure,
    mollier_graph,
    pressure_at_height,
)
from .Tool_A4_NLsfB import get_parent_code
from .models import ConceptSfbLink, InstallatieConcept, SfbClass
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
