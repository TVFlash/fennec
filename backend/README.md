# Fennec RESTful server

##Install
You should have Python 2.7.X installed (All Mac OS X machines and some Linux machines comes with this pre-installed)
The flask framework can be installed through Python Package Manager using ```pip install flask; pip install flask-cors```
The requests framework can be installed through Python Package Manager using ```pip install requests```. The web socket server can be installed with ```pip install websocket-server```

##Running
Start the server with ```python server.py```
The server will now be bound to port 5000 on your localhost

##Default Pages
The default pages that exist are accessed at '/' and '/api'. The first is a test landing page and the second is the subdirectory of all endpoints

##Usage
TODO

##Example
To send a move request through your browser ```curl -i -H "Content-Type: application/json" -X POST -d '{"uri":"https://www.youtube.com/watch?v=IuysY1BekOE"}' http://localhost:5000/api/1/remove```

##Scraper
###YouTube

Endpoint: /api/search/youtube

Request Type: GET

Parameters:

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
