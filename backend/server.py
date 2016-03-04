from flask import Flask, jsonify, request, url_for
from websocket_server import WebsocketServer
import requests
import json

app = Flask(__name__)


#====================================================================================
#MARK: Classes
#====================================================================================

class mediaObject:
	def __init__(self):
		self.jsondata = {}  # JSON representation of a media

class stationObject:
	def __init__(self):
		self.id = -1         # -1 -> Inactive | 0+ -> Active
		self.queue = []      # Holding a list of mediaObject


#====================================================================================
#MARK: Constants
#====================================================================================

MAX_NUM_STATIONS = 100
stationList = [stationObject() for i in range(MAX_NUM_STATIONS)]
		

#====================================================================================
#MARK: Server Web API
#====================================================================================

@app.route('/')
def index():
	return "Please use /api/"

@app.route('/api/create', methods=['POST'])
def addStation():
	stationId = -1
	for i in range(len(stationList)):
	    if stationList[i].id == -1:
	        stationList[i].id = stationId = i
	        break
	if stationId == -1:
		return jsonify({'err': 'All stations are currently active'}), 201
	return jsonify({'stationId': stationId}), 201


@app.route('/api/<int:stationid>/add', methods=['POST'])
def addMedia(stationid):
	if stationid < 0  or stationid > 99:
		return jsonify({'err': 'Please enter a station number between 0 and 99'}), 201
	if stationList[stationid].id == -1:
		return jsonify({'err': 'Station inactive'}), 201
	if not request.json:
		return jsonify({'err': 'Not JSON type'}), 201
	media = mediaObject()
	media.jsondata = {
		'id' : request.json['id'],
		'uri': request.json['uri'],
		'thumbnail': request.json['thumbnail'],
		'length': request.json['length'],
		'addedBy': request.json['addedBy']
	}
	stationList[stationid].queue.append(media)
	return jsonify({'result': 'Media added'}), 201

@app.route('/api/<int:stationid>/<int:mediaid>/next', methods=['GET'])
def nextMedia(stationid, mediaid):
	if stationid < 0  or stationid > 99:
		return jsonify({'err':'Please enter a station number between 0 and 99'}), 201
	if stationList[stationid].id == -1:
		return jsonify({'err': 'Station inactive'}), 201
	index = next((i for i, item in enumerate(stationList[stationid].queue) if item.jsondata['id'] == mediaid), -1)
	if index == -1:
		return jsonify({'err': 'media with given id not found'}), 201
	if index + 1 >= len(stationList[stationid].queue):
		return jsonify({'err': 'no next media in queue'}), 201
	return jsonify(stationList[stationid].queue[index + 1].jsondata), 201

@app.route('/api/<int:stationid>', methods=['GET'])
def allMedia(stationid):
	if stationid < 0  or stationid > 99:
		return jsonify({'err':'Please enter a station number between 0 and 99'}), 201
	if stationList[stationid].id == -1:
		return jsonify({'err': 'Station inactive'}), 201
	return json.dumps([mediaItem.jsondata for index, mediaItem in enumerate(stationList[stationid].queue)]), 201

@app.route('/api/<int:stationid>/<int:mediaid>/remove', methods=['GET'])
def removeMedia(stationid, mediaid):
	if stationid < 0  or stationid > 99:
		return jsonify({'err':'Please enter a station number between 0 and 99'}), 201
	if stationList[stationid].id == -1:
		return jsonify({'err': 'Station inactive'}), 201
	for index, mediaItem in enumerate(stationList[stationid].queue):
		if mediaItem.jsondata['id'] == mediaid:
			stationList[stationid].queue.remove(mediaItem)
	return jsonify({'status':'success'}), 201

@app.route('/api/<int:stationid>/destroy', methods=['GET'])
def destroyStation(stationid):
	if stationid < 0  or stationid > 99:
		return jsonify({'err':'Please enter a station number between 0 and 99'}), 201
	if stationList[stationid].id == -1:
		return jsonify({'err': 'Station inactive'}), 201
	station = stationList[stationid]
	station.id = -1
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
	d = request.args.get('debug')
	if d and d != 'true' and d != 'false':
		return jsonify({'status':'failure', 'description':'argument \'d\' should be \'true\' or \'false\''}), 201
	if not d or d == 'false':
		for item in items:
			for key, value in item['snippet'].items():
				item[key] = value
			item['videoId'] = item['id']['videoId']
			if item['thumbnails']['high']:
				item['thumbnailUrl'] = item['thumbnails']['high']['url']
			elif item['thumbnails']['medium']:
				item['thumbnailUrl'] = item['thumbnails']['medium']['url']
			else:
				item['thumbnailUrl'] = item['thumbnails']['default']['url']
			item['videoUrl'] = 'https://www.youtube.com/watch?v=' + item['videoId']
			del item['etag'], item['kind'], item['id'], item['snippet'], item['channelId'], item['liveBroadcastContent'], item['thumbnails']
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

if __name__ == '__main__':
	app.run(port=2000,debug=True)

#End of Chat websocket implementation
