# -*- coding: utf-8 -*-
#!/usr/bin/python
import sys, pygame
from pygame.locals import *
import time
import subprocess
import os
import glob
import re
#import pylast
from mpd import MPDClient
#import mpd
from math import ceil
import datetime
from datetime import timedelta
import pitft_ui
from signal import alarm, signal, SIGALRM, SIGTERM, SIGKILL
import logging
from logging.handlers import TimedRotatingFileHandler
from daemon import Daemon

import config
#import curses

# OS enviroment variables for pitft
os.environ["SDL_FBDEV"] = "/dev/fb1"
os.environ["SDL_MOUSEDEV"] = "/dev/input/touchscreen"
os.environ["SDL_MOUSEDRV"] = "TSLIB"

# Logging configs
logger = logging.getLogger("PMB PiTFT logger")
logger.setLevel(logging.INFO)
#logger.setLevel(logging.DEBUG)

handler = TimedRotatingFileHandler('logs/pmb-pitft.log',when="midnight",interval=1,backupCount=7)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

showscreen = 1 # 1 - playing screen 2 - playlist screen
#i = 0
#global i
#a=0
# Mouse related variables
minSwipe = 50
maxClick = 30
longPressTime = 200

#window=curses.initscr()
#curses.noecho()
#ecran = window.subwin(0, 0)
#ecran.box()
#ecran.refresh()



## HAX FOR FREEZING ##
class Alarm(Exception):
	pass
def alarm_handler(signum, frame):
	logger.debug("ALARM")
	raise Alarm
## HAX END ##

def signal_term_handler(signal, frame):
    logger.debug('got SIGTERM')
    sys.exit(0)



class PMBPitftDaemon(Daemon):
	sm = None
	client = None
	network = None
	screen = None

	# Setup Python game, MPD, Last.fm and Screen manager
	def setup(self):
		logger.info("Starting setup")
		signal(SIGTERM, signal_term_handler)
		# Python game ######################
		logger.info("Setting pygame")
		pygame.init()
                infoObject = pygame.display.Info()
                logger.info(infoObject.current_w)
                logger.info(infoObject.current_h)
                self.screen = pygame.display.set_mode((infoObject.current_w,infoObject.current_h),FULLSCREEN)
		pygame.mouse.set_visible(False)

		# Hax for freezing
		signal(SIGALRM, alarm_handler)
		alarm(3)
		try:
			# Set screen size
			#size = width, height = 480, 320
			self.screen = pygame.display.set_mode((480,320),FULLSCREEN)
			alarm(0)
		except Alarm:
			logger.debug("Keyboard interrupt?")
			raise KeyboardInterrupt
		# Hax end

		logger.info("Display driver: %s" % pygame.display.get_driver())

		# MPD ##############################
		logger.info("Setting MPDClient")
		self.client = MPDClient()
		self.client.timeout = 10
		self.client.idletimeout = None

		# Pylast ####################################################################  
		#logger.info("Setting Pylast")
		# You have to have your own unique two values for API_KEY and API_SECRET
		# Obtain yours from http://www.last.fm/api/account for Last.fm
		#API_KEY = "dcbf56084b47ffbd3cc6755724cb12fa"
		#API_SECRET = "a970660ef47453134192fa6a9fa6da31"

		# In order to perform a write operation you need to authenticate yourself
		#username = "your_user_name"
		#password_hash = pylast.md5("your_password")
		#self.network = pylast.LastFMNetwork(api_key = API_KEY, api_secret = API_SECRET)

		# Screen manager ###############

		logger.info("Setting screen manager")
		try:
			self.sm = pitft_ui.PmbPitft(self.client, self.network, logger)
		except Exception, e:
			logger.exception(e)
			raise

	# Connect to MPD server
	def connectToMPD(self):
		logger.info("Trying to connect MPD server")
		noConnection = True
		while noConnection:
			try:
				self.client.connect("localhost", 6600)
				noConnection=False
			except Exception, e:
				logger.info(e)
				noConnection=True
				time.sleep(15)
		logger.info("Connection to MPD server established.")

	# Function to detect swipes
	# -1 is that it was not detected as a swipe or click
	# It will return 1 , 2 for horizontal swipe
	# If the swipe is vertical will return 3, 4
	# If it was a click it will return 0
	def getSwipeType(self,pos,pos2):

		x = pos2[0] - pos [0]
		y = pos2[1] - pos [1]
		#x,y=pygame.mouse.get_rel()

		logger.debug("screen swipe length x y %s %s" % (x,y))  #for debugging purposes

		#if abs(x)<=minSwipe:
		if abs(y)<=minSwipe:
			#if abs(x) < maxClick and abs(y)< maxClick:
			if abs(y)< maxClick:
				return 0
			else:
				return -1
		elif y>minSwipe:
			return 3
		elif y<-minSwipe:
			return 4
		#elif abs(y)<=minSwipe:
		#	if x>minSwipe:
		#		return 1
		#	elif x<-minSwipe:
		#		return 2
		#return 0

	def swipe(self,swipe):
		if swipe == 3:
			#self.currentSong = self.currentSong + self.maxInView
			#if self.currentSong > len(self.songs):
			#	self.currentSong = self.currentSong - self.maxInView
			#self.setSongs()
			if showscreen == 2:
				# touch for playlistscreen
				self.button(18,0) # move 7 up
			elif showscreen == 3:
				self.button(16,0)
			elif showscreen == 4:
				self.button(16,0)

		elif swipe == 4:
			#self.currentSong = self.currentSong - self.maxInView
			#if self.currentSong < 0:
			#	self.currentSong = 0
			#self.setSongs()	

			if showscreen == 2:
				# touch for playlistscreen
				self.button(19,0) # move 7 down		
			elif showscreen == 3:
				self.button(17,0) # move 7 down
			elif showscreen == 4:
				self.button(17,0) # move 7 down

	# Click handler

