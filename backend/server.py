from flask import Flask, jsonify, request, url_for

app = Flask(__name__)

@app.route('/')
def index():
	return "Please use /api/"

@app.route('/api/<int:stationid>/next', methods=['GET'])
def nextMedia(stationid):
	media = {
		'id' : '1',
		'uri': 'https://www.youtube.com/watch?v=IuysY1BekOE',
		'addedBy': 'Tim'
	}
	return jsonify(media),201


if __name__ == '__main__':
	app.run(debug=True)
