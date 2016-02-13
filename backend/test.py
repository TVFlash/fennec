import unittest
import json
from server import app

class CrawlerTestCase(unittest.TestCase):
	def runTest(self):
		test_app = app.test_client()
		
		response = test_app.get('/api/search/youtube')
		json_data = json.loads(response.data)
		self.assertEquals(response.status, '201 CREATED')
		self.assertEquals(json_data['status'], 'failure')
		self.assertEquals(json_data['description'], 'missing argument \'q\'')
		
		response = test_app.get('/api/search/youtube', query_string='q=iceskating+trex')
		json_data = json.loads(response.data)
		self.assertEquals(response.status, '201 CREATED')
		self.assertEquals(json_data['status'], 'success')
		self.assertIsNotNone(json_data['items'])
		
		response = test_app.get('/api/search/youtube', query_string='q=iceskating+trex&debug=afdsaf')
		json_data = json.loads(response.data)
		self.assertEquals(response.status, '201 CREATED')
		self.assertEquals(json_data['status'], 'failure')
		self.assertEquals(json_data['description'], 'argument \'d\' should be \'true\' or \'false\'')
		
		response = test_app.get('/api/search/soundcloud')
		json_data = json.loads(response.data)
		self.assertEquals(response.status, '201 CREATED')
		self.assertEquals(json_data['status'], 'failure')
		self.assertEquals(json_data['description'], 'missing argument \'q\'')
		
		response = test_app.get('/api/search/soundcloud', query_string='q=iceskating+trex')
		json_data = json.loads(response.data)
		self.assertEquals(response.status, '201 CREATED')
		self.assertEquals(json_data['status'], 'success')
		self.assertIsNotNone(json_data['items'])
		
		response = test_app.get('/api/search/soundcloud', query_string='q=iceskating+trex&debug=afdsaf')
		json_data = json.loads(response.data)
		self.assertEquals(response.status, '201 CREATED')
		self.assertEquals(json_data['status'], 'failure')
		self.assertEquals(json_data['description'], 'argument \'d\' should be \'true\' or \'false\'')
		
if __name__ == '__main__':
	unittest.main()