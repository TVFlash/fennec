# Fennec RESTful server

##Install
You should have Python 2.7.X installed (All Mac OS X machines and some Linux machines comes with this pre-installed)
The flask framework can be installed through Python Package Manager using ```pip install flask; pip install flask-cors```
The requests framework can be installed through Python Package Manager using ```pip install requests```. The web socket server can be installed with ```pip install websocket-server```

##Running
Start the server with ```python server.py```
The server will now be bound to port 2000 on your localhost

##Default Pages
The default pages that exist are accessed at '/' and '/api'. The first is a test landing page and the second is the subdirectory of all endpoints

##Usage
TODO

##Example
To send a move request through your browser ``` curl -i -H "Content-Type: application/json" -X POST -d '{"id":"2","uri":"https://www.youtube.com/watch?v=IuysY1BekOE","thumbnail":"https://i.ytimg.com/vi/IuysY1BekOE/mqdefault.jpg","length":"0:05","addedBy":"Tim"}' http://localhost:2000/api/1/add```

##Server
###Create a station

Endpoint: /api/create

Request Type: POST

Description: Creates a station by going through the current 100 stations. The server would activate a station if it is not currently in use and return its id.

Example Request - HTTP Body Data: 
```
{
	"name": "Mitch\'s Station",
	"color": "FFFFFF",
}
```
> It is optional to post the JSON object. If it is not found in the HTTP Body, then the server defaults the station id as the name & "FFFFFF" as the color.

###Update a station

Endpoint: /api/update/<int:stationid>

Request Type: POST

Description: Updates the name ***and/or*** the color of a station

Example Request - HTTP Body Data: 
```
{
	"name": "Mitch\'s Station",
	"color": "FFFFFF",
}
```

###Add media to a station

Endpoint: /api/(int:stationid)/add

Request Type: POST

Description: Adds the given media specified in the HTTP Body to the station's queue.

Example Request - HTTP Body Data: 
```
{
	"id": 0,
	"uri": "testuri",
	"thumbnail": "testtn",
	"length": "testl",
	"addedBy": "testab"
}
```

###Gets the next media in a station

Endpoint: /api/(int:stationid)/(int:mediaid)/next

Description: Retrieves the media after the given media id, from the station's queue.

Request Type: GET

###List all media in a station

Endpoint: /api/(int:stationid)

Description: Returns a list of mediaObject from the station's queue

Request Type: GET

###Remove media from a station

Endpoint: /api/(int:stationid)/(int:mediaid)/remove

Description: The server will try to remove the media, specified by the media id, from the station's queue if found.

Request Type: GET

###Destroy a station

Endpoint: /api/(int:stationid)/destroy

Description: The station with that given station id will be destroyed. Basically, the server will deactivate it and clear its queue.

Request Type: GET


##Scraper
###YouTube

Endpoint: /api/search/youtube

Request Type: GET

Parameters:`

| Key | Value                                                                      |
|-----|----------------------------------------------------------------------------|
| q   | Required. The search string.                                               |
| debug | Optional. Debug mode: 'true' or 'false'. If true, it will print the original content from YouTube Data API, instead of the cleaned up version from the scraper. If not set, the default is false. |

Response:

| Key         | Value                                                      |
|-------------|------------------------------------------------------------|
| status      | 'success' or 'failure'                                     |
| description | When status is failure, it will include the error.         |
| items       | When status is success, it will include an array of media. |

###SoundCloud

Endpoint: /api/search/soundcloud

Request Type: GET

Parameters:

| Key | Value                                                                      |
|-----|----------------------------------------------------------------------------|
| q   | Required. The search string.                                               |
| debug | Optional. Debug mode: 'true' or 'false'. If true, it will print the original content from SoundCloud Web API, instead of the cleaned up version from the scraper. If not set, the default is false. |

Response:

| Key         | Value                                                      |
|-------------|------------------------------------------------------------|
| status      | 'success' or 'failure'                                     |
| description | When status is failure, it will include the error.         |
| items       | When status is success, it will include an array of media. |
