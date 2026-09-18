import math
import random
import unittest
from commute_map.model import Edge, Graph, Node, Policy
from commute_map.routing import RoutingIndex, classify
from commute_map.scenarios import build_scenario


class ConceptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scenario = build_scenario(16)

    def index(self,buffer=0,condo=5,direction="work_to_home",period="example"):
        return RoutingIndex(self.scenario.graph,"KLCC",direction,Policy(period,buffer,condo))

    def test_users_corridor_plus_local_examples(self):
        index = self.index()
        sb,rawang = index.route("SB_HOUSE"),index.route("RAWANG_HOUSE")
        self.assertEqual((sb.corridor_minutes,sb.local_minutes,sb.planning_minutes),(30,18,48))
        self.assertEqual((rawang.corridor_minutes,rawang.local_minutes,rawang.planning_minutes),(35,5,40))
        self.assertEqual(classify(sb,45),"outside")
        self.assertEqual(classify(rawang,45),"inside")

    def test_local_access_is_not_one_value_per_suburb(self):
        index = self.index(condo=0)
        self.assertEqual(index.route("CHERAS_HOUSE").planning_minutes,42)
        self.assertEqual(index.route("CHERAS_CONDO").planning_minutes,26)

    def test_condo_adds_exactly_five_once(self):
        for direction in ("home_to_work","work_to_home"):
            a,b = self.index(condo=0,direction=direction),self.index(condo=5,direction=direction)
            self.assertEqual(b.route("CHERAS_CONDO").planning_minutes-a.route("CHERAS_CONDO").planning_minutes,5)
            self.assertEqual(b.route("CHERAS_HOUSE"),a.route("CHERAS_HOUSE"))

    def test_distance_buffer_is_minutes_not_a_score(self):
        route = self.index(buffer=.2).route("SB_HOUSE")
        self.assertEqual(route.distance_km,30)
        self.assertEqual(route.buffer_minutes,6)
        self.assertEqual(route.planning_minutes,54)

    def test_reverse_direction_is_separate(self):
        self.assertEqual(self.index().route("SB_HOUSE").planning_minutes,48)
        inbound = self.index(direction="home_to_work").route("SB_HOUSE")
        self.assertEqual(inbound.planning_minutes,52)
        self.assertEqual(inbound.nodes,("SB_HOUSE","SB","KLCC"))

    def test_assumed_peak_profile_changes_cost(self):
        route = self.index(direction="home_to_work",period="morning").route("SB_HOUSE")
        self.assertAlmostEqual(route.planning_minutes,34*1.3+18*1.25)

    def test_farther_entrance_can_win(self):
        route = self.index().route("ALTERNATIVE")
        self.assertEqual(route.nodes,("KLCC","RAWANG","ALTERNATIVE"))
        self.assertEqual(route.planning_minutes,40)

    def test_buffer_can_change_the_best_route(self):
        route = self.index(buffer=1).route("ALTERNATIVE")
        self.assertEqual(route.nodes,("KLCC","SB","ALTERNATIVE"))
        self.assertEqual(route.planning_minutes,76)

    def test_no_route_has_no_duration(self):
        route = self.index().route("ISOLATED")
        self.assertIsNone(route.planning_minutes)
        self.assertEqual(classify(route,999),"no_route")

    def test_threshold_equality_is_inside(self):
        route = self.index().route("SB_HOUSE")
        self.assertEqual(classify(route,48),"inside")
        self.assertEqual(classify(route,47.99),"outside")

    def test_increasing_buffer_never_improves_optimum(self):
        indices = [self.index(buffer=v) for v in (0,.1,.5,1,3)]
        for home in self.scenario.examples[:-1]:
            values = [i.route(home).planning_minutes for i in indices]
            self.assertEqual(values,sorted(values))

    def test_private_home_cannot_be_used_as_shortcut(self):
        graph = Graph()
        for key,home in (("W",False),("H",True),("A",False),("B",True)):
            graph.add_node(Node(key,0,0,home=home))
        for a,b,cost in (("W","H",1),("H","A",1),("A","B",1),("W","A",20)):
            graph.add_edge(Edge(a,b,cost,0))
        route = RoutingIndex(graph,"W","work_to_home",Policy()).route("B")
        self.assertEqual(route.planning_minutes,21)

    def test_invalid_weight_and_policy_inputs(self):
        for value in (-1,float("nan"),float("inf"),True,"3"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError): Edge("a","b",value,0)
                with self.assertRaises(ValueError): Policy(buffer_min_per_km=value)
        with self.assertRaises(ValueError): Policy(period="now")
        with self.assertRaises(ValueError): Edge("a","b",1,1,"unrecognized")

    def test_invalid_graph_and_query(self):
        graph = Graph();graph.add_node(Node("W",0,0))
        with self.assertRaises(ValueError): graph.add_node(Node("W",0,0))
        with self.assertRaises(ValueError): graph.add_edge(Edge("W","missing",1,1))
        with self.assertRaises(ValueError): RoutingIndex(graph,"missing","home_to_work",Policy())
        with self.assertRaises(ValueError): RoutingIndex(graph,"W","sideways",Policy())
        with self.assertRaises(ValueError): self.index().route("missing")

    def test_overflow_rejected(self):
        graph = Graph()
        graph.add_node(Node("W",0,0));graph.add_node(Node("H",1,1,home=True))
        graph.add_edge(Edge("W","H",1e308,1e308,morning_factor=1e308))
        with self.assertRaises(ValueError): RoutingIndex(graph,"W","work_to_home",Policy("morning"))


class IndependentReferenceTests(unittest.TestCase):
    def test_random_graphs_against_floyd_warshall(self):
        """Independent all-pairs DP checks both directions, ties and zero costs."""
        for seed in range(30):
            randomizer = random.Random(seed)
            graph = Graph(); count=9
            for i in range(count): graph.add_node(Node(str(i),i,0,home=i>=6,condo=i==8))
            reference = [[math.inf]*count for _ in range(count)]
            for i in range(count): reference[i][i]=0
            policy=Policy("example",.3,5)
            for a in range(count):
                for b in range(count):
                    if a!=b and randomizer.random()<.24:
                        minutes,km=randomizer.randrange(0,20),randomizer.randrange(0,8)
                        graph.add_edge(Edge(str(a),str(b),minutes,km))
                        reference[a][b]=min(reference[a][b],minutes+.3*km)
            # Private endpoints cannot be intermediate vertices.
            for k in range(6):
                for i in range(count):
                    for j in range(count):
                        reference[i][j]=min(reference[i][j],reference[i][k]+reference[k][j])
            for direction in ("home_to_work","work_to_home"):
                index=RoutingIndex(graph,"0",direction,policy)
                for home in range(6,9):
                    expected=reference[home][0] if direction=="home_to_work" else reference[0][home]
                    route=index.route(str(home))
                    with self.subTest(seed=seed,direction=direction,home=home):
                        if math.isinf(expected): self.assertEqual(route.status,"no_route")
                        else:
                            self.assertAlmostEqual(route.planning_minutes,expected+(5 if home==8 else 0))
                            self.assertEqual((route.nodes[0],route.nodes[-1]),
                                             (str(home),"0") if direction=="home_to_work" else ("0",str(home)))
