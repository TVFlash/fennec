import socket #imports module allowing connection to IRC
import threading #imports module allowing timing functions
import random
import kappa
import datetime
#import lastseen
import urllib
import requests
import urllib2
import time
import Queue
import imaplib
import email
from command import *
from collections import Counter
import os
import sys
import math
from datastorage import * 
import operator
#from fuzzywuzzy import fuzz
#from fuzzywuzzy import process
from pytz import timezone
import pytz
from bs4 import BeautifulSoup
import urlparse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from django.utils import encoding
import operator
from collections import OrderedDict
from collections import defaultdict
from Tkinter import Tk
import jeopardy
from jeopardy import *
import sqlite3
from utility import *
import thread
from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE,SIG_DFL) 
#import Image
#import ImageGrab
#from imgurpython import ImgurClient
import twitter
#from pahk import Interpreter

ds = DataStorage()
link = ''
remindtime = None

def parse_dictionary(filename):
   word_anagrams = defaultdict(set)
   with open(filename) as dictionary:
      for word in dictionary:
         word = word.rstrip()
         word_anagrams[''.join(sorted(word))].add(word)
   return word_anagrams

word_anagrams = parse_dictionary("cardlist.txt")

rafflesubject = ''
rafflemess = ''

api = twitter.Api(consumer_key=ds.c_k, consumer_secret=ds.c_s, access_token_key=ds.a_t, access_token_secret = ds.a_s)
tweets = {}
for tw in ds.tweetchecks:
	statuses = api.GetUserTimeline(screen_name=tw)
	for st in statuses:
		if st.in_reply_to_screen_name is None and st.retweeted_status is None:
			tweets[tw] = unicodedata.normalize('NFKD', st.text).encode('ascii','ignore')
		#	print tw, tweets[tw]
			break


def checkon(): #looks at Twitch's api to see if a stream is online
	url = 'https://api.twitch.tv/kraken/streams/' + ds.streamer
	contents = urllib2.urlopen(url)
	con = contents.read()
#	print con
	if con.find('\"stream\":null') == -1: #not the correct way of doing it with json but works for now
		return True
	else:
		return False

def connect(): #returns a socket connection
	irc = socket.socket()
	irc.connect((ds.server, 6667)) #connects to the server
	#sends variables for connection to twitch chat
	irc.send('PASS ' + ds.password + '\r\n')
	irc.send('USER ' + ds.nick + ' 0 * :' + ds.bot_owner + '\r\n')
	irc.send('NICK ' + ds.nick + '\r\n')
	irc.send('JOIN ' + ds.channel + '\r\n')
	return irc

def whisperconnect():
	irc = socket.socket()
	irc.connect(('199.9.253.119', 6667)) #connects to the server
	#sends variables for connection to twitch chat
	irc.send('PASS ' + ds.password + '\r\n')
	irc.send('USER ' + ds.nick + ' 0 * :' + ds.bot_owner + '\r\n')
	irc.send('NICK ' + ds.nick + '\r\n')
	irc.send('CAP REQ :twitch.tv/commands\r\n')
	irc.send('CAP REQ :twitch.tv/tags\r\n')
	return irc



def message(msg): #function for sending messages to the IRC chat
	try:
		if len(msg) > 0:
			if ds.queue < 6: #ensures does not send >20 msgs per 30 seconds.
				irc.send('PRIVMSG ' + ds.channel + ' :' + ds.ircstart + msg + '\r\n')
				ds.queue = ds.queue + 1
				print 'queue is now ' + str(ds.queue)
			else:
				print 'oops'
	except TypeError:
		print 'nothing here'


def messagemods(inline):
	for mod in ds.modlist:
		r = br.open("http://www.twitch.tv/message/compose")
		formcount=0
		for frm in br.forms():  
			if str(frm.attrs["id"]) == "send_message_form":
				break
			formcount=formcount+1
		br.select_form(nr=formcount)
		br.form["to_login"] = mod 
		br.form["message[subject]"] = inline.split(':', 1)[0] 
		br.form["message[body]"] = inline.split(':', 1)[1] 
		last = br.submit()

