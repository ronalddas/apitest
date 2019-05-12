from home import app
import unittest



class FlaskBookshelfTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        # creates a test client
        self.app = app.test_client()
        # propagate the exceptions to the test client
        self.app.testing = True

    def tearDown(self):
        pass

    def geo_json(self,lat,long):
        return self.app.get('/get_using_geojson',
                            json=dict(lat=lat,long=long))

    def earth_distance_postgres(self,lat,long,radius):
        return self.app.get('/get_using_postgres',
                            json=dict(lat=lat,long=long,radius=radius))

    def earth_distance_self(self,lat,long,radius):
        return self.app.get('/get_using_self',
                            json=dict(lat=lat,long=long,radius=radius))

    def post_locations(self,data_dict):
        return self.app.post('/post_location',
                            json=data_dict)



    def test_home(self):
        # sends HTTP GET request to the application
        # on the specified path
        result = self.app.get('/')

        # assert the response data
        self.assertEqual(result.data, b'OK')
        self.assertEqual(result.status_code, 200)

    def test_get_post_locations(self):
        ##Test Case for existing Pincode
        data_dict={'ID': 72, 'PINCODE': 'IN/110083', 'NAME': 'Mangolpuri Block A', 'STATE': 'New Delhi',
                   'LATITUDE': 28.6488, 'LONGITUDE': 77.1726}
        result=self.post_locations(data_dict)
        self.assertIsInstance(result.json, dict)
        self.assertEqual(len(result.json.get('location')), 1)
        self.assertEqual(result.json.get('location')[0][0], 72)
        self.assertEqual(result.status_code, 200)

        ## Test case for similar Latitude , Longitude
        data_dict = {'ID': 72, 'PINCODE': 'IN/110083', 'NAME': 'Mangolpuri Block A', 'STATE': 'New Delhi',
                     'LATITUDE': 28.64, 'LONGITUDE': 77.17}
        result = self.post_locations(data_dict)
        self.assertIsInstance(result.json, dict)
        self.assertEqual(len(result.json.get('location')), 27)
        self.assertEqual(result.json.get('location')[0][0], 19)
        self.assertEqual(result.json.get('location')[-1][1],'IN/110096')
        self.assertEqual(result.status_code, 200)


    def test_get_using_self(self):
        #Test Case for Zero Locations within 5000m
        result = self.earth_distance_self(77.5, 28.6,5000)
        self.assertIsInstance(result.json, dict)
        self.assertEqual(len(result.json.get('locations')), 0)
        self.assertEqual(result.status_code, 200)

        #Test case for a single location within 7000m
        result = self.earth_distance_self(28.6,77.5,7000)
        self.assertIsInstance(result.json, dict)
        self.assertIsInstance(result.json.get('locations'), list)
        self.assertEqual(len(result.json.get('locations')), 1)
        self.assertEqual(result.json.get('locations')[0][1], 'IN/203207')
        self.assertEqual(result.status_code, 200)

        #Test case for multiple locations within 25KM
        result = self.earth_distance_self(28.6, 77.5, 25000)
        self.assertIsInstance(result.json, dict)
        self.assertIsInstance(result.json.get('locations'), list)
        self.assertEqual(len(result.json.get('locations')), 15)
        self.assertEqual(result.json.get('locations')[2][1], 'IN/110011')
        self.assertEqual(result.status_code, 200)

    def test_get_using_postgres(self):
        # Test Case for Zero Locations within 5000m
        result = self.earth_distance_postgres(77.5, 28.6,5000)
        self.assertIsInstance(result.json, dict)
        self.assertEqual(len(result.json.get('locations')), 0)
        self.assertEqual(result.status_code, 200)

        # Test case for a single location within 7000m
        result = self.earth_distance_postgres(28.6,77.5,5000)
        self.assertIsInstance(result.json, dict)
        self.assertIsInstance(result.json.get('locations'), list)
        self.assertEqual(len(result.json.get('locations')), 1)
        self.assertEqual(result.json.get('locations')[0][1], 'IN/203207')
        self.assertEqual(result.status_code, 200)

        # Test case for multiple locations within 25KM
        result = self.earth_distance_postgres(28.6, 77.5, 25000)
        self.assertIsInstance(result.json, dict)
        self.assertIsInstance(result.json.get('locations'), list)
        self.assertEqual(len(result.json.get('locations')), 19)
        self.assertEqual(result.json.get('locations')[2][1], 'IN/110011')
        self.assertEqual(result.status_code, 200)

    def test_get_using_geojson(self):
        # Test Case for location not in any area
        result = self.geo_json(77.5,28.6)
        self.assertIsInstance(result.json,dict)
        self.assertEqual(len(result.json.get('areas')), 0)
        self.assertEqual(result.status_code, 200)

        # Test case for location in a area
        result = self.geo_json(28.4908, 77.0690)
        self.assertIsInstance(result.json, dict)
        self.assertIsInstance(result.json.get('areas'),list)
        self.assertEqual(len(result.json.get('areas')), 1)
        self.assertEqual(result.json.get('areas')[0][1], 'Gurgaon')
        self.assertEqual(result.status_code, 200)

        # Test case for boundary point,i.e multiple locations
        result = self.geo_json(28.524246963021376, 77.05505847930908)
        self.assertIsInstance(result.json, dict)
        self.assertIsInstance(result.json.get('areas'), list)
        self.assertEqual(len(result.json.get('areas')), 2)
        self.assertEqual(result.json.get('areas')[0][1], 'Gurgaon')
        self.assertEqual(result.json.get('areas')[1][1], 'South West Delhi')
        self.assertEqual(result.status_code, 200)
