from flask import Flask, jsonify, request, url_for, send_from_directory, render_template
from websocket_server import WebsocketServer
import requests
import json
import isodate
import threading
import sys

app = Flask(__name__)


#====================================================================================
#MARK: Classes
#====================================================================================

class mediaObject:
	def __init__(self):
		self.id = '-1'                # Unique Id of the media object
		self.uri = ''                 # Url to the media
		self.thumbnail = ''           # Url to the thumbnail image
		self.length = 0               # Length of media in seconds
		self.title = ''               # Title of the media item
		self.addedBy = ''             # Name of the publisher
		self.type = ''                # YouTube or SoundCloud

class stationObject:
	def __init__(self):
		self.id = -1                  # -1 -> Inactive | 0+ -> Active
		self.name = ''                # Station name
		self.color = ''               # Station color
		self.media_elapsed_time = -1  # Elapsed time of current media in seconds
		self.clients = []             # List of websocket clients
		self.queue = []               # Holding a list of mediaObject
		
		
#====================================================================================
#MARK: Encoder
#====================================================================================

def encode_object(obj):
	if isinstance(obj, stationObject):
		return obj.__dict__
	if isinstance(obj, mediaObject):
		return obj.__dict__
	return obj


#====================================================================================
#MARK: Global variables
#====================================================================================

MAX_NUM_STATIONS = 100
stationList = [stationObject() for i in range(MAX_NUM_STATIONS)]
		

#====================================================================================
#MARK: Server Web API
#====================================================================================

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/api/create', methods=['POST'])
def addStation():
	stationId = -1
	for i in range(len(stationList)):
		if stationList[i].id == -1:
			stationList[i].id = stationId = i
			stationList[i].name = str(i)
			stationList[i].color = 'FFFFFF'
			if request.json:
				if request.json['name']:
					stationList[i].name = request.json['name']
				if request.json['color']:
					stationList[i].color = request.json['color']
			break
	if stationId == -1:
		return jsonify({'err': 'All stations are currently active'}), 201
	return jsonify({'stationId': stationId}), 201
	
@app.route('/api/update/<int:stationid>', methods=['POST'])
def updateStation(stationid):
	if stationid < 0  or stationid > 99:
		return jsonify({'err': 'Please enter a station number between 0 and 99'}), 201
	if stationList[stationid].id == -1:
		return jsonify({'err': 'Station inactive'}), 201
	if not request.json:
		return jsonify({'err': 'Not JSON type'}), 201
	if request.json['name']:
		stationList[stationid].name = request.json['name']
	if request.json['color']:
		stationList[stationid].color = request.json['color']
	return jsonify({'result': 'Station updated'})

@app.route('/api/stations', methods=['GET'])
def allStations():
	activeStationList = []
	for station in stationList:
		if station.id != -1:
			activeStationList.append(station)
	return json.dumps(activeStationList, default=encode_object), 201

@app.route('/api/<int:stationid>/add', methods=['POST'])
def addMedia(stationid):
	if stationid < 0  or stationid > 99:
		return jsonify({'err': 'Please enter a station number between 0 and 99'}), 201
	if stationList[stationid].id == -1:
		return jsonify({'err': 'Station inactive'}), 201
	if not request.json:
		return jsonify({'err': 'Not JSON type'}), 201
	media = mediaObject()
	media.id = str(request.json['id'])
	media.uri = request.json['uri']
	media.title = request.json['title']
	media.thumbnail = request.json['thumbnail']
	media.length = request.json['length']
	media.addedBy = request.json['addedBy']
	media.type = 'YouTube' if 'youtube' in request.json['uri'] else 'SoundCloud'
	stationList[stationid].queue.append(media)
	if len(stationList[stationid].queue) == 1:
		stationList[stationid].media_elapsed_time = 0
	return jsonify({'result': 'Media added'}), 201

