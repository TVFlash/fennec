from websocket import create_connection #imports module allowing connection to IRC
import threading #imports module allowing timing functions
import random
import datetime
import urllib
import requests
import urllib2
import time
import Queue
import imaplib
import time
import json

from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE,SIG_DFL) 

server_ip = "ws://localhost:5000"
server_port =  5000
channel = '1'


def connect(): #returns a socket connection
	#irc = websocket.WebSocket()
	irc = create_connection(server_ip) #connects to the server
        joined = {}
        joined['type'] = 'join'
        joined['stationid'] = 1
        irc.send(json.dumps(joined))
	return irc

def message(msg): #function for sending messages to the IRC chat
	try:
		if len(msg) > 0:
                    serialized = {}
                    serialized['type'] = 'send'
                    serialized['stationid'] = 1 
                    serialized['message'] = msg
                    json_data = json.dumps(serialized)
                    print 'sending ' + json_data + '*'
                    irc.send(json_data)
	except TypeError:
		print 'nothing here'


keep_trying = True #always stays True
uservotes = {}
if __name__ == '__main__':
    while keep_trying:
            print 'CONNECTING'
            irc = connect()
            while True: #double while loop here ensures we always maintain a connection
                    data = irc.recv() #gets output from IRC server
                    jdata = json.loads(data)
                    inline = jdata['message']
                    parts = inline.split(' ')
                    if inline == '!song':
                        message('Darude - Sandstorm')
                    if parts[0] == 'hello':
                        message('howdy')