def queuetimer(): #function for resetting the queue every 30 seconds
    ds.queue = 0
    threading.Timer(30,queuetimer).start()

queuetimer()

online = False
streamstart = None
def isonline():
	response = mechanize.urlopen("http://nightdev.com/hosted/uptime.php?channel=" + ds.streamer)
	line = response.read()
	if line.find('not') != -1:
		return False
	else:
		return True		

def checkfollows(user):
	url = "https://api.twitch.tv/kraken/users/" + user + "/follows/channels/" + ds.streamer
	print '*' + url + '*'
	try:
		contents = mechanize.urlopen(url)
		return True
	except:
		return False

keep_trying = True #always stays True
lastwrite = time.time()
troxon = True
lastspam = time.time()
lastsongcheck = time.time()
tryhard = False
#lastgame = time.time()
rafflelist = []
startraffle = False
twittercheck = time.time()

ds.checkusers()
while keep_trying:
	print 'CONNECTING'
	irc = connect()
	whisperirc = whisperconnect()
	while True: #double while loop here ensures we always maintain a connection
		data = irc.recv(4096) #gets output from IRC server
		if len(data) == 0:
			break
		else:
			messagelines = []
			linecount = data.count('\r\n')
			if linecount == 1:
				messagelines.append(data.replace('\r\n', ''))
			if linecount > 1:
				messagelines = data.split('\r\n', linecount - 1)
				messagelines[linecount - 1].replace('\r\n', '')
				messagelines[linecount - 1].replace('\n', '')
			for temp in messagelines:
				inline = temp
				inline.replace('\n', '')
				inline.replace('\r', '')
				checkdif = time.time() - ds.lastchecked
				onlinedif = time.time() - ds.lastonline
				writedif = time.time() - ds.lastwritten
				spamdif = time.time() - lastspam
				twitterdif = time.time() - twittercheck
				songdif = time.time() - lastsongcheck
				if twitterdif > 30:
					twittercheck = time.time()
					try:
						for tw in tweets:
							statuses = api.GetUserTimeline(screen_name=tw)
							if statuses[0].in_reply_to_screen_name is None and statuses[0].retweeted_status is None:
								actual = unicodedata.normalize('NFKD', statuses[0].text).encode('ascii','ignore')
								if tweets[tw] != actual:
									tweets[tw] = actual
									message('New tweet from ' + tw + ' : ' + actual)
					except:
						print 'rip rate limit'
				if checkdif > 120:
					temp = time.time()
					ds.difference = checkdif
					ds.templines = ds.lines
					thread.start_new_thread(ds.checkusers, ())
					ds.lastchecked = time.time()
				if onlinedif > 30:
					try:
						if checkon() == True: 
							if ds.streamon == False:
								ds.streamon = True
								whisperirc.send('PRIVMSG ' + ds.channel + ' :/w trox94 STREAM IS ON START RECORDING\r\n')
						else:
							ds.streamon = False
					except:
						pass
					ds.lastonline = time.time()
				if spamdif > 300:
					if len(ds.poemsubs) > 0:
						ret = ''
						for name in ds.poemsubs:
							ret += (name + ' , ')
						ret += 'need poems'
						whisperirc.send('PRIVMSG ' + ds.channel + ' :/w deernadia ' + ret + '\r\n')
						lastspam = time.time()
					f = open('points.txt', 'w')
					for k in ds.points:
						f.write(k + ':' + str(ds.points[k]) + '\n')
					f.close()
				if songdif > 60:
					f = open('currsong', 'r')
					ds.currsong =  ''
					



				if ds.remindtime is not None:
					f = datetime.datetime.now()
					q = ds.remindtime - f
					if q.days == -1:
						message('@trox94 here is your reminder')	
						ds.remindtime = None
				array = inline.split(':',2)
				if len(array) < 3:
					continue
				inline = array[2] 
				inline = inline.replace('\n', ' ')
				inline = inline.strip()
				now = time.time()
				stamp = time.strftime("%c")
				user = ''
				try:
					user = data.split(':')[1]
					user = user.split('!')[0] #determines the sender of the messages
				except IndexError:
					print 'index error avoided'
					continue
				if user in ds.lines:
					if user.find('tmi.twitch.tv') == -1:
						ds.lines[user] += 1
				else:
					if user.find('tmi.twitch.tv') == -1:
						ds.lines[user] = 1
				count = inline.count('Kappa')
				if (count > 0):
					for i in range (0, count):
						ds.kappatimes.append(now)
						ds.kappanames.append(user)
				while len(ds.kappatimes) > 0 and ds.kappatimes[0] + 60 < now:
					ds.kappatimes.pop()
					ds.kappanames.pop()
				kappa.update(ds.kappatimes, ds.kappanames, ds.highestKappa, stamp)
				if inline == ds.secret and len(inline) > 1 and len(ds.secret) > 1:
					ret = user + ' said the secret ' + ds.secret
					if checkfollows(user) == True:
						ret += ' and follows the channel!'
					else:
						ret += ' but doesn\'t follow the channel nadiaSad'
						irc.send('PRIVMSG ' + ds.channel + ' :/timeout ' + user + ' 20\r\n')
						ds.queue += 1
					ds.secret = ''
					message(ret)
				if user == 'deernadia':
					ret = handleNadia(ds, inline)
					if ret == 'added a poem!':
						message(ret)
				allwords = inline.split(' ')
				if ds.streamer == 'deernadia' and 'where' in allwords and 'nadia' in allwords and ('live' in allwords or 'from' in allwords):
					message('Nadia is actually 6 inches tall and is trapped in a tiny dollyhouse in Trump\'s basement')
				args = inline.split(' ')
				command = args[0]
				if inline == ds.targetphrase and len(ds.targetphrase) > 1:
					ds.targetcounter += 1
					if ds.target == ds.targetcounter:
						ds.targetphrase = ''
						ds.targetcounter = 0
						ds.target = 0
						message(user + ' wins!')
				if (user == 'twitchnotify' or user == 'trox94') and inline.find('subscribed') != -1 and inline.find(' to ') == -1 and inline.find('away') == -1:
					ret = handleSub(ds, user, inline)
					message(ret)
				if command == '!messagemods' and user == ds.bot_owner:
					messagemods(inline.split(' ', 1)[1])
					message('Messages sent.')
				for s in ds.cards:
					if s.name.lower() == inline.lower() and ds.ingame == True and user not in ds.ignore:
						message(user + ' won!') 
						ds.ingame = False
						ds.lastgame = time.time()
						ds.cards = []
						ds.question = ''
						if user not in ds.points:
							ds.points[user] = 1
						else:
							ds.points[user] += 1
				if inline == '!points' and ds.streamer == 'deernadia' and user not in ds.ignore:
					if user in ds.points:
						message(str(ds.points[user]))
					else:
						message('0')
				if inline == '!startraffle' and user == ds.bot_owner:
					startraffle = True
					message('If you are a subscriber, type !troxraffle to enter!')
				if inline.find('!stopraffle') != -1 and user == ds.bot_owner:
					number = int(inline.split(' ')[1])
					startraffle = False
					winners = random_subset(rafflelist, number)
					rafflesubject = raw_input('Enter subject: ')
					rafflemess = raw_input('Enter message: ')
					ret = ''
					for name in rafflelist:
						print '*' + name + '*'
					for name in winners:
						ret = ret + name + ', '
						rafflemessage(name)
					ret = ret + ' all won! Check your inbox for details!'
					message(ret)
					rafflelist = []
					winners = []
				if inline == '!troxraffle' and startraffle == True and user in ds.subs:
					if user not in rafflelist:
						rafflelist.append(user)
						print 'added ' + user
				if inline.split(' ')[0] in ds.functions:
					ret = ds.functions[inline.split(' ')[0]](ds, user, inline)
					if time.time() - ds.cooldowns[inline.split(' ')[0]] > 60 or user == 'trox94' or ret == '':
						ds.cooldowns[inline.split(' ')[0]] = time.time()
						if isinstance(ret, list):
							print 'woo'
							for item in ret:
								message(item)
						else:
							message(ret)
				com = Command(command, user, inline, ds, irc)
				update(user, inline, ds.seen, ds.said)

