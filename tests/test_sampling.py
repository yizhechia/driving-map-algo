import unittest
from commute_map.sampling import Observation, QueryBudget, sample_grid
from commute_map.contours import boundary_segments, feature_collection

class SamplingTests(unittest.TestCase):
    def test_full_scan_matches_each_reference_cell(self):
        grid=sample_grid(lambda x,y:Observation("ok",x+y),16,12,256)
        self.assertEqual(grid["queries"],256)
        self.assertEqual(grid["estimated_cells"],0)
        for y in range(16):
            for x in range(16):self.assertEqual(grid["labels"][y][x],"inside" if x+y<=12 else "outside")
    def test_all_methods_respect_budget_including_zero(self):
        for method in ("full","uniform","adaptive"):
            for budget in (0,1,3,17,64,100,255,256):
                seen=[]
                def oracle(x,y):seen.append((x,y));return Observation("ok",x+y)
                grid=sample_grid(oracle,16,12,budget,method)
                with self.subTest(method=method,budget=budget):
                    self.assertLessEqual(len(seen),budget)
                    self.assertEqual(len(seen),len(set(seen)))
                    self.assertEqual(grid["queries"],len(seen))
                    self.assertEqual(sum(grid["counts"].values()),256)
                    if budget==0:self.assertEqual(grid["counts"]["unknown"],256)
    def test_queries_are_cached(self):
        q=QueryBudget(lambda x,y:Observation("ok",x+y),1)
        self.assertEqual(q.get((0,0)).minutes,0)
        self.assertEqual(q.get((0,0)).minutes,0)
        self.assertEqual(q.calls,1);self.assertEqual(q.cache_hits,1)
        self.assertEqual(q.get((1,1)).status,"unknown")
    def test_errors_and_no_route_do_not_become_outside(self):
        def oracle(x,y):
            if x==0:raise TimeoutError("fixture")
            if x==1:return Observation("no_route")
            return Observation("ok",5)
        grid=sample_grid(oracle,4,10,16)
        for row in grid["labels"]:self.assertEqual(row,["unknown","no_route","inside","inside"])
    def test_invalid_observations_are_rejected(self):
        for status,value in (("ok",None),("ok",-1),("ok",float("nan")),("no_route",10),("wrong",None)):
            with self.assertRaises(ValueError):Observation(status,value)
    def test_invalid_sampler_settings(self):
        for value in (-1,1.5,True):
            with self.assertRaises(ValueError):sample_grid(lambda x,y:Observation("ok",1),4,5,value)
        with self.assertRaises(ValueError):sample_grid(None,4,5,10,"fake")
    def test_bilinear_uniform_recovers_affine_field(self):
        grid=sample_grid(lambda x,y:Observation("ok",2*x+3*y+1),16,35,16,"uniform")
        for y in range(16):
            for x in range(16):self.assertAlmostEqual(grid["values"][y][x],2*x+3*y+1)
        self.assertEqual(grid["estimated_cells"],240)
    def test_observed_points_always_override_interpolation(self):
        for method in ("uniform","adaptive"):
            grid=sample_grid(lambda x,y:Observation("ok",(x*7+y*11)%29),16,12,100,method)
            for y in range(16):
                for x in range(16):
                    if grid["observed"][y][x]:self.assertEqual(grid["values"][y][x],(x*7+y*11)%29)
    def test_coarse_corners_cannot_guarantee_no_interior_pocket(self):
        oracle=lambda x,y:Observation("ok",1 if (x,y)==(2,2) else 80)
        sparse=sample_grid(oracle,16,45,100,"adaptive")
        full=sample_grid(oracle,16,45,256,"full")
        self.assertEqual(full["labels"][2][2],"inside")
        self.assertEqual(sparse["labels"][2][2],"outside")
        self.assertFalse(sparse["observed"][2][2])
    def test_reproducible_result(self):
        oracle=lambda x,y:Observation("ok",x*x/3+y)
        self.assertEqual(sample_grid(oracle,32,45,256,"adaptive"),sample_grid(oracle,32,45,256,"adaptive"))

class BoundaryTests(unittest.TestCase):
    def test_single_cell_has_four_sides(self):self.assertEqual(len(boundary_segments([["inside"]])),4)
    def test_shared_sides_are_removed(self):self.assertEqual(len(boundary_segments([["inside","inside"]])),6)
    def test_diagonal_pockets_remain_separate(self):
        self.assertEqual(len(boundary_segments([["inside","outside"],["outside","inside"]])),8)
    def test_hole_boundary_is_preserved(self):
        labels=[["inside"]*3 for _ in range(3)];labels[1][1]="outside"
        self.assertEqual(len(boundary_segments(labels)),16)
    def test_unknown_cell_is_not_filled(self):
        self.assertEqual(len(boundary_segments([["inside","unknown"]])),4)
        self.assertEqual(boundary_segments([["outside","no_route"]]),[])
    def test_empty_export_is_valid_collection(self):
        grid=sample_grid(lambda x,y:Observation("ok",100),4,1,16)
        self.assertEqual(feature_collection(grid)["features"],[])
    def test_geojson_rings_closed_and_longitude_first(self):
        grid=sample_grid(lambda x,y:Observation("ok",1),4,5,16)
        collection=feature_collection(grid)
        self.assertEqual(len(collection["features"]),17)
        for feature in collection["features"][:-1]:
            ring=feature["geometry"]["coordinates"][0]
            self.assertEqual(ring[0],ring[-1])
            self.assertTrue(all(100<lon<103 and 2<lat<4 for lon,lat in ring))
