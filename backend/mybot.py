import socket #imports module allowing connection to IRC
import threading #imports module allowing timing functions
import random
import datetime
import urllib
import requests
import urllib2
import time
import Queue
import imaplib
from command import *
from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE,SIG_DFL) 

server_ip = 'SERVERIP'
server_port =  'SERVERPORT'
channel = '#test'


def connect(): #returns a socket connection
	irc = socket.socket()
	irc.connect((server_ip, server_port)) #connects to the server
	#irc.send('PASS ' + ds.password + '\r\n')
	#irc.send('USER ' + ds.nick + ' 0 * :' + ds.bot_owner + '\r\n')
	#irc.send('NICK ' + ds.nick + '\r\n')
	#irc.send('JOIN ' + ds.channel + '\r\n')
	return irc

def message(msg): #function for sending messages to the IRC chat
	try:
		if len(msg) > 0:
			irc.send('PRIVMSG ' + channel + ' :' + msg + '\r\n')
	except TypeError:
		print 'nothing here'

keep_trying = True #always stays True
while keep_trying:
	print 'CONNECTING'
	irc = connect()
	while True: #double while loop here ensures we always maintain a connection
		data = irc.recv(4096) #gets output from IRC server
		print data
	#	if len(data) == 0:
	#		break
	#	else:
	#		messagelines = []
	#		linecount = data.count('\r\n')
	#		if linecount == 1:
	#			messagelines.append(data.replace('\r\n', ''))
	#		if linecount > 1:
	#			messagelines = data.split('\r\n', linecount - 1)
	#			messagelines[linecount - 1].replace('\r\n', '')
	#			messagelines[linecount - 1].replace('\n', '')
	#		for temp in messagelines:
	#			inline = temp
	#			inline.replace('\n', '')
	##			inline.replace('\r', '')


#				if len(array) < 3:
#					continue
#				inline = array[2] 
#				inline = inline.replace('\n', ' ')
#				inline = inline.strip()
#				now = time.time()
#				stamp = time.strftime("%c")
#				user = ''
#				try:
#					user = data.split(':')[1]
#					user = user.split('!')[0] #determines the sender of the messages
#				except IndexError:
#					print 'index error avoided'
#					continue

