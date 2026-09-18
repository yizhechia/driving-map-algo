import json
import unittest
from commute_map.app import configuration, run, export


class AppTests(unittest.TestCase):
    def test_defaults_produce_complete_inspectable_grid(self):
        result=run({"size":16})
        self.assertEqual(result["grid"]["queries"],256)
        self.assertEqual(len(result["cell_details"]),256)
        self.assertEqual(result["manifest"]["paid_api_calls"],0)
        self.assertEqual(result["manifest"]["source"],"synthetic_kl_v1")
        json.dumps(result,allow_nan=False)

    def test_total_equals_all_components(self):
        for example in run({"size":16})["examples"]:
            if example["planning_minutes"] is not None:
                self.assertAlmostEqual(example["planning_minutes"],sum(example["breakdown"].values()))

    def test_unqueried_cells_have_no_leaked_route_details(self):
        result=run({"size":16,"method":"adaptive","budget":64})
        self.assertEqual(len(result["cell_details"]),result["grid"]["queries"])
        self.assertLessEqual(len(result["cell_details"]),64)

    def test_invalid_configuration_is_rejected(self):
        cases=[[],{"unknown":1},{"size":32.0},{"size":True},{"size":1000},
               {"threshold":0},{"threshold":float("nan")},{"threshold":True},
               {"threshold":10**400},
               {"buffer_min_per_km":-1},{"buffer_min_per_km":6},{"condo_minutes":61},
               {"budget":1.5},{"budget":-1},{"budget":10000},{"period":"live"},
               {"direction":"both"},{"method":"fake"}]
        for case in cases:
            with self.subTest(case=case),self.assertRaises(ValueError):configuration(case)

    def test_directions_and_profiles_all_serialize(self):
        for direction in ("home_to_work","work_to_home"):
            for period in ("example","morning","evening"):
                for method in ("full","uniform","adaptive"):
                    data=run({"size":16,"direction":direction,"period":period,"method":method,"budget":100})
                    json.dumps(data,allow_nan=False)
                    self.assertLessEqual(data["grid"]["queries"],100)

    def test_export_includes_settings_and_synthetic_provenance(self):
        result=export({"size":16,"threshold":45})
        self.assertEqual(result["type"],"FeatureCollection")
        self.assertEqual(result["config"]["threshold"],45)
        self.assertIn("Synthetic",result["data_source"])

    def test_zero_budget_preserves_unknown_coverage(self):
        result=run({"size":16,"budget":0})
        self.assertEqual(result["grid"]["counts"]["unknown"],256)
        self.assertEqual(result["outline"],[])

    def test_larger_buffer_cannot_expand_exact_inside_set(self):
        a=run({"size":16,"buffer_min_per_km":0})["grid"]["labels"]
        b=run({"size":16,"buffer_min_per_km":1})["grid"]["labels"]
        for y in range(16):
            for x in range(16):
                if b[y][x]=="inside":self.assertEqual(a[y][x],"inside")
