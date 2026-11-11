from django.test import TestCase

from .Tool_W1_MollierDiagram import build_comfort_zone_polygon, mollier_graph


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