@app.route('/api/<int:stationid>/<string:mediaid>/next', methods=['GET'])
def nextMedia(stationid, mediaid):
	if stationid < 0  or stationid > 99:
		return jsonify({'err':'Please enter a station number between 0 and 99'}), 201
	if stationList[stationid].id == -1:
		return jsonify({'err': 'Station inactive'}), 201
	index = next((i for i, item in enumerate(stationList[stationid].queue) if item.id == mediaid), -1)
	if index == -1:
		return jsonify({'err': 'media with given id not found'}), 201
	if index + 1 >= len(stationList[stationid].queue):
		return jsonify({'err': 'no next media in queue'}), 201
	return json.dumps(stationList[stationid].queue[index + 1], default=encode_object), 201

@app.route('/api/<int:stationid>', methods=['GET'])
def allMedia(stationid):
	if stationid < 0  or stationid > 99:
		return jsonify({'err':'Please enter a station number between 0 and 99'}), 201
	if stationList[stationid].id == -1:
		return jsonify({'err': 'Station inactive'}), 201
	return json.dumps(stationList[stationid], default=encode_object), 201

@app.route('/api/<int:stationid>/<string:mediaid>/remove', methods=['GET'])
def removeMedia(stationid, mediaid):
	if stationid < 0  or stationid > 99:
		return jsonify({'err':'Please enter a station number between 0 and 99'}), 201
	if stationList[stationid].id == -1:
		return jsonify({'err': 'Station inactive'}), 201
	for index, mediaItem in enumerate(stationList[stationid].queue):
		if mediaItem.id == mediaid:
			stationList[stationid].queue.remove(mediaItem)
			if index == 0:
				stationList[stationid].media_elapsed_time = 0
	return jsonify({'status':'success'}), 201

@app.route('/api/<int:stationid>/destroy', methods=['GET'])
def destroyStation(stationid):
	if stationid < 0  or stationid > 99:
		return jsonify({'err':'Please enter a station number between 0 and 99'}), 201
	if stationList[stationid].id == -1:
		return jsonify({'err': 'Station inactive'}), 201
	station = stationList[stationid]
	station.id = -1
	station.name = ''
	station.color = ''
	station.media_elapsed_time = -1
	del station.clients[:]
	del station.queue[:]
	return jsonify({'status':'success'}), 201
	

#====================================================================================
#MARK: YT + SC Crawler Web API
#====================================================================================

@app.route('/api/search/youtube', methods=['GET'])
#Crawl YouTube
def searchYouTube():
	q = request.args.get('q')
	if not q:
		return jsonify({'status':'failure', 'description':'missing argument \'q\''}), 201
	response = requests.get('https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=10&order=relevance&q=' + q + '&type=video&videoDefinition=any&key=AIzaSyASsdIg2A2eb-W9UlfOx4sIVRLZ2y1h63c')
	json_obj = response.json()
	items = json_obj['items']
	videoIdArray = []
	d = request.args.get('debug')
	if d and d != 'true' and d != 'false':
		return jsonify({'status':'failure', 'description':'argument \'d\' should be \'true\' or \'false\''}), 201
	if not d or d == 'false':
		for item in items:
			for key, value in item['snippet'].items():
				item[key] = value
			item['videoId'] = item['id']['videoId']
			videoIdArray.append(item['videoId'])
			if item['thumbnails']['high']:
				item['thumbnail'] = item['thumbnails']['high']['url']
			elif item['thumbnails']['medium']:
				item['thumbnail'] = item['thumbnails']['medium']['url']
			else:
				item['thumbnail'] = item['thumbnails']['default']['url']
			item['videoUrl'] = 'https://www.youtube.com/watch?v=' + item['videoId']
			del item['etag'], item['kind'], item['id'], item['snippet'], item['channelId'], item['liveBroadcastContent'], item['thumbnails']
	response = requests.get('https://www.googleapis.com/youtube/v3/videos?part=contentDetails&id=' + ','.join(videoIdArray) + '&key=AIzaSyASsdIg2A2eb-W9UlfOx4sIVRLZ2y1h63c')
	json_obj = response.json()
	duration_items = json_obj['items']
	if not d or d == 'false':
		for index, item in enumerate(duration_items):
			items[index]['duration'] = int(isodate.parse_duration(item['contentDetails']['duration']).total_seconds())
	return jsonify({'status':'success', 'items':items}), 201 

