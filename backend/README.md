# Fennec RESTful server

##Install
You should have Python 2.7.X installed (All Mac OS X machines and some Linux machines comes with this pre-installed)
The flask framework can be installed through Python Package Manager using ```pip install flask; pip install flask-cors```

##Running 
Start the server with ```python server.py```
The server will now be bound to port 5000 on your localhost

##Default Pages
The default pages that exist are accessed at '/' and '/api'. The first is a test landing page and the second is the subdirectory of all endpoints

##Usage
TODO
##Example 
To send a move request through your browser ```curl -i -H "Content-Type: application/json" -X POST -d '{"uri":"https://www.youtube.com/watch?v=IuysY1BekOE"}' http://localhost:5000/api/1/remove```

