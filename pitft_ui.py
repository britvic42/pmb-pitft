# -*- coding: utf-8 -*-
import sys, pygame
from pygame.locals import *
import time
import subprocess
import os
import glob
import re
from math import ceil
from threading import Thread
from mpd import MPDClient
#import mpd
import datetime
from datetime import timedelta
#import collections
from text_control import Text_Control
import config

#global i

class PmbPitft:

	def __init__(self, client, lfm, logger):

		self.mpdc = client
		self.lfm = lfm
		self.logger = logger

		# Paths
		self.path = os.path.dirname(sys.argv[0]) + "/root/pmb-pitft/pmb-pitft/"
		os.chdir(self.path)

		# Fonts
		#self.fontfile2 = self.path + "OpenSans-Regular.ttf"
		self.fontfile2 = self.path + "BebasNeue-TTF/BebasNeue-Regular.ttf"
		self.fontfile = self.path + "BebasNeue-TTF/BebasNeue-Bold.ttf"
		#		self.logger.info(self.fontfile)
		#		self.logger.info(self.fontfile2)
		self.font = {}
		self.font['details']	= pygame.font.Font(self.fontfile, 20)
		self.font['tracktitle'] = pygame.font.Font(self.fontfile,32)
		self.font['field']	= pygame.font.Font(self.fontfile2, 22)
		self.font['details_sm'] = pygame.font.Font(self.fontfile,16)
		self.font['tracktitle_sm'] = pygame.font.Font(self.fontfile,24)
		self.font['field_sm'] = pygame.font.Font(self.fontfile2,20)

		# Images
		self.image = {}
		self.image["background"]		=pygame.image.load(self.path + "background-black.png")
		# self.image["coverart_place"]		=pygame.image.load(self.path + "coverart-placer.png")
		# self.image["details"]			=pygame.image.load(self.path + "details.png")
		#self.image["field"]			=pygame.image.load(self.path + "field-value.png")
		#self.image["indicator_blue"]		=pygame.image.load(self.path + "indicator-blue.png")
		#self.image["indicator_red"]			=pygame.image.load(self.path + "indicator-red.png")
		self.image["position_bg"]			=pygame.image.load(self.path + "position-background-460.png")
		self.image["position_fg"]			=pygame.image.load(self.path + "position-foreground-460.png")
		#		self.image["icon_randomandrepeat"]	=pygame.image.load(self.path + "randomandrepeat.png")
		self.image["icon_screenoff"]		=pygame.image.load(self.path + "screen-off.png")

		# Buttons
		self.image["button_next"]		=pygame.image.load(self.path + "button-next.png")
		self.image["button_pause"]		=pygame.image.load(self.path + "button-pause.png")
		self.image["button_play"]		=pygame.image.load(self.path + "button-play.png")
		self.image["button_prev"]		=pygame.image.load(self.path + "button-prev.png")
		#		self.image["button_timeminus"]	=pygame.image.load(self.path + "button-timeminus.png")
		#		self.image["button_timeplus"]	=pygame.image.load(self.path + "button-timeplus.png")
		#		self.image["button_volumeminus"]=pygame.image.load(self.path + "button-volumeminus.png")
		#		self.image["button_volumeplus"]	=pygame.image.load(self.path + "button-volumeplus.png")
		#self.image["button_toggle_off"]	=pygame.image.load(self.path + "toggle-off.png")
		#self.image["button_toggle_on"]	=pygame.image.load(self.path + "toggle-on.png")
		#self.image["nocover"]			=pygame.image.load(self.path + "no-cover.png")
		self.image["nocover"]			=pygame.image.load("NONE - NONE.jpg")

		self.image["music_icon"]			=pygame.image.load("music-icon-white-30.png")
		self.image["folder_icon"]			=pygame.image.load("folder-icon-30.png")

		self.image["arrowaup_icon"]			=pygame.image.load("arrow-up-grey-50.png")
		self.image["arrowdown_icon"]			=pygame.image.load("arrow-down-grey-50.png")
		self.image["pageup_icon"]			=pygame.image.load("page-up-white-50.png")
		self.image["pagedown_icon"]			=pygame.image.load("page-down-white-50.png")
		self.image["backfolder_icon"]			=pygame.image.load("folder-icon-back-50.png")
		self.image["homescreen_icon"]			=pygame.image.load("home-icon-white-50.png")
		self.image["deleteplaylist_icon"]			=pygame.image.load("delete-icon-50.png")
		#self.image["deleteplaylist_sm_icon"]			=pygame.image.load("delete-icon-30.png")
		self.image["deleteplaylist_sm_icon"]			=pygame.image.load("delete-track-icon-cross-25.png")

		self.image["playlist_icon"]			=pygame.image.load("song-playlist-icon-50.png")

		self.image["button_settings"]			=pygame.image.load("button-settings-50.png")

		self.image["button_single"]			=pygame.image.load("button-single-50.png")
		self.image["button_repeat"]			=pygame.image.load("button-repeat-50.png")
		self.image["button_random"]			=pygame.image.load("button-random-50.png")				

		# Threads
		self.coverartThread = None
		self.oldCoverartThreadRunning = False

		# Things to remember
		self.sleepTimer = None
		self.processingCover = False
		self.coverFetched = False
		self.status = {}
		self.song = {}
		self.reconnect = False

		# Things to show
		self.trackfile = None
		self.artist = "NONE"
		self.album = "NONE"
		self.title = "NONE"
		self.timeElapsed = "00:00"
		self.timeTotal = "00:00"
		self.timeElapsedPercentage = 0
		self.playbackStatus = "stop"
		self.sleepTimerText = "OFF"
		self.volume = 0
		self.random = 0
		self.repeat = 0
		self.consume = 0
		self.single = 0		
		self.cover = False
		self.playlistlength = 0
		self.fileext = "dunno"
		self.timeTotalsecs = 0
		self.playlistpos = 0
		self.audiorate = ""
		currentaudiorate = "none"
		self.track_time = "00:00"
		#audiorates = {"44100:16:2":"16 bit / 44.1 khz","96000:16:2":"16 bit / 96 khz","192000:16:2":"16 bit / 192 khz","44100:24:2":"24 bit / 44.1 khz","96000:24:2":"24 bit / 96 khz","192000:24:2":"24 bit / 192 khz","44100:32:2":"32 bit / 44.1 khz","96000:32:2":"32 bit / 96 khz","192000:32:2":"32 bit / 192 khz","384000:32:2":"32 bit / 384 khz"}
		
		# What to update
		self.updateTrackInfo = False
		self.updateAlbum	 = False	
		self.updateElapsed	 = False
		self.updateRandom	 = False
		self.updateConsume	 = False
		self.updateSingle	 = False		
		self.updateRepeat	 = False
		self.updateVolume	 = False
		self.updateState	 = False
		self.updateSleepTimer	 = False		
		#	self.updatePlaylistlength 	 = False
		#		self.updateAudiorate	 = False
		#		self.updateFileext	 = False
		#		self.updatePlaylistpos	 = False
		self.updateAll		 = True

		# Print data
		self.logger.info("MPD server version: %s" % self.mpdc.mpd_version)
		
		# Turn backlight on
		self.turn_backlight_on()

	def convert_time(self,timesecs):

		self.track_time = "00:00"
		# convert time ins seconds to mins:secs
		min = int(ceil(float(timesecs)))/60
		min = min if min > 9 else "0%s" % min
		sec = int(ceil(float(timesecs)%60))
		sec = sec if sec > 9 else "0%s" % sec
		if sec == 60:
			sec = "00"
		return "%s:%s" % (min,sec)

	def refresh_mpd(self):

		#global i

		if self.reconnect:
			self.reconnect_mpd()
		if self.reconnect == False:
			connection = False
			try:
				self.status = self.mpdc.status()
				self.song = self.mpdc.currentsong()
				#self.playlist = playlistinfo()
				connection = True
			except Exception as e:
				self.logger.debug(e)
				connection = False
				self.status = {}
				self.song = {}
				self.playlist = {}

			if connection == False:
				try:
					if e.errno == 32:
						self.reconnect = True
					else:
						print "Nothing to do"
				except Exception, e:
					self.reconnect = True
					self.logger.debug(e)

	def reconnect_mpd(self):
		self.logger.info("Reconnecting to MPD server")
		client = MPDClient()
		client.timeout = 10
		client.idletimeout = None
		noConnection = True
		while noConnection:
			try:
				client.connect("localhost", 6600)
				noConnection=False
			except Exception, e:
				self.logger.info(e)
				noConnection=True
				time.sleep(15)
		self.mpdc = client
		self.reconnect = False
		self.logger.info("Connection to MPD server established.")


	def parse_mpd(self):
		# -------------
		# |  PARSE    |
		# -------------
		# Artist
		try:
			artist = self.song["artist"].decode('utf-8')
		except:
			artist = "NONE"
		
		# Album
		try:
			album = self.song["album"].decode('utf-8')
		except:
			album = "NONE"

		# Track URL
		try:
			track_URL = self.song["file"].decode('utf-8')
		except:
			track_URL = "NONE"

		# Track Title
		try:
			title = self.song["title"].decode('utf-8')
		except:
			title = "NONE"

		# Time elapsed
		try:
			min = int(ceil(float(self.status["elapsed"])))/60
			min = min if min > 9 else "0%s" % min
			sec = int(ceil(float(self.status["elapsed"])%60))
			sec = sec if sec > 9 else "0%s" % sec
			if sec == 60:
				sec = "00"
			timeElapsed = "%s:%s" % (min,sec)
		except:
			timeElapsed = "00:00"

		# Time total
		try:
			min = int(ceil(float(self.song["time"])))/60
			min = min if min > 9 else "0%s" % min
			sec = int(ceil(float(self.song["time"])%60))
			sec = sec if sec > 9 else "0%s" % sec
			timeTotal = "%s:%s" % (min,sec)
			timeTotalsecs = int(self.song["time"])
		except:
			timeTotal = "00:00"
			timeTotalsecs = 60

		# Time elapsed percentage
		try:
			timeElapsedPercentage = float(self.status["elapsed"])/float(self.song["time"])
		except:
			timeElapsedPercentage = 0

		# Playback status
		try:
			playbackStatus = self.status["state"]
		except:
			playbackStatus = "stop"

		# Repeat
		try:
			repeat = int(self.status["repeat"])
		except:
			repeat = 0

		# Random
		try:
			random = int(self.status["random"])
		except:
			random = 0

		# Consume
		try:
			consume = int(self.status["consume"])
		except:
			consume = 0

		# Single
		try:
			single = int(self.status["single"])
		except:
			single = 0

		# Volume
		try:
			volume = int(self.status["volume"])
		except:
			volume = 0

		# Audio - sampleRate:bits:channels
		try:
			audiorate = self.status["audio"].decode('utf-8')
		except:
			audiorate = "unknown"

        # playistlength
		try:
			playlistlength = self.status["playlistlength"]
		except:
			playlistlength = "0"

		# playlistpos
		try:
			playlistpos = int(self.status["song"]) + 1
		except:
			playlistpos = "0"

		# fileext - file extension flac/mp3
		try:
			fileext = self.song["file"].decode('utf-8')
		except:
			fileext = "???"

		# -------------
		# |  CHANGES  |
		# -------------
		# Artist
		if self.artist != artist:
			self.artist = artist
			self.updateTrackInfo = True

		# Album
		if self.album != album or self.oldCoverartThreadRunning:
			self.logger.debug("Album if")
			self.album = album
			self.track_URL = track_URL
			self.updateAlbum = True
			self.cover = False
			# Find cover art on different thread
			try:
				if self.coverartThread:
					self.logger.debug("if caT")
					if self.coverartThread.is_alive():
						self.logger.debug("caT is alive")
						self.oldCoverartThreadRunning = True
					else:
						self.logger.debug("caT not live")
						self.oldCoverartThreadRunning = False
						self.coverartThread = Thread(target=self.fetch_coverart)
						self.logger.debug("caT go")
						self.coverartThread.start()
				else:
					self.logger.debug("not caT")
					self.coverartThread = Thread(target=self.fetch_coverart)
					self.coverartThread.start()
			except Exception, e:
				self.logger.debug("Coverartthread: %s" % e)
				self.processingCover = False

		# Track Title
		if self.title != title:
			self.title = title
			self.updateTrackInfo = True

		# Time elapsed
		if self.timeElapsed != timeElapsed:
			self.timeElapsed = timeElapsed
			self.updateElapsed = True

		# Time total
		if self.timeTotal != timeTotal:
			self.timeTotal = timeTotal
			self.timeTotalsecs = timeTotalsecs
			self.updateTrackInfo = True
			self.updateElapsed = True

		# Time elapsed percentage
		if self.timeElapsedPercentage != timeElapsedPercentage:
			self.timeElapsedPercentage = timeElapsedPercentage
			self.updateElapsed = True

		# Playback status
		if self.playbackStatus != playbackStatus:
			self.playbackStatus = playbackStatus
			self.updateState = True

		# Repeat
		if self.repeat != repeat:
			self.repeat = repeat
			self.updateRepeat = True

		# Random
		if self.random != random:
			self.random = random
			self.updateRandom = True

		# Consume
		if self.consume != consume:
			self.consume = consume
			self.updateConsume = True

		# Single
		if self.single != single:
			self.single = single
			self.updateSingle = True

		# Volume
		if self.volume != volume:
			self.volume = volume
			self.updateVolume = True

		# playlistlength
		if self.playlistlength != playlistlength:
			self.playlistlength = playlistlength
			self.updateTrackInfo = True

		# audiorate
		if self.audiorate != audiorate:
			self.audiorate = audiorate
			self.updateTrackInfo = True

		# fileext
		if self.fileext != fileext:
			self.fileext = fileext
			self.updateTrackInfo = True

		# playlistpos
		if self.playlistpos != playlistpos:
			self.playlistpos = playlistpos
			self.updateTrackInfo = True

		# Sleeptimer
		if self.sleepTimer:
			td = self.sleepTimer - datetime.datetime.now()
			if self.sleepTimer > datetime.datetime.now():
				sleepTimerText = str(int(td.total_seconds() / 60))
				if self.sleepTimerText != sleepTimerText:
					self.sleepTimerText = sleepTimerText
					self.updateSleepTimer = True
			else:

				self.sleepTimerText = "OFF"
				self.sleepTimer = None
				self.updateSleepTimer = True
				self.sleepThread = Thread(target=self.sleep)
				self.sleepThread.start()


	def renderlibrarylist_albumartist(self, surface, i):

		# show album on on library list

		surface.blit(self.image["background"], (0,0))

		self.logger.debug("Show current library-list Album art")

		self.currentPage = 0
		self.maxInView = 7
		self.currentSong = i
		songList = []
		self.touchList = {}

		highlight_text = 130,227,127
		normal_text = 230,228,227
		track_bar_width = 355

		curr_URL = config.URL [len(config.URL)-1]
		self.logger.debug("Current directory: %s" % curr_URL)

		self.lib_dir = self.mpdc.lsinfo(curr_URL)

		#add_folder = self.lib_dir[1]['directory']
		#self.mpdc.add(add_folder)
		
		#for entry in self.mpdc.lsinfo(curr_URL):
		#   self.logger.debug("%s" % entry)
		#for key, value in self.mpdc.status().items():
 		#   self.logger.debug("%s: %s" % (key, value))
  
		config.folder_items = int(len(self.lib_dir))

		y =27
		exitLoop = False

		# draw buttons
		#rect(Surface, color, Rect, width)
		surface.blit(self.image["homescreen_icon"], (430, 20)) # back to main screen
		#surface.blit(self.image["arrowaup_icon"], (430, 20)) # scroll up 1
		#surface.blit(self.image["arrowdown_icon"], (430, 260)) # scroll down 1
		surface.blit(self.image["backfolder_icon"], (430, 250)) # prev directory
		#surface.blit(self.image["pageup_icon"], (430, 70)) # scroll up 7
		#surface.blit(self.image["pagedown_icon"], (430, 200)) # scroll down 7

		#currenti = int(config.i)	
		currenti = config.libi[len(config.libi)-1]

		self.logger.info("Currenti self.currentSong: %s %s" % (currenti,self.currentSong))

		showNum = 0
		highlight_selected = False

		if currenti + 7 > config.folder_items:
			currenti = config.folder_items - 7
			if currenti < 0:
				currenti =0
			config.libi[len(config.libi)-1] = currenti

		#config.key_library_selected = currenti

		#tracklimit = int(playlisttracks_count)

		#self.logger.debug("playlist length - currenti %s %s" % (playlisttracks_count,currenti))
		
		self.logger.debug("Library-list number currenti key_selected %s %s %s %s" % (config.folder_items,currenti,curr_URL,config.key_library_selected))
 
		text = self.font["details_sm"].render(str(config.folder_items) +":"+str(curr_URL),1,normal_text,(0,0,0))
		surface.blit(text, (10, 8)) # directory info

		# draw scroll bar
		pygame.draw.line(surface, (25,25,25), (412, 23), (412, 301), 15)
		# calculate length and start pos of position indicator

		scroll_start = 0
		scroll_length = 0
		scroll_bar_percent = 0

		if config.folder_items < 8:
			scroll_start = 0
			scroll_length = 278
			scroll_bar_percent = 1.0
		else:
			scroll_bar_percent = round((7. / config.folder_items),2)
			scroll_length = int(scroll_bar_percent * 278)
			#int(config.key_track_selected)+ config.i
			scroll_page_top_track = currenti # starts at 0
			scroll_px_per_track = 278. / config.folder_items
			scroll_start = int(scroll_page_top_track * scroll_px_per_track)

		self.logger.debug("scrollbar percent length start %s %s %s" % (scroll_bar_percent,scroll_length,scroll_start))

		pygame.draw.line(surface, (80,80,80), (412, scroll_start+23), (412, scroll_length+23+scroll_start), 15)

		while not exitLoop and currenti < config.folder_items:

			self.logger.debug("In library-list loop %s" % currenti)

			# set text color for remote key highighted item
			text_color = normal_text
			if int(currenti) == int(config.libi[len(config.libi)-1]) + int(config.key_library_selected[len(config.key_library_selected)-1]):
				#text_color = highlight_text
				highlight_selected = True
			else:
				#text_color = normal_text
				highlight_selected = False

			# show file/folder
			try:
				# strip current config.url from 'directory' value
				directory_entry = str(self.lib_dir[currenti]['directory'])
				#self.logger.debug("directory/curr.URL replace '%s' - '%s'" % (directory_entry,curr_URL))
				disp_URL = str(curr_URL + "/")
				display_directory_entry = directory_entry.replace(disp_URL,"")

				self.logger.info("before Album art thread %s" %  display_directory_entry)

				# show Album art of folder
				#if self.oldCoverartThreadRunning:
				self.logger.info("Album if")
				#self.album = album
				#self.updateAlbum = True
				self.cover = False
				# Find cover art on different thread
				try:
					if self.coverartThread:
						self.logger.info("if caT")
						if self.coverartThread.is_alive():
							self.logger.info("caT is alive")
							self.oldCoverartThreadRunning = True
						else:
							self.logger.info("caT not live")
							self.oldCoverartThreadRunning = False
							self.coverartThread = Thread(target=self.fetch_coverart_library)
							self.logger.info("caT go")
							self.coverartThread.start()
					else:
						self.logger.info("not caT")
						self.coverartThread = Thread(target=self.fetch_coverart_library)
						self.coverartThread.start()
				except Exception, e:
					self.logger.info("Coverartthread: %s" % e)
					self.processingCover = False

				if self.coverFetched:
					if self.cover:
						surface.blit(self.image["cover"], (0,y))
						self.coverFetched = False
					else:
						surface.blit(self.image["nocover"], (0,y))
				#surface.blit(self.image["folder_icon"], (0,y)) # show folder icon
	
				tracktitletextsize = self.font["tracktitle_sm"].size(display_directory_entry)
				textwidth_dir_name = tracktitletextsize[0]
				if textwidth_dir_name > 400:
					# only show 50 chars on line
					short_directory_text = display_directory_entry[:40]
					text = self.font["tracktitle_sm"].render(short_directory_text, 1,text_color,(40,40,40))
				else:
					text = self.font["tracktitle_sm"].render(display_directory_entry, 1,text_color,(40,40,40))

				pygame.draw.rect(surface, (40,40,40), [40, y-3, track_bar_width, 38], 0)

				surface.blit(text, (45, y)) # directory

				text = self.font["details_sm"].render(str(currenti+1),1,text_color,(0,0,0))
				#textwidth = text[0]
				surface.blit(text, (18, y+17)) # directory number

				pygame.draw.line(surface, (0,0,0), (40, y-4), (track_bar_width, y-4), 1)

 				if highlight_selected == True:
 					# draw selection box
 					pygame.draw.rect(surface, (227,227,230), [40, y-3, track_bar_width, 38], 1)

				current = Text_Control().changeText(('DIR'+str(showNum)), self.lib_dir[currenti]['directory'], 0, y,-1,surface,self.font["tracktitle_sm"])
				config.click_URI[currenti] = self.lib_dir[currenti]['directory']

			except:
				surface.blit(self.image["music_icon"], (0, y)) # show music icon
				library_track_time = 0
				try:
					library_raw_title = self.lib_dir[currenti]['title']
					library_track_time = self.convert_time(self.lib_dir[currenti]['time'])
					config.click_URI[currenti] = self.lib_dir[currenti]['file']

				except:
					try:
						library_raw_title2 = self.lib_dir[currenti]['file']
						disp_URL = str(curr_URL + "/")
						library_raw_title = library_raw_title2.replace(disp_URL,"")
					except:
						try:
							library_raw_title2 = self.lib_dir[currenti]['playlist']
							disp_URL = str(curr_URL + "/")
							library_raw_title = library_raw_title2.replace(disp_URL,"")
							config.click_URI[currenti] = self.lib_dir[currenti]['playlist']

						except:
							library_raw_title = "unknown"

				self.logger.debug("track time %s" % library_track_time)
				#if library_track_time == 0:
				#	tracktitletextsize = self.font["tracktitle_sm"].size(str(currenti+1) + ". " +  library_raw_title)
				#else:
				#	tracktitletextsize = self.font["tracktitle_sm"].size(str(currenti+1) + ". " +  library_raw_title + " " + str(library_track_time))
				library_title = str(currenti+1) + ". " + library_raw_title
				text = self.font["tracktitle_sm"].render(str(library_title), 1,text_color,(40,40,40))
				tracktitletextsize = self.font["tracktitle_sm"].size(str(library_title))
				textwidth_lib_title = tracktitletextsize[0]
				if textwidth_lib_title > 380:
					library_title = library_title[:40]
					tracktitletextsize = self.font["tracktitle_sm"].size(library_title)
					textwidth_lib_title = tracktitletextsize[0]
					text = self.font["tracktitle_sm"].render(library_title, 1,text_color,(40,40,40))

				#else:
				#	text = self.font["tracktitle_sm"].render(str(currenti+1) + ". " +  str(library_raw_title), 1,(230,228,227),(0,0,0))
				#	tracktitletextsize = self.font["tracktitle_sm"].size(short_library_text)
				#	textwidth_title = tracktitletextsize[0]
				text_track_time = self.font["field"].render(str(library_track_time), 1,(200,230,200),(40,40,40))

				try:
					library_raw_album = self.lib_dir[currenti]['album']
					library_raw_artist = self.lib_dir[currenti]['artist']

				except:
					library_raw_album = "unknown"
					library_raw_artist = "unknown"

				trackalbumtextsize = self.font["tracktitle_sm"].size(library_raw_album+" - "+library_raw_artist)
				textwidth = trackalbumtextsize[0]
				if textwidth > 420:
					library_trackalbum = library_raw_album+" - "+library_raw_artist
					short_trackalbum_text = library_trackalbum[:60]
					text2 = self.font["details_sm"].render(short_trackalbum_text, 1,(200,200,230),(40,40,40))
				else:
					text2 = self.font["details_sm"].render(library_raw_album+" - "+library_raw_artist, 1,(200,200,230),(40,40,40))

				pygame.draw.rect(surface, (40,40,40), [40, y-3, track_bar_width, 38], 0)

				surface.blit(text, (45, y)) # Title
				if library_track_time <> 0:
					librarytimetextsize = self.font["field"].size(str(library_track_time))
					surface.blit(text_track_time, (track_bar_width-librarytimetextsize[0]+35, y)) # TrackTime
					#surface.blit(text_track_time, (55 + textwidth_lib_title, y)) # Track time

				surface.blit(text2, (45, y+20)) # album - artist
				# add track ID
				# config.click_URI[currenti] = self.lib_dir[currenti]['directory']

				pygame.draw.line(surface, (0,0,0), (40, y-4), (track_bar_width, y-4), 1)

	 			if highlight_selected == True:
	 				# draw selection box
	 				pygame.draw.rect(surface, (227,227,230), [40, y-3, track_bar_width, 38], 1)		

				current = Text_Control().changeText(('SONG'+str(showNum)), library_raw_title, 0, y,-1,surface,self.font["tracktitle_sm"])


			self.logger.debug("track/dir %s %s" % (currenti,y))
		

			if (current.get_rect().height+y < surface.get_height()):
				songList.append(current)
				self.touchList[('DIR'+str(showNum))] = pygame.Rect(0,y,songList[showNum].get_rect().width,songList[showNum].get_rect().height)
				y = y + songList[showNum].get_height() + 15
				currenti = currenti +1
				#config.libi[len(config.libi)-1]  = config.libi[len(config.libi)-1] + 1 
				showNum = showNum +1
			else:
				self.maxInView = currenti - self.currentSong
				exitLoop = True

		self.updateAll = True


	def renderlibrarylist(self, surface, i):

		surface.blit(self.image["background"], (0,0))

		self.logger.debug("Show current library-list")

		self.currentPage = 0
		self.maxInView = 7
		self.currentSong = i
		songList = []
		self.touchList = {}

		highlight_text = 130,227,127
		normal_text = 230,228,227
		track_bar_width = 355

		curr_URL = config.URL [len(config.URL)-1]
		self.logger.debug("Current directory: %s" % curr_URL)

		self.lib_dir = self.mpdc.lsinfo(curr_URL)

		#add_folder = self.lib_dir[1]['directory']
		#self.mpdc.add(add_folder)
		
		#for entry in self.mpdc.lsinfo(curr_URL):
		#   self.logger.debug("%s" % entry)
		#for key, value in self.mpdc.status().items():
 		#   self.logger.debug("%s: %s" % (key, value))
  
		config.folder_items = int(len(self.lib_dir))

		y =27
		exitLoop = False

		# draw buttons
		#rect(Surface, color, Rect, width)
		surface.blit(self.image["homescreen_icon"], (430, 20)) # back to main screen
		#surface.blit(self.image["arrowaup_icon"], (430, 20)) # scroll up 1
		#surface.blit(self.image["arrowdown_icon"], (430, 260)) # scroll down 1
		surface.blit(self.image["backfolder_icon"], (430, 250)) # prev directory
		#surface.blit(self.image["pageup_icon"], (430, 70)) # scroll up 7
		#surface.blit(self.image["pagedown_icon"], (430, 200)) # scroll down 7

		#currenti = int(config.i)	
		currenti = config.libi[len(config.libi)-1]

		showNum = 0
		highlight_selected = False

		if currenti + 7 > config.folder_items:
			currenti = config.folder_items - 7
			if currenti < 0:
				currenti =0
			config.libi[len(config.libi)-1] = currenti

		#config.key_library_selected = currenti

		#tracklimit = int(playlisttracks_count)

		#self.logger.debug("playlist length - currenti %s %s" % (playlisttracks_count,currenti))
		
		self.logger.debug("Library-list number currenti key_selected %s %s %s %s" % (config.folder_items,currenti,curr_URL,config.key_library_selected))
 
		text = self.font["details_sm"].render(str(config.folder_items) +":"+str(curr_URL),1,normal_text,(0,0,0))
		surface.blit(text, (10, 8)) # directory info

		# draw scroll bar
		pygame.draw.line(surface, (25,25,25), (412, 23), (412, 301), 15)
		# calculate length and start pos of position indicator

		scroll_start = 0
		scroll_length = 0
		scroll_bar_percent = 0

		if config.folder_items < 8:
			scroll_start = 0
			scroll_length = 278
			scroll_bar_percent = 1.0
		else:
			scroll_bar_percent = round((7. / config.folder_items),2)
			scroll_length = int(scroll_bar_percent * 278)
			#int(config.key_track_selected)+ config.i
			scroll_page_top_track = currenti # starts at 0
			scroll_px_per_track = 278. / config.folder_items
			scroll_start = int(scroll_page_top_track * scroll_px_per_track)

		self.logger.debug("scrollbar percent length start %s %s %s" % (scroll_bar_percent,scroll_length,scroll_start))

		pygame.draw.line(surface, (80,80,80), (412, scroll_start+23), (412, scroll_length+23+scroll_start), 15)

		while not exitLoop and currenti < config.folder_items:

			self.logger.debug("In library-list loop %s" % currenti)

			# set text color for remote key highighted item
			text_color = normal_text
			if int(currenti) == int(config.libi[len(config.libi)-1]) + int(config.key_library_selected[len(config.key_library_selected)-1]):
				#text_color = highlight_text
				highlight_selected = True
			else:
				#text_color = normal_text
				highlight_selected = False

			# show file/folder
			try:
				# strip current config.url from 'directory' value
				directory_entry = str(self.lib_dir[currenti]['directory'])
				#self.logger.debug("directory/curr.URL replace '%s' - '%s'" % (directory_entry,curr_URL))
				disp_URL = str(curr_URL + "/")
				display_directory_entry = directory_entry.replace(disp_URL,"")

				surface.blit(self.image["folder_icon"], (0,y)) # show folder icon
	
				tracktitletextsize = self.font["tracktitle_sm"].size(display_directory_entry)
				textwidth_dir_name = tracktitletextsize[0]
				if textwidth_dir_name > 400:
					# only show 50 chars on line
					short_directory_text = display_directory_entry[:40]
					text = self.font["tracktitle_sm"].render(short_directory_text, 1,text_color,(40,40,40))
				else:
					text = self.font["tracktitle_sm"].render(display_directory_entry, 1,text_color,(40,40,40))

				pygame.draw.rect(surface, (40,40,40), [40, y-3, track_bar_width, 38], 0)

				surface.blit(text, (45, y)) # directory

				text = self.font["details_sm"].render(str(currenti+1),1,text_color,(0,0,0))
				#textwidth = text[0]
				surface.blit(text, (18, y+17)) # directory number

				pygame.draw.line(surface, (0,0,0), (40, y-4), (track_bar_width, y-4), 1)

 				if highlight_selected == True:
 					# draw selection box
 					pygame.draw.rect(surface, (227,227,230), [40, y-3, track_bar_width, 38], 1)

				current = Text_Control().changeText(('DIR'+str(showNum)), self.lib_dir[currenti]['directory'], 0, y,-1,surface,self.font["tracktitle_sm"])
				config.click_URI[currenti] = self.lib_dir[currenti]['directory']

			except:
				surface.blit(self.image["music_icon"], (0, y)) # show music icon
				library_track_time = 0
				try:
					library_raw_title = self.lib_dir[currenti]['title']
					library_track_time = self.convert_time(self.lib_dir[currenti]['time'])
					config.click_URI[currenti] = self.lib_dir[currenti]['file']

				except:
					try:
						library_raw_title2 = self.lib_dir[currenti]['file']
						disp_URL = str(curr_URL + "/")
						library_raw_title = library_raw_title2.replace(disp_URL,"")
					except:
						try:
							library_raw_title2 = self.lib_dir[currenti]['playlist']
							disp_URL = str(curr_URL + "/")
							library_raw_title = library_raw_title2.replace(disp_URL,"")
							config.click_URI[currenti] = self.lib_dir[currenti]['playlist']

						except:
							library_raw_title = "unknown"

				self.logger.debug("track time %s" % library_track_time)
				#if library_track_time == 0:
				#	tracktitletextsize = self.font["tracktitle_sm"].size(str(currenti+1) + ". " +  library_raw_title)
				#else:
				#	tracktitletextsize = self.font["tracktitle_sm"].size(str(currenti+1) + ". " +  library_raw_title + " " + str(library_track_time))
				library_title = str(currenti+1) + ". " + library_raw_title
				text = self.font["tracktitle_sm"].render(str(library_title), 1,text_color,(40,40,40))
				tracktitletextsize = self.font["tracktitle_sm"].size(str(library_title))
				textwidth_lib_title = tracktitletextsize[0]
				if textwidth_lib_title > 380:
					library_title = library_title[:40]
					tracktitletextsize = self.font["tracktitle_sm"].size(library_title)
					textwidth_lib_title = tracktitletextsize[0]
					text = self.font["tracktitle_sm"].render(library_title, 1,text_color,(40,40,40))

				#else:
				#	text = self.font["tracktitle_sm"].render(str(currenti+1) + ". " +  str(library_raw_title), 1,(230,228,227),(0,0,0))
				#	tracktitletextsize = self.font["tracktitle_sm"].size(short_library_text)
				#	textwidth_title = tracktitletextsize[0]
				text_track_time = self.font["field"].render(str(library_track_time), 1,(200,230,200),(40,40,40))

				try:
					library_raw_album = self.lib_dir[currenti]['album']
					library_raw_artist = self.lib_dir[currenti]['artist']

				except:
					library_raw_album = "unknown"
					library_raw_artist = "unknown"

				trackalbumtextsize = self.font["tracktitle_sm"].size(library_raw_album+" - "+library_raw_artist)
				textwidth = trackalbumtextsize[0]
				if textwidth > 420:
					library_trackalbum = library_raw_album+" - "+library_raw_artist
					short_trackalbum_text = library_trackalbum[:60]
					text2 = self.font["details_sm"].render(short_trackalbum_text, 1,(200,200,230),(40,40,40))
				else:
					text2 = self.font["details_sm"].render(library_raw_album+" - "+library_raw_artist, 1,(200,200,230),(40,40,40))

				pygame.draw.rect(surface, (40,40,40), [40, y-3, track_bar_width, 38], 0)

				surface.blit(text, (45, y)) # Title
				if library_track_time <> 0:
					librarytimetextsize = self.font["field"].size(str(library_track_time))
					surface.blit(text_track_time, (track_bar_width-librarytimetextsize[0]+35, y)) # TrackTime
					#surface.blit(text_track_time, (55 + textwidth_lib_title, y)) # Track time

				surface.blit(text2, (45, y+20)) # album - artist
				# add track ID
				# config.click_URI[currenti] = self.lib_dir[currenti]['directory']

				pygame.draw.line(surface, (0,0,0), (40, y-4), (track_bar_width, y-4), 1)

	 			if highlight_selected == True:
	 				# draw selection box
	 				pygame.draw.rect(surface, (227,227,230), [40, y-3, track_bar_width, 38], 1)		

				current = Text_Control().changeText(('SONG'+str(showNum)), library_raw_title, 0, y,-1,surface,self.font["tracktitle_sm"])


			self.logger.debug("track/dir %s %s" % (currenti,y))
		

			if (current.get_rect().height+y < surface.get_height()):
				songList.append(current)
				self.touchList[('DIR'+str(showNum))] = pygame.Rect(0,y,songList[showNum].get_rect().width,songList[showNum].get_rect().height)
				y = y + songList[showNum].get_height() + 15
				currenti = currenti +1
				#config.libi[len(config.libi)-1]  = config.libi[len(config.libi)-1] + 1 
				showNum = showNum +1
			else:
				self.maxInView = currenti - self.currentSong
				exitLoop = True

		self.updateAll = True

	
	def renderplaylist(self, surface, i):

		#global i

		surface.blit(self.image["background"], (0,0))
		#text = self.font["tracktitle"].render("playlist screen", 1,(230,228,227),(0,0,0))
		#surface.blit(text, (10, 15)) # Title

		#self.songs = self.client.litplaylistinfo(self.playlist)
		#self.mainText = self.myfont.render('Songs in '+self.playlist, 1, [255,255,255])
		#self.mainText = self.font["details_sm"].render('Songs in ', 1, [255,255,255])
		#surface.blit(self.mainText,(10, 0))
		#surface.blit(self.mainText,(self.surface.get_width()/2-self.mainText.get_rect().width/2, 0))
		#for i in range(0,10):
		#	tc = Text_Control()
		#	tc.printKey('SONG'+str(i))


		#for entry in self.mpdc.playlist():
		#   self.logger.debug("%s" % entry)

		self.logger.debug("Show current playlist")

		self.currentPage = 0
		self.maxInView = 7
		self.currentSong = i
		songList = []
		self.touchList = {}
		#self.myfont = pygame.font.SysFont(None, 30)
		#self.mainText = self.font["details_sm"].render('Songs in Current Playlist', 1, [255,255,255])
		#self.songs = self.client.listplaylistinfo(self.playlist)
		self.songs = self.mpdc.playlistinfo()
		#y = self.mainText.get_height()
		y =27
		exitLoop = False
		track_bar_width = 355


		playlist_currenttrack = self.playlistpos
		
		if playlist_currenttrack <= 0:
			playlist_currenttrack = 1		

		playlisttracks_count = self.playlistlength
		config.curplaylistlength = int(self.playlistlength)		
		tracklimit = int(playlisttracks_count)

		self.logger.debug("playlist length - config.i  %s %s" % (playlisttracks_count,config.i))
		
		#i = self.mpdc.currentsong()

		#if i == 0:
		#	currenti = int(playlist_currenttrack) -1
		#	starttrack = currenti

		#if i == 1:
		#	#currenti = i
		#	currenti = starttrack + 1

		#elif i == -1:
		#	currenti = starttrack - 1

		#starttrack = currenti

		if config.i < 0:
			config.i = 0
		
		currenti = config.i	
		#if currenti < 0:
		#	currenti = 0

		if tracklimit <> 0:
			if currenti + 7 > tracklimit:
				currenti = tracklimit - 7
				if currenti < 0:
					currenti =0
				config.i = currenti


		showNum = 0
		#tracklimit = int(playlisttracks_count) - 1

		self.logger.debug("playlist length - currenti - tracklimit %s %s %s" % (playlisttracks_count,currenti,tracklimit))

		text = self.font["details_sm"].render("Playlist Tracks: " + str(playlisttracks_count) + "      Current Track : " + str(playlist_currenttrack), 1,(230,228,227),(0,0,0))
		surface.blit(text, (10, 10)) # Playlist Info

		surface.blit(self.image["homescreen_icon"], (430, 20)) # back to main screen
		#surface.blit(self.image["arrowaup_icon"], (430, 20)) # scroll up
		#surface.blit(self.image["arrowdown_icon"], (430, 260)) # scroll down
		surface.blit(self.image["deleteplaylist_icon"], (430, 135)) # clear playlist
		#surface.blit(self.image["pageup_icon"], (430, 70)) # scroll up 7
		#surface.blit(self.image["pagedown_icon"], (430, 200)) # scroll down 7
		surface.blit(self.image["button_settings"], (430, 250)) # clear playlist

		# scroll bar
		pygame.draw.line(surface, (25,25,25), (412, 23), (412, 301), 15)
		# calculate length and start pos of position indicator

		scroll_start = 0
		scroll_length = 0
		scroll_bar_percent = 0

		if tracklimit < 8:
			scroll_start = 0
			scroll_length = 278
			scroll_bar_percent = 1.0
		else:
			scroll_bar_percent = round((7. / tracklimit),2)
			scroll_length = int(scroll_bar_percent * 278)
			#int(config.key_track_selected)+ config.i
			scroll_page_top_track = config.i # starts at 0
			scroll_px_per_track = 278. / tracklimit
			scroll_start = int(scroll_page_top_track * scroll_px_per_track)


		self.logger.debug("scrollbar percent length start %s %s %s" % (scroll_bar_percent,scroll_length,scroll_start))

		pygame.draw.line(surface, (80,80,80), (412, scroll_start+23), (412, scroll_length+23+scroll_start), 15)

		#while not exitLoop and i < self.getMax():
		while not exitLoop and currenti < tracklimit:

			self.logger.debug("start loop - show track titles currenti tracklimit %s %s" % (currenti,tracklimit))

			if config.key_track_selected > tracklimit-1:
				config.key_track_selected = tracklimit-1

			surface.blit(self.image["deleteplaylist_sm_icon"], (10, y+3)) # show track trash icon
			try:
				playlist_track_time = self.convert_time(self.songs[currenti]['time'])
			except:
				playlist_track_time = "0:00" # set default time for 0 tracklimit

			try:
				track_title_string = str(currenti+1) + ". " +  self.songs[currenti]['title']
			except:
				try:
					track_title_string = str(currenti+1) + ". " +  self.songs[currenti]['file']
				except:
					track_title_string = "" # set default title for 0 tracklimit

			self.logger.debug("in loop - after get track title")

			tracktitletextsize = self.font["tracktitle_sm"].size(track_title_string)
			textwidth_title = tracktitletextsize[0]
			if textwidth_title > 380:
				track_title_string = track_title_string[:38]
				tracktitletextsize = self.font["tracktitle_sm"].size(track_title_string)
				textwidth_title = tracktitletextsize[0]

			#current = Text_Control().changeText(('SONG'+str(showNum)), self.songs[i]['title']+'-'+self.songs[i]['artist'], 0, y,-1,self.surface,self.myfont)
			self.logger.debug("in loop currenti tracklimit playlist_currenttrack %s %s %s" % (currenti,tracklimit,str(playlist_currenttrack)))
			
			if int(currenti) == int(playlist_currenttrack) -1:
				text = self.font["tracktitle_sm"].render(track_title_string, 1,(130,128,227),(40,40,40))
			else:
				text = self.font["tracktitle_sm"].render(track_title_string, 1,(230,228,227),(40,40,40))
			#text_track_time = self.font["details_sm"].render(str(playlist_track_time), 1,(200,230,200),(0,0,0))

 			#if int(currenti) == int(config.key_track_selected)+ config.i:
			#	text = self.font["tracktitle_sm"].render(track_title_string, 1,(130,227,127),(0,0,0))

			text_track_time = self.font["field"].render(str(playlist_track_time), 1,(200,230,200),(40,40,40))

			try:
				track_details = self.songs[currenti]['album']+" - "+self.songs[currenti]['artist']	
			except:
				track_details = "Unknown"

			trackdetailstextsize = self.font["details_sm"].size(track_details)
			textwidth_details = trackdetailstextsize[0]
			if textwidth_details > 380:
				track_details = track_details[:60]

			text2 = self.font["details_sm"].render(track_details, 1,(200,200,230),(40,40,40))

			pygame.draw.rect(surface, (40,40,40), [40, y-3, track_bar_width, 38], 0)

			#ypos = 10 + (i * y)
			surface.blit(text, (45, y)) # Title
			#surface.blit(text_track_time, (55 +textwidth_title, y)) # TrackTime

			tracktimetextsize = self.font["field"].size(str(playlist_track_time))
			#surface.blit(text_track_time, (400-tracktimetextsize[0], y)) # TrackTime
			surface.blit(text_track_time, (track_bar_width-tracktimetextsize[0]+35, y)) # TrackTime

			surface.blit(text2, (45, y+20)) # track details

			pygame.draw.line(surface, (0,0,0), (40, y-4), (track_bar_width, y-4), 1)

 			if int(currenti) == int(config.key_track_selected)+ config.i:
 				# draw selection box
 				pygame.draw.rect(surface, (227,227,230), [40, y-3, track_bar_width, 38], 1)

			self.logger.debug("track %s %s" % (currenti,y))
			#self.logger.debug("ypos %s" % ypos)

			#current = Text_Control().changeText(('SONG'+str(showNum)), self.songs[currenti]['title']+'-'+self.songs[currenti]['artist'], 0, y,-1,surface,self.font["tracktitle_sm"])
			current = Text_Control().changeText(('SONG'+str(showNum)), track_title_string, 0, y,-1,surface,self.font["tracktitle_sm"])

			#if (current.get_rect().height+y < self.surface.get_height()):
			if (current.get_rect().height+y < surface.get_height()):
				songList.append(current)
				self.logger.debug("track txt height %s" % songList[showNum].get_height())
				self.touchList[('SONG'+str(showNum))] = pygame.Rect(0,y,songList[showNum].get_rect().width,songList[showNum].get_rect().height)
				self.logger.debug("track txt after height")
				y = y + songList[showNum].get_height() + 15
				self.logger.debug("track txt after Y height calc")
				#if currenti < int(self.playlistlength)-1:
				currenti = currenti +1
				showNum = showNum +1
			else:
				self.maxInView = currenti - self.currentSong
				exitLoop = True

		self.updateAll = True

	def render_settings(self, surface):
		if self.updateAll:
			self.updateTrackInfo = True
			self.updateAlbum	 = True	
			self.updateElapsed	 = True
			self.updateRandom	 = True
			self.updateRepeat	 = True
			self.updateConsume   = True
			self.updateSingle    = True			
			self.updateVolume	 = True
			self.updateState	 = True
				
			self.updateSleepTimer= True

		surface.blit(self.image["background"], (0,0))	

		surface.blit(self.image["homescreen_icon"], (430, 20)) # back to main screen
		surface.blit(self.image["playlist_icon"], (430, 260)) # back to playlist
		surface.blit(self.image["button_single"], (430,135))
		#surface.blit(self.image["indicator_blue"], (357, 136))
		text = self.font["details_sm"].render("library", 1,(230,228,227),(0,0,0))
		surface.blit(text, (438, 190)) # refresh library


		self.logger.debug("Show settings")

		if self.updateRepeat:
			if not self.updateAll:
				surface.blit(self.image["background"], (215,0), (215,0, 105,31)) # reset background

			if self.repeat == 1:
				surface.blit(self.image["button_repeat"], (195,55))
				#surface.blit(self.image["indicator_blue"], (190, 110))
				text = self.font["details_sm"].render("repeat", 1,(130,128,227),(0,0,0))
				surface.blit(text, (202, 110)) # repeat

			else:
				surface.blit(self.image["button_repeat"], (195,55))
				#surface.blit(self.image["indicator_red"], (190, 110))
				text = self.font["details_sm"].render("repeat", 1,(230,228,227),(0,0,0))
				surface.blit(text, (202, 110)) # repeat

		if self.updateRandom:
			if not self.updateAll:
				surface.blit(self.image["background"], (215,33), (215,33, 105,31)) # reset background

			if self.random == 1:
				surface.blit(self.image["button_random"], (82,135))
				#surface.blit(self.image["indicator_blue"], (142, 136))
				text = self.font["details_sm"].render("random", 1,(130,128,227),(0,0,0))
				surface.blit(text, (84, 192)) # random

			else:
				surface.blit(self.image["button_random"], (82,135))
				#surface.blit(self.image["indicator_red"], (142, 136))
				text = self.font["details_sm"].render("random", 1,(230,228,227),(0,0,0))
				surface.blit(text, (84, 192)) # random

		if self.updateConsume:
			if not self.updateAll:
				surface.blit(self.image["background"], (215,33), (215,33, 105,31)) # reset background

			if self.consume == 1:
				surface.blit(self.image["deleteplaylist_icon"], (195,215))
				#surface.blit(self.image["indicator_blue"], (255, 216))
				text = self.font["details_sm"].render("consume", 1,(130,128,227),(0,0,0))
				surface.blit(text, (197, 270)) # consume
			else:
				surface.blit(self.image["deleteplaylist_icon"], (195,215))
				#surface.blit(self.image["indicator_red"], (255, 216))
				text = self.font["details_sm"].render("consume", 1,(230,228,227),(0,0,0))
				surface.blit(text, (197, 270)) # consume

		if self.updateSingle:
			if not self.updateAll:
				surface.blit(self.image["background"], (215,33), (215,33, 105,31)) # reset background

			if self.single == 1:
				surface.blit(self.image["button_single"], (297,135))
				#surface.blit(self.image["indicator_blue"], (357, 136))
				text = self.font["details_sm"].render("single", 1,(130,128,227),(0,0,0))
				surface.blit(text, (305, 190)) # single
			else:
				surface.blit(self.image["button_single"], (297,135))
				#surface.blit(self.image["indicator_red"], (357, 136))
				text = self.font["details_sm"].render("single", 1,(230,228,227),(0,0,0))
				surface.blit(text, (305, 190)) # single

		# Reset updates
		#self.resetUpdates()
		self.updateAll = True


	def render(self, surface):
		if self.updateAll:
			self.updateTrackInfo = True
			self.updateAlbum	 = True	
			self.updateElapsed	 = True
			self.updateRandom	 = True
			self.updateRepeat	 = True
			self.updateConsume   = True
			self.updateSingle    = True			
			self.updateVolume	 = True
			self.updateState	 = True
			#	self.updatePlaylistlength 	 = True
			#	self.updateAudiorate	 = True
			#	self.updateFileext	 = True
			#	self.updatePlaylistpos   = True
				
			self.updateSleepTimer= True

			#for entry in self.mpdc.lsinfo("USB"):
			#    self.logger.debug("%s" % entry)
			#for key, value in self.mpdc.status().items():
 			#	self.logger.debug("%s: %s" % (key, value))

			
			surface.blit(self.image["background"], (0,0))	
			# surface.blit(self.image["coverart_place"], (10,80))
			# surface.blit(self.image["details"], (6, 209))
			#	surface.blit(self.image["icon_randomandrepeat"], (360,260))
			#	surface.blit(self.image["icon_randomandrepeat"], (20,290))
			surface.blit(self.image["position_bg"], (10,282))
			#	surface.blit(self.image["button_volumeminus"], (188, 65))
			#	surface.blit(self.image["button_volumeplus"], (281, 65))
			#	surface.blit(self.image["button_timeminus"], (188, 103))
			#	surface.blit(self.image["button_timeplus"], (281, 103))
			surface.blit(self.image["button_prev"], (250, 145))
			surface.blit(self.image["button_next"], (390, 146))
			surface.blit(self.image["icon_screenoff"], (455, 270))

			config.i = int(self.playlistpos) -1
			config.curplaylistlength = int(self.playlistlength)			

		#for entry in self.mpdc.lsinfo(curr_URL):
		#   self.logger.debug("%s" % entry)
		#for key, value in self.mpdc.status().items():
 		#   self.logger.debug("%s: %s" % (key, value))
		#for key, value in self.mpdc.currentsong().items():
 		#  self.logger.debug("%s: %s" % (key, value))

		if self.updateAlbum or self.coverFetched:
			if self.cover:
				surface.blit(self.image["cover"], (10,78))
				self.coverFetched = False
			else:
				surface.blit(self.image["nocover"], (10,78))
			
		if self.updateTrackInfo:
			if not self.updateAll:
				surface.blit(self.image["background"], (10,10), (10,10, 470,70)) # reset background track text
				# surface.blit(self.image["details"], (6, 279))
				surface.blit(self.image["position_bg"], (10, 282))
				surface.blit(self.image["icon_screenoff"], (455, 270))	# redraw screenoff icon
				#surface.blit(self.image["background"], (200,303), (200,303,120,25)) # reset background track data	
				surface.blit(self.image["background"], (100,303), (100,303,250,35)) # reset background track data  & length
                                                  

			#print audioratechoices
			#currentaudiorate = audiorates["44100:16:2"]
			#currentaudiorate = audiorates['self.audiorate']


			
			if self.audiorate == "44100:16:2":
				audioratetext = "44.1kHz/16bit"
			elif self.audiorate == "48000:16:2":
				audioratetext = "48kHz/16bit"
			elif self.audiorate == "96000:16:2":
				audioratetext = "96kHz/16bit"
			elif self.audiorate == "192000:16:2":
				audioratetext = "192kHz/16bit"				
			elif self.audiorate == "44100:24:2":
				audioratetext = "44.1kHz/24bit"
			elif self.audiorate == "48000:24:2":
				audioratetext = "48kHz/24bit"
			elif self.audiorate == "96000:24:2":
				audioratetext = "96kHz/24bit"
			elif self.audiorate == "192000:24:2":
				audioratetext = "192kHz/24bit"
			elif self.audiorate == "44100:32:2":
				audioratetext = "44.1kHz/32bit"
			elif self.audiorate == "48000:32:2":
				audioratetext = "48kHz/32bit"
			elif self.audiorate == "96000:32:2":
				audioratetext = "96kHz/32bit"
			elif self.audiorate == "192000:32:2":
				audioratetext = "192kHz/32bit"
			else:
				audioratetext = self.audiorate

			curplaylistpos = str(self.playlistpos)
			curplaylistlength = str(self.playlistlength)
			#curplaylistpos = "1"
			#text = self.font["details_sm"].render(curplaylistpos + "/" + self.playlistlength + "       " + audioratetext,1,(230,228,227),(0,0,0))

			track_fileext = self.fileext.upper()
			self.logger.debug("Track upper.fileext %s" % track_fileext)

			isflac = track_fileext.count(".FLAC")
			ismp3 =  track_fileext.count(".MP3")
			iswav =  track_fileext.count(".WAV")
			ism4a =  track_fileext.count(".M4A")
			filetype = "???"
			if isflac > 0:
				filetype = "FLAC"
			if ismp3 > 0:
				filetype = "MP3"
			if iswav > 0:
				filetype = "WAV"
			if ism4a > 0:
				filetype = "M4A"

			#text = self.font["details"].render("Track    " + self.playlistpos + "/" + self.playlistlength,1,(230,228,227))
			#surface.blit(text, (215,220))
			#text = self.font["details"].render(self.playlistpos,1,(230,228,227))
			#surface.blit(text, (300,120)) # playlistpos
			#text = self.font["details"].render("/",1,(230,228,227))
			#surface.blit(text, (315,120))
			#text = self.font["details"].render(self.playlistlength,1,(230,228,227))
			#surface.blit(text, (325,120)) # playlistlength
			#text = self.font["field"].render(self.fileext, 1,(230,228,227))
			#surface.blit(text, (225,235)) # mp3/flac

			# calculate text width & use tracktitle_sm if too long
			self.logger.debug("Ttitle size start")

			tracktitletextsize = self.font["tracktitle"].size(self.title)
			textwidth = tracktitletextsize[0]
			#textwidth = 300
			#self.logger.debug("Ttitle width " + textwidth)

			if textwidth > 400:
				# use small font
				text = self.font["tracktitle_sm"].render(self.title, 1,(230,228,227),(0,0,0))
			else:
				# use regular font
				text = self.font["tracktitle"].render(self.title, 1,(230,228,227),(0,0,0))
			surface.blit(text, (10, 15)) # Title
			self.logger.debug("Ttitle size end")


			# calculate text width & use field_sm if too long
			self.logger.debug("Talbum size start")

			artisttextsize = self.font["field"].size(self.artist + " - " + self.album)
			textwidth = artisttextsize[0]
			#textwidth = 300
			#self.logger.debug("Talbum width " + textwidth)

			if textwidth > 400:
				# use small font
				text = self.font["field_sm"].render(self.artist + " - " + self.album, 1,(230,228,227),(0,0,0))
			else:
				# use regular font
				text = self.font["field"].render(self.artist + " - " + self.album, 1, (230,228,227),(0,0,0))
			surface.blit(text, (10, 50)) # Artist
			self.logger.debug("Talbum size end")

			surface.blit(self.image["background"], (470,0), (470,0, 10,80)) # reset background track text
			# text = self.font["details"].render(self.album, 1,(230,228,227))
			# surface.blit(text, (10, 60)) # Album
			
			track_bitdetails = curplaylistpos + "/" + curplaylistlength + "       " + audioratetext + "  " + filetype
			track_bitdetails_width = self.font["details_sm"].size(track_bitdetails)

			text = self.font["details_sm"].render(track_bitdetails,1,(130,128,127),(0,0,0))
			surface.blit(self.image["background"], (100,303), (100,303,250,25)) # reset background audiorate	
			if curplaylistpos == "0" or curplaylistlength == "0":
				# show nothing
				surface.blit(self.image["background"], (100,303), (100,303,250,25)) # reset background audiorate	
			else:
				surface.blit(text, (240 - (track_bitdetails_width[0] / 2),303)) # audiorate

			text = self.font["details"].render(self.timeTotal, 1,(230,228,227),(0,0,0))
			surface.blit(text, (432, 300)) # Track length


		if self.updateElapsed:
			if not self.updateAll or not self.updateTrackInfo:
				surface.blit(self.image["background"], (8,298), (0,292, 80,35)) # reset background - elapsed time
				surface.blit(self.image["position_bg"], (10, 282))
			surface.blit(self.image["position_fg"], (10, 282),(0,0,int(460*self.timeElapsedPercentage),10))
			text = self.font["details"].render(self.timeElapsed, 1,(230,228,227),(0,0,0))
			surface.blit(text, (10, 300)) # Elapsed

			#if self.updateRepeat:
			#	if not self.updateAll:
			#		surface.blit(self.image["background"], (215,0), (215,0, 105,31)) # reset background

			#	if self.repeat == 1:
			#		surface.blit(self.image["button_toggle_on"], (38,288))
			#		surface.blit(self.image["indicator_blue"], (105, 289))
			#	else:
			#		surface.blit(self.image["button_toggle_off"], (38,288))
			#		surface.blit(self.image["indicator_red"], (105, 289))

			#if self.updateRandom:
			#	if not self.updateAll:
			#		surface.blit(self.image["background"], (215,33), (215,33, 105,31)) # reset background

			#	if self.random == 1:
			#		surface.blit(self.image["button_toggle_on"], (380,288))
			#		surface.blit(self.image["indicator_blue"], (445, 289))
			#	else:
			#		surface.blit(self.image["button_toggle_off"], (380,288))
			#		surface.blit(self.image["indicator_red"], (445, 289))


		# if self.updateVolume:
                                                                                                                                                                                                       			#	if not self.updateAll:
			#		surface.blit(self.image["field"], (229,70), (5,4, 44,23)) # Reset field value area
			#	else:
			#		surface.blit(self.image["field"], (226, 67)) # Draw field
			
			#	text = self.font["field"].render(str(self.volume), 1,(230,228,227))

			#	pos = 227 + (48 - text.get_width())/2
			#	surface.blit(text, (pos, 72)) # Volume

		if self.updateState:
			if not self.updateAll:
				surface.blit(self.image["background"], (305,140), (305,140, 40,43)) # reset background
			if self.playbackStatus == "play":
				surface.blit(self.image["button_pause"], (310, 135))			
			else:
				surface.blit(self.image["button_play"], (310, 135))

		# if self.updateSleepTimer:
			#	if not self.updateAll:
			#		surface.blit(self.image["field"], (229,108), (5,4, 44,23)) # Reset field value area
			#	else:
				#		surface.blit(self.image["field"], (226, 105))
			#	text = self.font["field"].render(self.sleepTimerText, 1,(230,228,227))
			#	pos = 227 + (48 - text.get_width())/2
			#	surface.blit(text, (pos, 110))
			
		# Reset updates
		self.resetUpdates()

	def resetUpdates(self):
		self.updateTrackInfo = False
		self.updateAlbum	 = False	
		self.updateElapsed	 = False
		self.updateRandom	 = False
		self.updateRepeat	 = False
		self.updateConsume	 = False
		self.updateSingle   = False		
		self.updateVolume	 = False
		self.updateState	 = False
		#		self.updatePlaylistlength	 = False
		#		self.updateAudiorate	 = False
		#		self.updateFileext	 = False
		#		self.updatePlaylistpos	 = False
		self.updateSleepTimer	 = False
		self.updateAll		 = False
		
	def fetch_coverart(self):
		self.logger.debug("caT start")
		self.processingCover = True
		self.coverFetched = False
		self.cover = False
		# try:
		#	lastfm_album = self.lfm.get_album(self.artist, self.album)
		#	self.logger.debug("caT album: %s" % lastfm_album)
		# except Exception, e:
		#	self.logger.exception(e)
		#	raise

		# if lastfm_album:
		try:
			#coverart_url = lastfm_album.get_cover_image(2)
			#self.logger.debug("caT curl: %s" % coverart_url)
			#if coverart_url:
			#self.logger.debug("caT sp start")
			#	subprocess.check_output("wget -q --limit-rate=40k %s -O %s/cover.png" % (coverart_url, "/tmp/"), shell=True )
			#self.logger.debug("caT sp end")

			# get albumart filename for ARTWORK folder
			#albumname = self.album
			#albumname = albumname.replace(chr(58)," -")
			#albumname = albumname.replace(chr(47)," -")

			# get albumart path for cover.jpg
			albumart_fullurl = self.track_URL
			# remove track filename to leave raw path
			albumart_url = os.path.dirname(albumart_fullurl)
			try:
				#self.logger.info("caT load artist/album " + "/mnt/USB/ARTWORK/" + self.artist + " - " + albumname + ".jpg")
				self.logger.info("caT load artist/album from dir " + albumart_url + "/cover.jpg")
				#coverart=pygame.image.load("/mnt/USB/ARTWORK/" + self.artist + " - " + albumname + ".jpg")
				coverart=pygame.image.load("/mnt/" + albumart_url + "/cover.jpg")
			except:
				#self.logger.info("caT load album " + "/mnt/USB/ARTWORK/" + albumname + ".jpg")
				#coverart=pygame.image.load("/mnt/USB/ARTWORK/" + albumname + ".jpg")
				self.logger.info("caT load album from dir " + "/cover.jpg")
				coverart=pygame.image.load("/mnt/" + albumart_url + "/cover.jpg")
			self.logger.debug("caT c loaded")
			self.image["cover"] = pygame.transform.scale(coverart, (200, 200))
			self.logger.debug("caT c placed")
			self.processingCover = False
			self.coverFetched = True
			self.cover = True
		except Exception, e:
			#self.logger.info("caT load album " + "/mnt/NAS/Music/ARTWORK/" + albumname + ".jpg")
			#coverart=pygame.image.load("/mnt/NAS/Music/ARTWORK/NONE - NONE.jpg")
			#self.image["cover"] = pygame.transform.scale(coverart, (200, 200))
			#self.processingCover = False
			#self.coverFetched = True
			#self.cover = True
			self.logger.exception(e)
			pass
		self.processingCover = False
		self.logger.debug("caT end")

	def fetch_coverart_library(self):
			self.logger.info("caT start")
			self.processingCover = True
			self.coverFetched = False
			self.cover = False
			# try:
			#	lastfm_album = self.lfm.get_album(self.artist, self.album)
			#	self.logger.debug("caT album: %s" % lastfm_album)
			# except Exception, e:
			#	self.logger.exception(e)
			#	raise

			# if lastfm_album:
			try:
				#coverart_url = lastfm_album.get_cover_image(2)
				#self.logger.debug("caT curl: %s" % coverart_url)
				#if coverart_url:
				#self.logger.debug("caT sp start")
				#	subprocess.check_output("wget -q --limit-rate=40k %s -O %s/cover.png" % (coverart_url, "/tmp/"), shell=True )
				#self.logger.debug("caT sp end")
				albumname = "Christ Illusion"
				artistname = "Slayer"
				albumname = albumname.replace(chr(58)," -")
				albumname = albumname.replace(chr(47)," -")
				try:
					self.logger.info("caT load artist/album " + "/mnt/USB/ARTWORK/" + artistname + " - " + albumname + ".jpg")
					coverart=pygame.image.load("/mnt/USB/ARTWORK/" + artistname + " - " + albumname + ".jpg")
				except:
					self.logger.info("caT load album " + "/mnt/USB/ARTWORK/" + albumname + ".jpg")
					coverart=pygame.image.load("/mnt/USB/ARTWORK/" + albumname + ".jpg")
				self.logger.info("caT c loaded")
				self.image["cover"] = pygame.transform.scale(coverart, (50, 50))
				self.logger.info("caT c placed")
				self.processingCover = False
				self.coverFetched = True
				self.cover = True
			except Exception, e:
				#self.logger.info("caT load album " + "/mnt/NAS/Music/ARTWORK/" + albumname + ".jpg")
				#coverart=pygame.image.load("/mnt/NAS/Music/ARTWORK/NONE - NONE.jpg")
				#self.image["cover"] = pygame.transform.scale(coverart, (200, 200))
				#self.processingCover = False
				#self.coverFetched = True
				#self.cover = True
				self.logger.exception(e)
				pass
			self.processingCover = False
			self.logger.info("caT end")


	def toggle_random(self):
		random = (self.random + 1) % 2
		self.mpdc.random(random)

	def toggle_repeat(self):
		repeat = (self.repeat + 1) % 2
		self.mpdc.repeat(repeat)

	def toggle_consume(self):
		consume = (self.consume + 1) % 2
		self.mpdc.consume(consume)

	def toggle_single(self):
		single = (self.single + 1) % 2
		self.mpdc.single(single)

	# Direction: +, -
	#def set_volume(self, amount, direction=""):
	#		if direction == "+":
	#			volume = self.volume + amount
	#		elif direction == "-":
	#			volume = self.volume - amount
	#		else:
	#			volume = amount

	#		volume = 100 if volume > 100 else volume
	#		volume = 0 if volume < 0 else volume
	#		self.mpdc.setvol(volume)

	def toggle_playback(self):
		status = self.playbackStatus
		if status == "play":
			self.mpdc.pause()
		else:
			self.mpdc.play()

	def goto_track(self,xpos):

		#seek_track = xpos + int(self.playlistpos)
		
		seek_track = xpos

		self.logger.debug("Seeking xpos / actual_track %s / %s" % (xpos,seek_track))

		self.mpdc.seek(seek_track,0)

	def add_directory(self,directory_URI):
	
		self.mpdc.add(directory_URI)

	def clear_playlist(self):
		self.mpdc.clear()

	def remove_track(self,xpos):
		self.mpdc.delete(xpos)

	def update_library(self):
		self.mpdc.update()

	def track_seek(self,xpos):
		# seek to current track xpos seconds 
		# calculate seek position in seconds from xpos pixels
		# track length in secs, progress bar start=10, progress bar width=460, xpos
		
		clickpos = xpos - 10 # x position of progress bar png
		trackpercent = clickpos / 460. # width of progress bar png
		seekto = self.timeTotalsecs * trackpercent
		status = self.playbackStatus
		if status == "play":
			self.mpdc.seekcur(seekto)
	
	def control_player(self, command):
		if command == "next":
			self.mpdc.next()
		elif command == "previous":
			self.mpdc.previous()
		elif command == "pause":
			self.mpdc.pause()
		elif command == "stop":
			self.mpdc.stop()
		else:
			pass

	def toggle_backlight(self):
		bl = (self.backlight + 1) % 2
		if bl == 1:
			self.turn_backlight_on()
		else:
			self.turn_backlight_off()

	def turn_backlight_off(self):
		self.logger.debug("Backlight off")
		#subprocess.call("echo 1 | sudo tee /sys/class/backlight/*/bl_power", shell=True)
		subprocess.call("gpio -g mode 18 pwm", shell=True)
		subprocess.call("gpio -g pwm 18 0", shell=True)
		self.backlight = 0

	def turn_backlight_on(self):
		self.logger.debug("Backlight on")
		#subprocess.call("echo 0 | sudo tee /sys/class/backlight/*/bl_power", shell=True)
		subprocess.call("gpio -g pwm 18 900", shell=True)
		self.backlight = 1


	def get_backlight_status(self):
		return self.backlight

	def adjust_sleeptimer(self, amount, direction):
		sleeptimer = self.sleepTimer
		if direction == "+":
			if sleeptimer:
				if timedelta(minutes=120) > (sleeptimer + timedelta(minutes=amount))-datetime.datetime.now():
					sleeptimer = sleeptimer + timedelta(minutes=amount)
				else:
					sleeptimer = datetime.datetime.now() + timedelta(minutes=120)
			else:
				sleeptimer = datetime.datetime.now() + timedelta(minutes=amount)
		else:
			if sleeptimer:
				sleeptimer = sleeptimer - timedelta(minutes=amount)
				if sleeptimer < datetime.datetime.now():
					sleeptimer = None
		self.sleepTimer = sleeptimer

	def sleep(self):
		self.logger.info("SLEEP")
		self.turn_backlight_off()
		self.control_player("stop")
		self.sleepTimer = None
