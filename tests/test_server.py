import http.client
import json
import threading
import unittest
from commute_map.server import make_server


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=make_server(0)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join()

    def request(self,method,path,body=None):
        connection=http.client.HTTPConnection("127.0.0.1",self.server.server_port,timeout=10)
        connection.request(method,path,body,headers={"Content-Type":"application/json"})
        response=connection.getresponse();data=response.read();status=response.status
        headers=dict(response.getheaders());connection.close()
        return status,data,headers

    def test_health_and_static_assets(self):
        for path in ("/","/app.js","/style.css","/health"):
            status,body,headers=self.request("GET",path)
            self.assertEqual(status,200);self.assertGreater(len(body),0)
            self.assertIn("Content-Security-Policy",headers)

    def test_run_and_export(self):
        for path in ("/api/run","/api/export"):
            status,body,_=self.request("POST",path,json.dumps({"size":16}))
            self.assertEqual(status,200);self.assertIsInstance(json.loads(body),dict)

    def test_bad_json_and_inputs_return_400(self):
        for body in ("oops","[]",'{"threshold":NaN}','{"budget":-1}',
                     json.dumps({"threshold":10**400}),"{}"*5000):
            status,data,_=self.request("POST","/api/run",body)
            self.assertEqual(status,400);self.assertIn("error",json.loads(data))

    def test_unknown_and_traversal_paths_return_404(self):
        for path in ("/missing","/../PROJECT_STATE.md","/static/../../etc/passwd"):
            self.assertEqual(self.request("GET",path)[0],404)
        self.assertEqual(self.request("POST","/api/missing","{}")[0],404)
