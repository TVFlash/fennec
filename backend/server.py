from flask import Flask, jsonify, request, url_for

app = Flask(__name__)

@app.route('/')
def index():
	return "Please use /api/"

@app.route('/api/create', methods=['POST'])
def addStation():
	#TODO: Parse JSON object, create new station and return stationid
	return 201


@app.route('/api/<int:stationid>/add', methods=['POST'])
def addMedia(stationid):
	#TODO: Parse JSON object and store in queue stationid
	return 201

@app.route('/api/<int:stationid>/next', methods=['GET'])
def nextMedia(stationid):
	media = {
		'id' : '1',
		'uri': 'https://www.youtube.com/watch?v=IuysY1BekOE',
		'thumbnail': 'https://i.ytimg.com/vi/IuysY1BekOE/mqdefault.jpg',
		'length': '0:05',
		'addedBy': 'Tim'
	}
	return jsonify(media),201

@app.route('/api/<int:stationid>', methods=['GET'])
def allMedia(stationid):
	queue = [{}]
	queue[0]['id'] = '1'
	queue[0]['uri'] = 'https://www.youtube.com/watch?v=IuysY1BekOE'
	queue[0]['thumbnail'] = 'https://i.ytimg.com/vi/IuysY1BekOE/mqdefault.jpg'
	queue[0]['length'] = '0:05'
	queue[0]['addedBy']= 'Tim'
	#TODO: Return full queue for station stationid
	return jsonify(queue[0]),201

@app.route('/api/<int:stationid>/remove', methods=['POST'])
def removeMedia(stationid):
	#TODO: Parse JSON object and remove it for the station's queue if exists
	return jsonify({'status':'success'}), 201



if __name__ == '__main__':
	app.run(debug=True)
