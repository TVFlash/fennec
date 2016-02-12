import poem
import datetime
import time
import urllib2
import unicodedata
import json
import mechanize
import xlrd
import sqlite3
from jeopardy import *
import sys
import traceback
import os
import shutil
import utility
from selenium import webdriver
from pyvirtualdisplay import Display

def monkeypatch_mechanize():
    """Work-around for a mechanize 0.2.5 bug. See: https://github.com/jjlee/mechanize/pull/58"""
    import mechanize
    if mechanize.__version__ < (0, 2, 6):
        from mechanize._form import SubmitControl, ScalarControl

        def __init__(self, type, name, attrs, index=None):
            ScalarControl.__init__(self, type, name, attrs, index)
            # IE5 defaults SUBMIT value to "Submit Query"; Firebird 0.6 leaves it
            # blank, Konqueror 3.1 defaults to "Submit".  HTML spec. doesn't seem
            # to define this.
            if self.value is None:
                if self.disabled:
                    self.disabled = False
                    self.value = ""
                    self.disabled = True
                else:
                    self.value = ""
            self.readonly = True

        SubmitControl.__init__ = __init__
	print 'done with monkeypatch'



class DataStorage:

	def __init__(self):
		#monkeypatch_mechanize()
		self.queueing = False	
		self.templines = {}
		self.question = ''
		self.cards = []
		self.difference = 0 
		self.dfact = False
		self.queue = 0
		self.target = 0
		self.streamon = False
		self.targetcounter = 0
		self.targetphrase = ''
		self.streamer = sys.argv[1]
		self.messagebody = ''
		self.messagesubject = ''
		self.plugbrowser = None
		f = None
		if os.path.isfile('streamdata/' + self.streamer + '/' + self.streamer + 'config.txt'):
			f = open('streamdata/' + self.streamer + '/' + self.streamer +  'config.txt', 'r')
		else:
			f = open('trox94config.txt', 'r')
		self.userlog = f.readline().split(':')[1].replace('\n', '')
		self.userpw = f.readline().split(':')[1].replace('\n', '')
		self.bot_owner = f.readline().split(':')[1].replace('\n', '')
		self.nick = f.readline().split(':')[1].replace('\n', '')
		self.channel = '#' + self.streamer
		self.server = f.readline().split(':')[1].replace('\n', '')
		self.password = f.readline().replace('\n', '')
		self.emailuser = f.readline().split(':')[1].replace('\n', '')
		self.emailpw = f.readline().split(':')[1].replace('\n', '')
		self.emailreceive = f.readline().split(':')[1].replace('\n', '')
		self.pluguser = f.readline().split(':')[1].replace('\n', '')
		self.plugpw = f.readline().split(':')[1].replace('\n', '')
		self.c_k = f.readline().split(':')[1].replace('\n', '')
		self.c_s = f.readline().split(':')[1].replace('\n', '')
		self.a_t = f.readline().split(':')[1].replace('\n', '')
		self.a_s = f.readline().split(':')[1].replace('\n', '')
		self.client_id = f.readline().split(':')[1].replace('\n', '')
		self.client_secret = f.readline().split(':')[1].replace('\n', '')
		self.access_token = f.readline().split(':')[1].replace('\n', '')
		self.refresh_token = f.readline().split(':')[1].replace('\n', '')
		self.plugdj = f.readline().split(':')[1].replace('\n', '')
		self.messagesubject = f.readline().split(':')[1].replace('\n', '')
		self.messagebody = f.readline().split(':', 1)[1].replace('\n', '')
		self.ircstart = f.readline().split(':')[1].replace('\n', '')
		self.tweetchecks = f.readline().split(':', 1)[1].split(' ')
		self.facelog = f.readline().split(':')[1].replace('\n', '')
		self.facepw = f.readline().split(':')[1].replace('\n', '')
		f.close()
		self.messagesubject = unicode(self.messagesubject.decode("utf-8"))
		self.messagebody = unicode(self.messagebody.decode("utf-8"))
		self.messagearray = self.messagebody.split('::') 
		self.remindtime = None
		f = open('subscribestream.txt', 'r')
		self.subscribestreamers = []
		for line in f:
			self.subscribestreamers.append(line.replace('\n', ''))
		self.browser = None
		if self.streamer in self.subscribestreamers:
			#self.browser = webdriver.Firefox()
			self.browser = webdriver.PhantomJS('phantomjs')
			self.browser.get("https://www.facebook.com")
			time.sleep(3)
			elem = self.browser.find_element_by_xpath('//*[@id="email"]')
			elem.send_keys(self.facelog)
			elem = self.browser.find_element_by_xpath('//*[@id="pass"]')
			elem.send_keys(self.facepw)
			elem = self.browser.find_element_by_xpath('//*[@id="loginbutton"]')
			elem.click()
			self.browser.get("http://www.twitch.tv")
			elem = self.browser.find_element_by_xpath('//*[@id="header_login"]')
			elem.click()
			time.sleep(1)
			elem = self.browser.find_element_by_xpath('//*[@id="login_subwindow"]/div[1]/div/div/div[1]/div/a')
			elem.click()
			r = open(self.streamer + 'pid.txt', 'a')
			r.write('\n' + str(self.browser.service.process.pid))
		self.factlist = []
		f = open('deerfacts.txt', 'r')
		for l in f:
			self.factlist.append(l.replace('\n', ''))
		self.troxon = True
		print 'streamer is *' + self.streamer + '**'
		self.lastemail = time.time()
		cont = urllib2.urlopen("https://api.twitch.tv/kraken/users/" + self.streamer)
		dat = json.loads(cont.read())
		self.hostlink = "http://tmi.twitch.tv/hosts?include_logins=1&host=" + str(dat['_id'])
		self.poems = {}
		print len(self.poems)
		poem.loadDic(self.poems)
		print len(self.poems)
		self.seen = {} #will contain the time stamp of when someone was last seen
		self.said = {} #will contain the message they said
		self.startTime = datetime.datetime.now()
		self.lastchecked = time.time() #used to track how long someone has been in the channel
		self.lastwritten = time.time()
		self.lastonline = time.time()
		self.kappatimes = []
		self.kappanames = []
		self.quotes = []
		self.poemsubs = []
		#self.poemday = False
		f = open('kappa.txt', 'r')
		self.highestKappa = int(f.readline())
		self.ignore = []
		f = open('blacklist.txt', 'r')
		for line in f:
			self.ignore.append(line.replace('\n', ''))
		self.mods = []
		self.modlist = []
		self.viewers = {}
		m = open('mods.txt', 'r')
		for mod in m:
			addedmod = mod.replace('\n', '')
			self.modlist.append(addedmod)
		self.subs = []
		self.plugs = {}
		su = open('tempsubs.txt', 'r')
		for s in su:
			addedsub = s.replace('\n', '')
			self.subs.append(addedsub) #build list of subscriber names
		su.close()
	
		q = open('quotes.txt', 'r')
		for quo in q:
			toadd = quo.replace('\n', '')
			self.quotes.append(toadd)
		q.close()

		plu = open('plugs.txt', 'r') #build hashmap of twitch username -> plugdj username
		for pl in plu:
			twitch = pl.split(':')[0]
			plugdj = pl.split(':')[1].replace('\n', '')
			self.plugs[twitch] = plugdj
		plu.close()

		self.points = {}
		f = open('points.txt', 'r')	
		for li in f:
			twitch = li.split(':')[0]
			pt = int(li.split(':')[1].replace('\n', ''))
			self.points[twitch] = pt

		p = os.getpid()
		f = open(self.streamer + "pid.txt", 'w')
		f.write(str(p))
		f.close()


		self.linestyped = {}
		self.secret = ''
		self.troxuser = ''
		self.troxmessage = ''
		self.ingame = False
		self.lastgame = time.time()
		self.currentsubs = []
		self.watchingfor = ''
		self.lines = {}
		self.queued = []
		if not os.path.isdir('streamdata/' + self.streamer):
			os.makedirs('streamdata/' + self.streamer)
			shutil.copy('streamdata/database.db', 'streamdata/' + self.streamer)

		self.conn = sqlite3.connect('streamdata/' + self.streamer + '/database.db', check_same_thread=False) 
		self.commands = {} #commands will only contain commands that are simple call and response with no variation
		self.functions = {}
		self.cooldowns = {}
		f = open('streamdata/' + self.streamer + '/' + self.streamer + 'commands.txt', 'r')
		for com in f:
			if com[0] == ':':
				self.functions[com.split(':')[1].replace('\n', '')] = getattr(utility, com.split('!')[1].replace('\n', ''))
				self.cooldowns[com.split(':')[1].replace('\n', '')] = time.time()	
			else:
				key = com.split(':', 1)[0]
				val = com.split(':', 1)[1].replace('\n', '')
				self.commands[key] = val
				self.cooldowns[key] = time.time()

		for re in self.cooldowns:
			print re, self.cooldowns[re]

		############ START OF JEOPARDY GAME #################
		
		self.book = xlrd.open_workbook('HearthstoneCardList.xlsx')

		self.cardlist = []
		self.lookup = {0: 'class', 1: 'rarity', 2: 'cardtype', 3: 'mana', 4: 'attack', 5: 'health', 6: 'text'} 
		self.first_sheet = self.book.sheet_by_index(0)
		for i in range(1, 567):
			row = self.first_sheet.row_values(i)
			card = Card(row)
			self.cardlist.append(card)

		############   END OF JEOPARDY GAME #############
	def checkusers(self): #looks at twitch api to see people in chat
		try:
			tempmap = self.lines.copy() 
			self.lines = {}
			tempconn = sqlite3.connect('streamdata/' + self.streamer + '/database.db', check_same_thread=False) 
			check = 0
			start = time.time()
			url = 'https://tmi.twitch.tv/group/user/' + self.streamer + '/chatters'
			contents = urllib2.urlopen(url)
			data = json.loads(contents.read())
			self.troxon = False
			newlist = []
			for thing in data['chatters']['moderators']:
				actual = unicodedata.normalize('NFKD', thing).encode('ascii','ignore')
				newlist.append(actual)
			for thing in data['chatters']['staff']:
				actual = unicodedata.normalize('NFKD', thing).encode('ascii','ignore')
				newlist.append(actual)
			self.mods = newlist
			end = time.time()
			#print 'init takes ' + str(end - start)
			#if self.streamer == 'deernadia':
			try:
				sum = 0.0 
				for group in data['chatters']:
					for member in data['chatters'][group]:
						start = time.time()
						actual = unicodedata.normalize('NFKD', member).encode('ascii','ignore')
						end = time.time()
						tot = end - start
						sum += tot
						if len(self.watchingfor) > 0:
							if actual == self.watchingfor:
								check = 1
						with tempconn:
							c = tempconn.cursor()
							c.execute("SELECT * FROM Users Where name = ?", (actual,))
							r = c.fetchone()
							if r is None:
								c.execute("INSERT INTO Users Values(?, ?, ?)", (actual, 0, self.difference))
							else:
								c.execute("UPDATE Users SET time = time + ? WHERE name = ?", (self.difference, actual))
			#	print 'check took ' + str(sum) + ' seconds'
			except:
				print 'failed update'

			#print str(time.time() - end)
			start = time.time()
			#print len(tempmap)
			try:
				for key in tempmap:
				#	print key, tempmap[key]
					with tempconn:
						c = tempconn.cursor()
						c.execute("SELECT * FROM Users Where name = ?", (key,))
						r = c.fetchone()
						if r is None:
							#print '' 
							continue
						else:
							c.execute("UPDATE Users SET lines = lines + ? WHERE name = ?", (tempmap[key], key))
				end = time.time()
			#	print 'line update took ' + str(end - start)
			except:
				print 'failed line update'
			return check 
		except:
			return ''


	def convertSeconds(self, sec):
		d = datetime.datetime(1,1,1) + datetime.timedelta(seconds = sec)
		return ("%d days, %d hours, %d minutes, %d seconds" % (d.day-1, d.hour, d.minute, d.second))

	def datetimetostring(self, datetime):
		print datetime
		string = str(datetime)
		period = string.index('.')
		string = string[0:period]
		if string.find(',') != -1:
			ind = string.index(',') + 1
			string = string[ind:len(string)]
		return string
