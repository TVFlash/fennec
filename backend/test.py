import unittest
import json
from server import app

class CrawlerTestCase(unittest.TestCase):
	
	def setUp(self):
		app.config['TESTING'] = True
		app.config['LIVESERVER_PORT'] = 2000
		self.test_app = app.test_client()
	
	def test_youtube_no_arg(self):
		response = self.test_app.get('/api/search/youtube')
		json_data = json.loads(response.data)
		self.assertEquals(response.status, '201 CREATED')
		self.assertEquals(json_data['status'], 'failure')
		self.assertEquals(json_data['description'], 'missing argument \'q\'')
		
	def test_youtube_normal(self):
		response = self.test_app.get('/api/search/youtube', query_string='q=iceskating+trex')
		json_data = json.loads(response.data)
		self.assertEquals(response.status, '201 CREATED')
		self.assertEquals(json_data['status'], 'success')
		self.assertIsNotNone(json_data['items'])
		
	def test_youtube_invalid_arg(self):
		response = self.test_app.get('/api/search/youtube', query_string='q=iceskating+trex&debug=abcd')
		json_data = json.loads(response.data)
		self.assertEquals(response.status, '201 CREATED')
		self.assertEquals(json_data['status'], 'failure')
		self.assertEquals(json_data['description'], 'argument \'d\' should be \'true\' or \'false\'')
		
	def test_soundcloud_no_arg(self):
		response = self.test_app.get('/api/search/soundcloud')
		json_data = json.loads(response.data)
		self.assertEquals(response.status, '201 CREATED')
		self.assertEquals(json_data['status'], 'failure')
		self.assertEquals(json_data['description'], 'missing argument \'q\'')
		
	def test_soundcloud_normal(self):
		response = self.test_app.get('/api/search/soundcloud', query_string='q=ylvis+fox')
		json_data = json.loads(response.data)
		self.assertEquals(response.status, '201 CREATED')
		self.assertEquals(json_data['status'], 'success')
		self.assertIsNotNone(json_data['items'])
		
	def test_soundcloud_invalid_arg(self):
		response = self.test_app.get('/api/search/soundcloud', query_string='q=ylvis+fox&debug=1234')
		json_data = json.loads(response.data)
		self.assertEquals(response.status, '201 CREATED')
		self.assertEquals(json_data['status'], 'failure')
		self.assertEquals(json_data['description'], 'argument \'d\' should be \'true\' or \'false\'')
		
if __name__ == '__main__':
	unittest.main()
	