@app.route('/api/search/soundcloud', methods=['GET'])
#Crawl SoundCloud
def searchSoundCloud():
	q = request.args.get('q')
	if not q:
		return jsonify({'status':'failure', 'description':'missing argument \'q\''}), 201
	response = requests.get('http://api.soundcloud.com/tracks.json?client_id=87dd0b14dbc81970b9b4becdf176c498&q=' + q + '&limit=10')
	json_obj = response.json()
	d = request.args.get('debug')
	if d and d != 'true' and d != 'false':
		return jsonify({'status':'failure', 'description':'argument \'d\' should be \'true\' or \'false\''}), 201
	if not d or d == 'false':
		for item in json_obj:
			item['thumbnail'] = item['artwork_url']
			item['videoUrl'] = item['video_url']
			item['waveformUrl'] = item['waveform_url']
			item['trackUrl'] = item['permalink_url']
			item['playCount'] = item['playback_count']
			item['lastModified'] = item['last_modified']
			item['trackId'] = item['id']
			item['format'] = item['original_format']
			item['publishedAt'] = item['created_at']
			item['uploader'] = item['user']['username']
			del item['user'], item['user_favorite'], item['user_id'], item['user_playback_count'], item['video_url'], item['waveform_url'], item['state'], item['stream_url'], item['streamable'], item['tag_list'], item['track_type'], item['uri'], item['sharing'], item['reposts_count'], item['release_year'], item['release_month'], item['release_day'], item['release'], item['purchase_url'], item['purchase_title'], item['permalink'], item['permalink_url'], item['playback_count'], item['license'], item['likes_count'], item['last_modified'], item['label_name'], item['label_id'], item['kind'], item['key_signature'], item['isrc'], item['id'], item['original_format'], item['original_content_size'], item['genre'], item['favoritings_count'], item['embeddable_by'], item['downloadable'], item['download_url'], item['download_count'], item['created_at'], item['commentable'], item['comment_count'], item['bpm'], item['attachments_uri'], item['artwork_url']
	return jsonify({'status':'success', 'items':json_obj}), 201
	

#====================================================================================
#MARK: Timer
#====================================================================================
	
def timer_func():
	try:
		for station in stationList:
			if station.id == -1:
				continue
			if station.media_elapsed_time == -1:
				continue
			elif station.media_elapsed_time != -1:
				station.media_elapsed_time += 1
			if station.media_elapsed_time >= station.queue[0].length:
				station.queue.pop(0)
				if len(station.queue) > 0:
					station.media_elapsed_time = 0
				else:
					destroyStation(station.id)
	except:
		print "Unexpected error:", sys.exc_info()[0]
	finally:
		threading.Timer(1, timer_func).start()


#====================================================================================
#MARK: WebSocket functions
#====================================================================================

def client_left(client, server):
	for station in stationList:
		continue
		#if station.clients has client:
			#delete the client

def message_received(client, server, message):
	try:
		json_obj = json.loads(message)
	except ValueError:
		server.send_message(client, json.dumps({'err': 'Not JSON type'}))
	if json_obj['type'] == 'connect':
		station = stationList[json_obj['stationId']]
		if station.id == -1:
			server.send_message(client, json.dumps({'err': 'Inactive station'}))
			return
		station.clients.append(client)
		server.send_message(client, json.dumps({'res': 'Success'}))
		
	
def ws_destroyedStation():
	server.send_message_to_all(json.dumps({''}))


#====================================================================================
#MARK: Main
#====================================================================================

if __name__ == '__main__':
	timer_func()
	app.run(host='0.0.0.0',port=2000,debug=True)
	server = WebsocketServer(3000, "0.0.0.0")
	server.set_fn_client_left(client_left)
	server.set_fn_message_received(message_received)
	server.run_forever()