#	def on_click_lib_list_albumartist(self):		
#
#		click_pos = (pygame.mouse.get_pos() [0], pygame.mouse.get_pos() [1])
#		if  375 <= click_pos[0] <= 420 and 120 <= click_pos[1] <= 260:
#			self.button(20,0) # bck to main screen
#		elif 420 <= click_pos[0] <= 480 and 0 <= click_pos[1] <=70:
#			self.button(11,0) # move 1 up
#		elif 420 <= click_pos[0] <= 480 and 260 <= click_pos[1] <=320:
#			self.button(12,0) # move 1 down		
#		elif 375 <= click_pos[0] <= 420 and 50 <= click_pos[1] <=120:
#			self.button(14,0) # move back 1 folder
#		elif 420 <= click_pos[0] <= 480 and 70 <= click_pos[1] <=120:
#			self.button(16,0) # move 7 up
#		elif 420 <= click_pos[0] <= 480 and 190 <= click_pos[1] <=260:
#			self.button(17,0) # move 7 down		
#		elif 420 <= click_pos[0] <= 480 and 120 <= click_pos[1] <=190:
#			self.button(22,0) # switch to screen 3 - library list folder view
#
		# select folder to go into
#		elif 50 <= click_pos[0] <= 300 and 27 <= click_pos[1] <=67:
			# get URI for the first item on screen
