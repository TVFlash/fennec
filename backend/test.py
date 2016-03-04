import unittest
import json
from server import app


#====================================================================================
#MARK: Server
#====================================================================================

class ServerTestCase(unittest.TestCase):
	
	def setUp(self):
		app.config['TESTING'] = True
		app.config['LIVESERVER_PORT'] = 2000
		self.test_app = app.test_client()
		
	def test_create_destroy_station(self):
		# Test adding stations over the max limit
		for i in range(101):
			json_data = json.loads(self.test_app.post('/api/create').data)
			if i < 100:
				self.assertEquals(json_data['stationId'], i)
			else:
				self.assertIsNotNone(json_data['err'])
		# Test destroying all the station
		for i in range(100):
			self.test_app.get('/api/' + str(i) + '/destroy')
		# Test creating single station
		self.assertEquals(json.loads(self.test_app.post('/api/create').data)['stationId'], 0)
		
	def test_update_station(self):
		self.assertIsNotNone(json.loads(self.test_app.post('/api/update/0', data=json.dumps(dict(
			name = 'station_0',
			color = '000000'
		)), content_type = 'application/json').data)['result'])
		station = json.loads(self.test_app.get('/api/0').data)
		self.assertEquals(station['name'], 'station_0')
		self.assertEquals(station['color'], '000000')
				
	def test_media(self):
		# Add - Test the obvious error cases
		self.assertIsNotNone(json.loads(self.test_app.post('/api/100/add').data)['err'])
		# Add - Test adding media
		self.assertIsNotNone(json.loads(self.test_app.post('/api/0/add', data=json.dumps(dict(
			id = 0, uri = 'https://www.youtube.com/watch/?v=TMB6-YflpA4',
			thumbnail = 'thumbnail_url_0', length = 300, addedBy ='George'
		)), content_type = 'application/json').data)['result'])
		self.assertIsNotNone(json.loads(self.test_app.post('/api/0/add', data=json.dumps(dict(
			id = 1, uri = 'https://soundcloud.com/trishanicolezara/sugar-maroon-5',
			thumbnail = 'thumbnail_url_1', length = 200, addedBy ='Tim'
		)), content_type = 'application/json').data)['result'])
		# Next - Test the error cases
		self.assertIsNotNone(json.loads(self.test_app.get('/api/100/0/next').data)['err'])
		self.assertIsNotNone(json.loads(self.test_app.get('/api/0/100/next').data)['err'])
		self.assertIsNotNone(json.loads(self.test_app.get('/api/0/1/next').data)['err'])
		# Next - Test next media
		self.assertEquals(json.loads(self.test_app.get('/api/0/0/next').data)['id'], 1)
		# All - Make sure both media are still in queue
		json_data = json.loads(self.test_app.get('/api/0').data)
		queue = json_data['queue']
		self.assertEquals(len(queue), 2)
		self.assertEquals(queue[0]['id'], 0)
		self.assertEquals(queue[0]['type'], 'YouTube')
		self.assertEquals(queue[1]['id'], 1)
		self.assertEquals(queue[1]['type'], 'SoundCloud')
		# Remove - Test removal of first media
		self.assertIsNotNone(json.loads(self.test_app.get('/api/0/0/remove').data)['status'])
		# Remove - Make sure removal is successful
		json_data = json.loads(self.test_app.get('/api/0').data)
		queue = json_data['queue']
		self.assertEquals(len(queue), 1)
		self.assertEquals(queue[0]['id'], 1)


#====================================================================================
#MARK: Crawler
#====================================================================================

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
		

#====================================================================================
#MARK: Main
#====================================================================================

if __name__ == '__main__':
	unittest.main()
	