#			self.button(13,0)
#		elif 50 <= click_pos[0] <= 300 and 67 <= click_pos[1] <=107:
#			self.button(13,1)
#		elif 50 <= click_pos[0] <= 300 and 107 <= click_pos[1] <=147:
#			self.button(13,2)
#		elif 50 <= click_pos[0] <= 300 and 147 <= click_pos[1] <=187:
#			self.button(13,3)
#		elif 50 <= click_pos[0] <= 300 and 187 <= click_pos[1] <=227:
#			self.button(13,4)
#		elif 50 <= click_pos[0] <= 300 and 227 <= click_pos[1] <=267:
#			self.button(13,5)
#		elif 50 <= click_pos[0] <= 300 and 267 <= click_pos[1] <=307:
#			self.button(13,6)
#		# select folder/track to add to playlist	
#		elif 0 <= click_pos[0] <= 50 and 27 <= click_pos[1] <=67:
#			self.button(15,0)
#		elif 0 <= click_pos[0] <= 50 and 67 <= click_pos[1] <=107:
#			self.button(15,1)
#		elif 0 <= click_pos[0] <= 50 and 107 <= click_pos[1] <=147:
#			self.button(15,2)
#		elif 0 <= click_pos[0] <= 50 and 147 <= click_pos[1] <=187:
#			self.button(15,3)
#		elif 0 <= click_pos[0] <= 50 and 187 <= click_pos[1] <=227:
#			self.button(15,4)
#		elif 0 <= click_pos[0] <= 50 and 227 <= click_pos[1] <=267:
#			self.button(15,5)
#		elif 0 <= click_pos[0] <= 50 and 267 <= click_pos[1] <=307:
#			self.button(15,6)

	def on_click_lib_list_albumartist(self):		

		click_pos = (pygame.mouse.get_pos() [0], pygame.mouse.get_pos() [1])
		if  430 <= click_pos[0] <= 480 and 20 <= click_pos[1] <= 70:
			self.button(20,0) # bck to main screen
		#elif 420 <= click_pos[0] <= 480 and 0 <= click_pos[1] <=70:
		#	self.button(11,0) # move 1 up
		#elif 420 <= click_pos[0] <= 480 and 260 <= click_pos[1] <=320:
		#	self.button(12,0) # move 1 down		
		elif 430 <= click_pos[0] <= 480 and 260 <= click_pos[1] <=320:
			self.button(14,0) # move back 1 folder
		#elif 420 <= click_pos[0] <= 480 and 70 <= click_pos[1] <=120:
		#	self.button(16,0) # move 7 up
		#elif 420 <= click_pos[0] <= 480 and 190 <= click_pos[1] <=260:
		#	self.button(17,0) # move 7 down		
		elif 430 <= click_pos[0] <= 480 and 120 <= click_pos[1] <=190:
			self.button(22,0) # switch to screen 4 - libriary list album artwork

		#	vertical scroll bar	
		elif 400 <= click_pos[0] <= 430 and 23 <= click_pos[1] <=301:
			# calculate touch poistion - between 0 and 1
			logger.debug("Library - Scrollbar Touch")
			y_click_val = click_pos[1]
			lib_list_percent = y_click_val / 278. # % pos of touched bar
			logger.debug("Library - Scrollbar Touch Percent %s" % lib_list_percent)
			self.button(33,lib_list_percent) # goto library list position 0 to 1

		# select folder to go into
		elif 50 <= click_pos[0] <= 300 and 27 <= click_pos[1] <=67:
			# get URI for the first item on screen
			self.button(13,0)
		elif 50 <= click_pos[0] <= 300 and 67 <= click_pos[1] <=107:
			self.button(13,1)
		elif 50 <= click_pos[0] <= 300 and 107 <= click_pos[1] <=147:
			self.button(13,2)
		elif 50 <= click_pos[0] <= 300 and 147 <= click_pos[1] <=187:
			self.button(13,3)
		elif 50 <= click_pos[0] <= 300 and 187 <= click_pos[1] <=227:
			self.button(13,4)
		elif 50 <= click_pos[0] <= 300 and 227 <= click_pos[1] <=267:
			self.button(13,5)
		elif 50 <= click_pos[0] <= 300 and 267 <= click_pos[1] <=307:
			self.button(13,6)
		# select folder/track to add to playlist	
		elif 0 <= click_pos[0] <= 50 and 27 <= click_pos[1] <=67:
			self.button(15,0)
		elif 0 <= click_pos[0] <= 50 and 67 <= click_pos[1] <=107:
			self.button(15,1)
		elif 0 <= click_pos[0] <= 50 and 107 <= click_pos[1] <=147:
			self.button(15,2)
		elif 0 <= click_pos[0] <= 50 and 147 <= click_pos[1] <=187:
			self.button(15,3)
		elif 0 <= click_pos[0] <= 50 and 187 <= click_pos[1] <=227:
			self.button(15,4)
		elif 0 <= click_pos[0] <= 50 and 227 <= click_pos[1] <=267:
			self.button(15,5)
		elif 0 <= click_pos[0] <= 50 and 267 <= click_pos[1] <=307:
			self.button(15,6)

	def on_click_settings(self):		

		click_pos = (pygame.mouse.get_pos() [0], pygame.mouse.get_pos() [1])
		if  430 <= click_pos[0] <= 480 and 20 <= click_pos[1] <= 70:
			self.button(20,0) # back to main screen
		elif 430 <= click_pos[0] <= 480 and 260 <= click_pos[1] <=320:
			self.button(5,0) # back to playlist screen
		elif 430 <= click_pos[0] <= 480 and 120 <= click_pos[1] <=190:
			self.button(28,0) # refresh library

		# settings toggle buttons

		elif 195 <= click_pos[0] <= 245 and 55 <= click_pos[1] <=125:
			self.button(24,0) # repeat
		elif 82 <= click_pos[0] <= 132 and 135 <= click_pos[1] <=207:
			self.button(25,0) # random		
		elif 297 <= click_pos[0] <= 347 and 135 <= click_pos[1] <=207:
			self.button(27,0) # single
		elif 195 <= click_pos[0] <= 245 and 215 <= click_pos[1] <=285:
			self.button(26,0) # consume		


	def on_click_lib_list(self):		

		click_pos = (pygame.mouse.get_pos() [0], pygame.mouse.get_pos() [1])
		if  430 <= click_pos[0] <= 480 and 20 <= click_pos[1] <= 70:
			self.button(20,0) # bck to main screen
		#elif 420 <= click_pos[0] <= 480 and 0 <= click_pos[1] <=70:
		#	self.button(11,0) # move 1 up
		#elif 420 <= click_pos[0] <= 480 and 260 <= click_pos[1] <=320:
		#	self.button(12,0) # move 1 down		
		elif 430 <= click_pos[0] <= 480 and 260 <= click_pos[1] <=320:
			self.button(14,0) # move back 1 folder
		#elif 420 <= click_pos[0] <= 480 and 70 <= click_pos[1] <=120:
		#	self.button(16,0) # move 7 up
		#elif 420 <= click_pos[0] <= 480 and 190 <= click_pos[1] <=260:
		#	self.button(17,0) # move 7 down		
		elif 430 <= click_pos[0] <= 480 and 120 <= click_pos[1] <=190:
			self.button(21,0) # switch to screen 4 - libriary list album artwork

		#	vertical scroll bar	
		elif 400 <= click_pos[0] <= 430 and 23 <= click_pos[1] <=301:
			# calculate touch poistion - between 0 and 1
			logger.debug("Library - Scrollbar Touch")
			y_click_val = click_pos[1]
			lib_list_percent = y_click_val / 278. # % pos of touched bar
			logger.debug("Library - Scrollbar Touch Percent %s" % lib_list_percent)
			self.button(33,lib_list_percent) # goto library list position 0 to 1

		# select folder to go into
		elif 50 <= click_pos[0] <= 300 and 27 <= click_pos[1] <=67:
			# get URI for the first item on screen
			self.button(13,0)
		elif 50 <= click_pos[0] <= 300 and 67 <= click_pos[1] <=107:
			self.button(13,1)
		elif 50 <= click_pos[0] <= 300 and 107 <= click_pos[1] <=147:
			self.button(13,2)
		elif 50 <= click_pos[0] <= 300 and 147 <= click_pos[1] <=187:
			self.button(13,3)
		elif 50 <= click_pos[0] <= 300 and 187 <= click_pos[1] <=227:
			self.button(13,4)
		elif 50 <= click_pos[0] <= 300 and 227 <= click_pos[1] <=267:
			self.button(13,5)
		elif 50 <= click_pos[0] <= 300 and 267 <= click_pos[1] <=307:
			self.button(13,6)
		# select folder/track to add to playlist	
		elif 0 <= click_pos[0] <= 50 and 27 <= click_pos[1] <=67:
			self.button(15,0)
		elif 0 <= click_pos[0] <= 50 and 67 <= click_pos[1] <=107:
			self.button(15,1)
		elif 0 <= click_pos[0] <= 50 and 107 <= click_pos[1] <=147:
			self.button(15,2)
		elif 0 <= click_pos[0] <= 50 and 147 <= click_pos[1] <=187:
			self.button(15,3)
		elif 0 <= click_pos[0] <= 50 and 187 <= click_pos[1] <=227:
			self.button(15,4)
		elif 0 <= click_pos[0] <= 50 and 227 <= click_pos[1] <=267:
			self.button(15,5)
		elif 0 <= click_pos[0] <= 50 and 267 <= click_pos[1] <=307:
			self.button(15,6)


	def on_click_playlist(self):
		
		# global i
		logger.debug("click playlist config.i %s" % config.i)
		click_pos = (pygame.mouse.get_pos() [0], pygame.mouse.get_pos() [1])
		if  430 <= click_pos[0] <= 480 and 20 <= click_pos[1] <= 70:
			self.button(20,0) # home button
		#elif 420 <= click_pos[0] <= 480 and 0 <= click_pos[1] <=70:
		#	self.button(1,0) # move up 1 track
		#elif 420 <= click_pos[0] <= 480 and 260 <= click_pos[1] <=320:
		#	self.button(2,0) # mve down 1 track
		elif 430 <= click_pos[0] <= 480 and 260 <= click_pos[1] <=320:
			self.button(23,0) # switch to screen 5 - settings screen
		#elif 420 <= click_pos[0] <= 480 and 70 <= click_pos[1] <=120:
		#	self.button(18,0) # move 7 up
		#elif 420 <= click_pos[0] <= 480 and 120 <= click_pos[1] <=260:
		#	self.button(19,0) # move 7 down		
		elif 430 <= click_pos[0] <= 480 and 120 <= click_pos[1] <=190:
			self.button(4,0)  # clear playlist

		#	vertical scroll bar	
		elif 400 <= click_pos[0] <= 430 and 23 <= click_pos[1] <=301:
			# calculate touch poistion - between 0 and 1
			logger.debug("Playlist - Scrollbar Touch")
			y_click_val = click_pos[1]
			lib_list_percent = y_click_val / 278. # % pos of touched bar
			logger.debug("Playlist - Scrollbar Touch Percent %s" % lib_list_percent)
			self.button(34,lib_list_percent) # goto playlist position 0 to 1

		# list all poss 7 tracks and pass track num to button 3
		# 1st track starts at y=27, each track text is 40 pix high
 		# click track to play it

		elif 50 <= click_pos[0] <= 300 and 27 <= click_pos[1] <=67:
			self.button(3,config.i)
		elif 50 <= click_pos[0] <= 300 and 67 <= click_pos[1] <=107:
			self.button(3,config.i+1)
		elif 50 <= click_pos[0] <= 300 and 107 <= click_pos[1] <=147:
			self.button(3,config.i+2)
		elif 50 <= click_pos[0] <= 300 and 147 <= click_pos[1] <=187:
			self.button(3,config.i+3)
		elif 50 <= click_pos[0] <= 300 and 187 <= click_pos[1] <=227:
			self.button(3,config.i+4)
		elif 50 <= click_pos[0] <= 300 and 227 <= click_pos[1] <=267:
			self.button(3,config.i+5)
		elif 50 <= click_pos[0] <= 300 and 267 <= click_pos[1] <=307:
			self.button(3,config.i+6)	

		# click track to delete from playlist	
		elif 0 <= click_pos[0] <= 50 and 27 <= click_pos[1] <=67:
			self.button(10,config.i)
		elif 0 <= click_pos[0] <= 50 and 67 <= click_pos[1] <=107:
			self.button(10,config.i+1)
		elif 0 <= click_pos[0] <= 50 and 107 <= click_pos[1] <=147:
			self.button(10,config.i+2)
		elif 0 <= click_pos[0] <= 50 and 147 <= click_pos[1] <=187:
			self.button(10,config.i+3)
		elif 0 <= click_pos[0] <= 50 and 187 <= click_pos[1] <=227:
			self.button(10,config.i+4)
		elif 0 <= click_pos[0] <= 50 and 227 <= click_pos[1] <=267:
			self.button(10,config.i+5)
		elif 0 <= click_pos[0] <= 50 and 267 <= click_pos[1] <=307:
			self.button(10,config.i+6)



		time.sleep(0.1)

	def on_click(self):
	
		#global i

		click_pos = (pygame.mouse.get_pos() [0], pygame.mouse.get_pos() [1])

		# Screen is off and its touched
		if self.sm.get_backlight_status() == 0 and 0 <= click_pos[0] <= 480 and 0 <= click_pos[1] <= 320:
			logger.debug("Screen off, Screen touch")
			self.button(9,0)
		# Screen is on. Check which button is touched 
		else:
			# There is no multi touch so if one button is pressed another one can't be pressed at the same time
			if 450 <= click_pos[0] <= 480 and 270 <= click_pos[1] <=300:
				logger.debug("Screen off")
				self.button(9,0)
			# track seek
			elif 10 <= click_pos[0] <= 460 and 280 <= click_pos[1] <=320:
				logger.debug("Track Seek") 
				self.button(0,click_pos[0])		
			#elif 223 <= click_pos[0] <= 285 and 6 <= click_pos[1] <=31:
			#	logger.debug("Toggle Repeat") 
			#	self.button(0)
			#elif 223 <= click_pos[0] <= 285 and 38 <= click_pos[1] <=63:
			#	logger.debug("Toggle random")
			#	self.button(1)	
			# Volume
			#elif 188 <= click_pos[0] <= 226 and 65 <= click_pos[1] <=100:
			#		logger.debug("Volume-")
			#		self.button(2)
			#elif 281 <= click_pos[0] <= 319 and 65 <= click_pos[1] <=100:
			#		logger.debug("Volume+")
			#		self.button(3)
			# SLEEP
			#elif 188 <= click_pos[0] <= 226 and 103 <= click_pos[1] <=138:
			#		logger.debug("Sleep-")
			#		self.button(4)
			elif 10 <= click_pos[0] <= 480 and 10 <= click_pos[1] <=80:
					logger.debug("Cover Click - Playlist")
					self.button(5,0)
			elif 10 <= click_pos[0] <= 210 and 80 <= click_pos[1] <=280:
					logger.debug("Cover Click - Library list")
					self.button(5,1)
			# Controls
			elif 250 <= click_pos[0] <= 280 and 155 <= click_pos[1] <=195:
					logger.debug("Prev")
					self.button(6,0)
			elif 310 <= click_pos[0] <= 370 and 144 <= click_pos[1] <=205:
					logger.debug("Toggle play/pause")
					self.button(7,0)
			elif 390 <= click_pos[0] <= 430 and 155 <= click_pos[1] <=195:
					logger.debug("Next")
					self.button(8,0) 
		time.sleep(0.1)

	def on_key_home(self,key):
		# key remote on home screen 

		#character = pygame.key.get_pressed()
		if (key==K_SPACE):
			#self.sm.toggle_playback()
			logger.debug("Key - Toggle play/pause")
			self.button(7,0)
		elif (key==K_LEFT):
			#self.sm.control_player("previous")
			logger.debug("Key - Prev")
			self.button(6,0)
		elif (key==K_RIGHT):
			#self.sm.control_player("next")
			logger.debug("Key - Next")
			self.button(8,0)
		elif (key==K_UP):
			logger.debug("Key - Playlist")
			self.button(5,0)
		elif (key==K_DOWN):
			logger.debug("Key - Library list")
			self.button(5,1)
		elif (key==K_ESCAPE):
			logger.debug("Key - Settings")
			self.button(23,0)
		elif (key==K_0):
			logger.debug("Key Screen Toggle")
			self.button(9,0)
		#time.sleep(0.1)		
	
	def on_key_playlist(self,key):
		# key remote on playlist screen 

		#character = pygame.key.get_pressed()
		if (key==K_SPACE):
			logger.debug("Key - Toggle play/pause")
			self.button(7,0)
		elif (key==K_x):
			logger.debug("Key - Home")
			self.button(20,0)
		elif (key==K_ESCAPE):
			logger.debug("Key - Settings")
			self.button(23,0)
		elif (key==K_UP):
			logger.debug("Key - Scroll Selector Up")
			self.button(29,0)
		elif (key==K_DOWN):
			logger.debug("Key - Scroll Selector Down")
			self.button(30,0)
		elif (key==K_RETURN):
			logger.debug("Key - Play Track")
			self.button(3,config.key_track_selected+config.i)

		#time.sleep(0.1)		

	def on_key_library(self,key):
		# key remote on library screen 

		#character = pygame.key.get_pressed()
		#if (key==K_SPACE):
		#	logger.debug("Key - Toggle play/pause")
		#	self.button(7,0)
		#elif (key[pygame.K_x]):
		if (key==K_x):			
			logger.debug("Key - Home")
			self.button(20,0)
		elif (key==K_ESCAPE):
			logger.debug("Key - Settings")
			self.button(23,0)
		elif (key==K_UP):
			logger.debug("Key - Scroll Selector Up")
			self.button(31,0)
		elif (key==K_DOWN):
			logger.debug("Key - Scroll Selector Down")
			self.button(32,0)
		elif (key==K_RETURN):
			#time.sleep(0.5)			
			logger.debug("Key - Enter Folder")
			self.button(13,"a")
		elif (key==K_BACKSPACE):
			#time.sleep(0.5)
			logger.debug("Key - Prev Folder")
			self.button(14,0)
		elif (key==K_SPACE):
			#time.sleep(0.5)			
			logger.debug("Key - Add Folder/Track to Playlist")
			self.button(15,"a")
		elif (key==K_0):
			# skip to library list 0%			
			logger.debug("Key - Skip to 0p/c Library List")
			self.button(33,0)
		elif (key==K_1):
			# skip to library list 10%			
			logger.debug("Key - Skip to 10p/c Library List")
			self.button(33,0.1)
		elif (key==K_2):
			# skip to library list 20%		
			logger.debug("Key - Skip to 20p/c Library List")
			self.button(33,0.2)
		elif (key==K_3):
			# skip to library list 30%	
			logger.debug("Key - Skip to 30p/c Library List")
			self.button(33,0.3)
		elif (key==K_4):
			# skip to library list 40%	
			logger.debug("Key - Skip to 40p/c Library List")
			self.button(33,0.4)
		elif (key==K_5):
			# skip to library list 50%	
			logger.debug("Key - Skip to 50p/c Library List")
			self.button(33,0.5)
		elif (key==K_6):
			# skip to library list 60%
			logger.debug("Key - Skip to 60p/c Library List")
			self.button(33,0.6)
		elif (key==K_7):
			# skip to library list 70%
			logger.debug("Key - Skip to 70p/c Library List")
			self.button(33,0.7)
		elif (key==K_8):
			# skip to library list 80%
			logger.debug("Key - Skip to 80p/c Library List")
			self.button(33,0.8)
		elif (key==K_9):
			# skip to library list 90%
			logger.debug("Key - Skip to 90p/c Library List")
			self.button(33,0.9)


	def on_key_settings(self,key):
		# key remote on settigs screen 

		#character = pygame.key.get_pressed()
		if (key==K_SPACE):
			logger.debug("Key - Toggle play/pause")
			self.button(7,0)
		elif (key==K_x):
			logger.debug("Key - Home")
			self.button(20,0)
		elif (key==K_RETURN):
			self.button(28,0) # refresh library

		# settings toggle buttons

		elif (key==K_UP):
			self.button(24,0) # repeat
		elif (key==K_LEFT):
			self.button(25,0) # random		
		elif (key==K_RIGHT):
			self.button(27,0) # single
		elif (key==K_DOWN):
			self.button(26,0) # consume		


	#define action on pressing buttons
	def button(self, number, x_pos):
		global showscreen
		#global i

		logger.debug("You pressed button %s" % number)
		if number == 0:    #specific script when exiting
			#self.sm.toggle_repeat()
			#x_pos = click_pos[0]
			self.sm.track_seek(x_pos)		
		elif number == 1:	
		#	self.sm.toggle_random()
			if config.i > 0:
				config.i = config.i -1
		elif number == 2:
		#	self.sm.set_volume(1, "-")
			if config.i < (config.curplaylistlength-7):
				config.i = config.i + 1
		elif number == 3:
		#	self.sm.set_volume(1, "+")
		#	playist switch track
		#	* get "i" then add to click num to get clicked track	
			logger.debug("button3 x_pos config.curplaylistlength %s %s" % (x_pos , config.curplaylistlength))	
			if x_pos < config.curplaylistlength:
				self.sm.goto_track(x_pos)

		elif number == 4:
		#	self.sm.adjust_sleeptimer(15, "-")
			self.sm.clear_playlist()

		elif number == 5:
			# change to playlist screen
			#self.sm.adjust_sleeptimer(15, "+")
			#i = 0
			if x_pos == 0:
				showscreen = 2
			elif x_pos == 1:
				showscreen = 3
		elif number == 6:
			self.sm.control_player("previous")

		elif number == 7:
			self.sm.toggle_playback()

		elif number == 8:
			self.sm.control_player("next")

		elif number == 9:
			self.sm.toggle_backlight()

		elif number == 10:
		#	remove track from playlist
			logger.debug("screen pressed: %s trackid: %s" % (str(number),str(x_pos))) # directory URI
			if x_pos < config.curplaylistlength:
				self.sm.remove_track(x_pos)

		elif number == 11:

			# library move 1 up
			logger.debug("screen pressed skip -1 %s" % str(config.libi[len(config.libi)-1]))

			if config.libi[len(config.libi)-1] > 0:
				#config.libi = config.libi -1
				config.libi[len(config.libi)-1] = config.libi[len(config.libi)-1] - 1

		elif number == 12:

			# library move 1 down
			#if config.libi < (config.curplaylistlength-7):
			logger.debug("screen pressed skip +1 %s" % str(config.libi[len(config.libi)-1]))
			if config.libi[len(config.libi)-1] < (config.folder_items - 7):
				config.libi[len(config.libi)-1] = config.libi[len(config.libi)-1] + 1

		elif number == 13:
			#config.prev_URL = config.URL
	
			if x_pos == "a":
				key_selected_offset = config.key_library_selected[len(config.key_library_selected)-1]
				clicked_itemURI = config.click_URI[config.libi[len(config.libi)-1]+key_selected_offset]
			else:
				clicked_itemURI = config.click_URI[config.libi[len(config.libi)-1]+x_pos]
				config.key_library_selected[len(config.key_library_selected)-1] = x_pos

			config.URL.append(clicked_itemURI)
			config.libi.append(0)
			config.key_library_selected.append(0)
			logger.debug("screen pressed %s" % str(clicked_itemURI)) # directory URI

		elif number == 14:
			# go back a folder
			if len(config.URL) >1:
				config.URL.pop()						
				config.libi.pop()
				config.key_library_selected.pop()

			#logger.debug("screen pressed - prev URL - %s %s" % (str(config.URL))) # directory URI

		elif number == 15:
			# add directory / track to playlist

			if x_pos == "a":
				key_selected_offset = config.key_library_selected[len(config.key_library_selected)-1]
				clicked_itemURI = config.click_URI[config.libi[len(config.libi)-1]+key_selected_offset]
			else:
				clicked_itemURI = config.click_URI[config.libi[len(config.libi)-1]+x_pos]
			logger.debug("screen pressed add  %s" % str(clicked_itemURI)) # directory URI

			self.sm.add_directory(clicked_itemURI)

			# skip 7 items for library/playlist scroll
		elif number == 16:
			logger.debug("screen pressed skip -7 %s folder items %s" % (str(config.libi[len(config.libi)-1]),config.folder_items))

			if config.libi[len(config.libi)-1] > 7:
				config.libi[len(config.libi)-1] = config.libi[len(config.libi)-1] - 7
			else:
				config.libi[len(config.libi)-1] = 0
			config.key_library_selected[len(config.key_library_selected)-1] = 0

		elif number == 17:
			logger.debug("screen pressed skip +7 %s folder items %s" % (str(config.libi[len(config.libi)-1]),config.folder_items))

			if config.folder_items > 7:

				if config.libi[len(config.libi)-1] < (config.folder_items - 7): 
					config.libi[len(config.libi)-1] = config.libi[len(config.libi)-1] + 7
				else:
					config.libi[len(config.libi)-1] = config.folder_items - 7
				config.key_library_selected[len(config.key_library_selected)-1] = 0

		elif number == 18:	
			# playlist move 7 up
			#	self.sm.toggle_random()
			if config.i > 7:
				config.i = config.i -7
			else:
				config.i = 0
			config.key_track_selected = 0

		elif number == 19:
			# playlist move 7 down
			#	self.sm.set_volume(1, "-")
			logger.debug("screen pressed playist skip +7 %s" % str(config.i))

			if config.i <= (config.curplaylistlength-7):
				config.i = config.i + 7
			else:
				config.i = config.curplaylistlength - 7
			config.key_track_selected = 0
			logger.debug("screen pressed playist skip +7 recalc %s" % str(config.i))

		elif number == 20:
			showscreen = 1

		elif number == 21:
			showscreen = 4

		elif number == 22:
			showscreen = 3

		elif number == 23:
			showscreen = 5 # settings screen

		elif number == 24:    # click repeat
			self.sm.toggle_repeat()
		elif number == 25:	# click random
			self.sm.toggle_random()
		elif number == 26:    #click consume
			self.sm.toggle_consume()
		elif number == 27:    #click single
			self.sm.toggle_single()
		elif number == 28:    #click update library
			self.sm.update_library()

		elif number == 29:	
		#	playlist key remote scroll up 1
			#if config.key_track_selected > 1:
			#	config.key_track_selected = config.key_track_selected -1
			#	if config.key_track_selected == config.i:
			#		config.i = config.i -1
			if config.key_track_selected > 0:
				config.key_track_selected = config.key_track_selected -1
			else:
				config.key_track_selected = 0
				config.i = config.i -1

		elif number == 30:
		#	playlist key remote scroll down 1
			#if config.key_track_selected < (config.curplaylistlength):
			#	config.key_track_selected = config.key_track_selected + 1
			#	if config.key_track_selected > config.i + 7:
			#		config.i = config.i + 1
			if config.key_track_selected < config.curplaylistlength-1:
				if (config.key_track_selected < 6):
					config.key_track_selected = config.key_track_selected + 1
				else:
					config.key_track_selected = 6
					config.i = config.i + 1

		elif number == 31:

			# remote key library scroll 1 up
			logger.debug("remote key pressed skip -1 libi library_selected %s %s" % (str(config.libi[len(config.libi)-1]),config.key_library_selected))
			if config.libi[len(config.libi)-1] > -1:
				if config.key_library_selected[len(config.key_library_selected)-1] > 0:
					config.key_library_selected[len(config.key_library_selected)-1] = config.key_library_selected[len(config.key_library_selected)-1] -1
				#config.libi = config.libi -1
				#if config.key_library_selected[len(config.key_library_selected)-1] == config.libi[len(config.libi)-1]:
				else:
					if config.libi[len(config.libi)-1] > 0:
						config.libi[len(config.libi)-1] = config.libi[len(config.libi)-1] - 1
						config.key_library_selected[len(config.key_library_selected)-1] = 0

		elif number == 32:

			logger.debug("remote key pressed skip +1 libi library_selected %s %s" % (str(config.libi[len(config.libi)-1]),config.key_library_selected))
			# remote key library scroll 1 down
			#if config.libi < (config.curplaylistlength-7):
			if config.key_library_selected[len(config.key_library_selected)-1] < (config.folder_items-1):
				if config.key_library_selected[len(config.key_library_selected)-1] < 6:
					config.key_library_selected[len(config.key_library_selected)-1] = config.key_library_selected[len(config.key_library_selected)-1] +1
				#if config.key_library_selected[len(config.key_library_selected)-1] > config.libi[len(config.libi)-1] + 7:
					#if config.libi[len(config.libi)-1] < (config.folder_items - 7):
				else:
					config.libi[len(config.libi)-1] = config.libi[len(config.libi)-1] + 1
					config.key_library_selected[len(config.key_library_selected)-1] = 6

		elif number == 33:

			# remote key library scroll to 0% to 100% page skip - x_pos = 0,0.1,0.2....0.9 of config.folder_items

			logger.debug("remote key pressed skip %s percent libi library_selected %s folder items %s" % (x_pos,str(config.libi[len(config.libi)-1]),config.folder_items))

			if x_pos == 0:
				config.libi[len(config.libi)-1] = 0
			else:
				# calculate which screen from x_pos %age
				config.libi[len(config.libi)-1] = int(config.folder_items * x_pos)

			config.key_library_selected[len(config.key_library_selected)-1] = 0

		elif number == 34:

			# remote key playlist scroll to 0% to 100% page skip - x_pos = 0,0.1,0.2....0.9 of config.folder_items
			#if config.key_track_selected < config.curplaylistlength-1:
			#	if (config.key_track_selected < 6):
			#		config.key_track_selected = config.key_track_selected + 1
			#	else:
			#		config.key_track_selected = 6
			#		config.i = config.i + 1

			logger.debug("remote key pressed skip %s percent config.i %s playlist items %s" % (x_pos,str(config.i),config.curplaylistlength))

			if x_pos == 0:
				config.i = 0
			else:
				# calculate which screen from x_pos %age
				config.i = int(config.curplaylistlength * x_pos)

			config.key_track_selected = 0

	def shutdown(self):
		# Close MPD connection
		if self.client:
			self.client.close()
			self.client.disconnect()

	# Main loop
	def run(self):
		global showscreen
		#global i
	
		self.setup()
		self.connectToMPD()

		refresh_interval = 500
		pygame.key.set_repeat(550,50)

		liblistalbum_refresh = 1

		try:
			drawtime = datetime.datetime.now()
			while 1:

				for event in pygame.event.get():

					#keys = pygame.key.get_pressed()

					if event.type == pygame.KEYDOWN:

						key = event.key
						logger.debug("remote key repeat pressed %s" % key) #for debugging purposes

						if showscreen == 1:
							self.on_key_home(key)
						elif showscreen == 2:
							self.on_key_playlist(key)
						elif showscreen == 3:
							self.on_key_library(key)
						elif showscreen == 5:
							self.on_key_settings(key)

					
					#	if showscreen == 2:
					#		if key==K_DOWN or key==K_UP:
					#			self.on_key_playlist(key)
					#	elif showscreen == 3:
					#		if key==K_DOWN or key==K_UP:
					#			self.on_key_library(key)


					if event.type == pygame.MOUSEBUTTONDOWN:
						logger.debug("screen pressed") #for debugging purposes
						pos = (pygame.mouse.get_pos() [0], pygame.mouse.get_pos() [1])
						logger.debug("touch x y %s %s" % (pos[0],pos[1]))

						#liblistalbum_refresh = 1

					#	#pygame.draw.circle(screen, (255,255,255), pos, 2, 0) #for debugging purposes - adds a small dot where the screen is pressed
					#	logger.debug("screen state %s" % showscreen)
					
					# Mouse released
					if event.type == pygame.MOUSEBUTTONUP:
						#logger.debug("screen swipe") #for debugging purposes
						pos2 = (pygame.mouse.get_pos() [0], pygame.mouse.get_pos() [1])
						logger.debug("release x y %s %s" % (pos2[0],pos2[1]))
				
						swipe = self.getSwipeType(pos,pos2)

						logger.debug("swipe %s " % str(swipe)) #for debugging purposes

						liblistalbum_refresh = 1

						if(swipe != -1):																									
							if showscreen == 1:
								self.on_click()
							elif showscreen == 2:
								# touch for playlistscreen
								if swipe >2:
									logger.debug("swipe 3or4 playlist %s " % str(swipe)) #for debugging purposes

									self.swipe(swipe)
								else:
									self.on_click_playlist()
							elif showscreen == 3:
								if swipe >2:
									logger.debug("swipe 3or4 lib-list %s " % str(swipe)) #for debugging purposes

									self.swipe(swipe)
								else:	
									self.on_click_lib_list()
							elif showscreen == 4:
								# click for album artist library view		
								self.on_click_lib_list_albumartist()
							elif showscreen ==5:
								self.on_click_settings()


							#if (swipe == 1):
							#	a = a + swipe
				             #  			if a > len(pluginScreens) - 1: a = 0
							#else:
							#	try:
									# Pass to the plugin currently displayed
									#pluginScreens[a].mouseReleased(swipe, mouseDownPos, pygame.mouse.get_pos(),longPress(mouseDownTime))
									# Force to refresh the displayed plugin
									#refreshNow = True
							#	except AttributeError:
							#		pass


					#if event.type == pygame.MOUSEBUTTONDOWN:
					#	logger.debug("screen pressed") #for debugging purposes
					#	pos = (pygame.mouse.get_pos() [0], pygame.mouse.get_pos() [1])
					#	logger.debug(pos[0])
					#	#pygame.draw.circle(screen, (255,255,255), pos, 2, 0) #for debugging purposes - adds a small dot where the screen is pressed
					#	logger.debug("screen state %s" % showscreen)
					#	if showscreen == 1:
					#		self.on_click()
					#	elif showscreen == 2:
					#		# touch for playlistscreen
					#		self.on_click_playlist()
					#	else:
					#		self.on_click_lib_list()		

				# Update screen
				if drawtime < datetime.datetime.now():
					drawtime = datetime.datetime.now() + timedelta(milliseconds=refresh_interval)
					self.sm.refresh_mpd()
					self.sm.parse_mpd()

					if showscreen == 1:
						refresh_interval = 500
						self.sm.render(self.screen)
					elif showscreen == 2:
						refresh_interval = 50
						self.sm.renderplaylist(self.screen, config.i)
					elif showscreen == 3:
						refresh_interval = 50
						self.sm.renderlibrarylist(self.screen, config.i)
					elif showscreen == 4:
						refresh_interval = 50
						if liblistalbum_refresh == 1:
							self.sm.renderlibrarylist_albumartist(self.screen, config.i)
						#	liblist_refresh = 0
					elif showscreen == 5:
						refresh_interval = 500						
						self.sm.render_settings(self.screen)

					if showscreen == 4:
						if liblistalbum_refresh == 1:
							pygame.display.flip()
							liblistalbum_refresh = 0
					else:
						pygame.display.flip()		

			if showscreen == 4:
				if liblistalbum_refresh == 1:
					pygame.display.update()
					liblistalbum_refresh = 0
			else:			
				pygame.display.update()

		except Exception, e:
			logger.debug(e)
			raise

		curses.echo()
		curses.endwin()


if __name__ == "__main__":
	daemon = PMBPitftDaemon('/tmp/pmbpitft-daemon.pid')
	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			daemon.start()
		elif 'stop' == sys.argv[1]:
			daemon.shutdown()
			daemon.stop()
		elif 'restart' == sys.argv[1]:
			daemon.restart()
		else:
			print "Unknown command"
			sys.exit(2)
		sys.exit(0)
	else:
		print "usage: %s start|stop|restart" % sys.argv[0]
		sys.exit(2)
