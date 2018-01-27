#!/usr/bin/python
# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.
import time
from threading import Thread
import os, sys
from threading import Timer
from neopixel import *
import logging
import pymongo
import datetime
import traceback
import signal
from time import gmtime, strftime
from daemon import Daemon
import Adafruit_CharLCD as LCD
import urllib2

PIDFILE = '/var/run/heatbox.pid'
LOGFILE = '/var/log/heatbox.log'

CLOCK_RUNMODE = 1
COUNTDOWN_RUNMODE = 2
INTERVAL_PICK_RUNMODE = 3
SCOREBOARD_RUNMODE = 4
MENU_RUNMODE = 5
SYSMENU_RUNMODE = 6
VOLUME_RUNMODE = 7
SHUTDOWN_RUNMODE = 8
INTERVAL_RUNMODE = 9
MUSIC_PICK_RUNMODE = 10
MUSIC_STOP_RUNMODE = 11
COUNTDOWN_TO_TIME_RUNMODE = 12
NONE_RUNMODE = 100

VOLUME_SYSMENU_RUNMODE = 1
SHUTDOWN_SYSMENU_RUNMODE = 2

currentTimerD1 = " "
currentTimerD2 = " "
currentTimerD3 = " "
currentTimerD4 = " "
currentTimerState = -1
countdownSeconds = -1
countdownMinues = -1
countdownSecondsLeft = -1
currentIntervalIndex = 0
currentMusicIndex = 0
currentInterval = {}
currentMusic = {}
totalPauseTime = 0
totalPauseStartTime = 0
isPaused = False
lastTimeOnStrip = 0
lastMenuShown = ""
lastLCDMsgShown = ""

currentDigit1 = ""
currentDigit2 = ""
currentDigit3 = ""
currentDigit4 = ""
shutdownCount = 0

currentRunmode = NONE_RUNMODE 
prevRunmode = NONE_RUNMODE 
currentMenuMode = -1
prevMenuMode = -1
currentSysMenuMode = -1
prevSysMenuMode = -1
inSysMenu = False
reloadIntervalName = False
reloadMusicName = False
intervalRunning = False
updateLCD = False
displayFileName = "/tmp/display.txt"
LCDFileName = "/tmp/lcd.txt"

logging.basicConfig(filename=LOGFILE,level=logging.DEBUG)
exec(compile(source=open('variables.py').read(), filename='variables.py', mode='exec'))

def signal_handler(signal, frame):
	print('You pressed Ctrl+C!')
	commandClear()
	stopAll()

def getColor(colorString):
	c = colorString.split(",")
	return Color(int(c[1]), int(c[0]), int(c[2]))
	
def initMongo():
	global mongodb
	global mongoclient


def updateMode(mode):
	global mongodb
	mongodb.mode.update({}, {'$set' : {'current' : mode}})

def startUp():
	global strip
	global strandtestActive

	try:
		# Intialize the library (must be called once before other functions).
		strandtestActive = False
		if os.path.exists(pipe_name):
			os.remove(pipe_name)

		if not os.path.exists(pipe_name):
			os.mkfifo(pipe_name)  
			os.chmod(pipe_name, 0666)

		strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
		strip.begin()
		strip.show()
		startMe()
	except Exception as e:
		print e
		logging.exception("message")
		commandClear()
		stopAll()

def resetLCD():
	global lcd
	global lastLCDMsgShown
	lcd.enable_display(False)
	lcd.enable_display(True)
	lcd.clear()
	lcd.message("")
	lastLCDMsgShown = ""

# Define functions which animate LEDs in various ways.

def colorWipe(strip, color, wait_ms=50):
	"""Wipe color across display a pixel at a time."""
	for i in range(strip.numPixels()):
		strip.setPixelColor(i, color)
		strip.show()
		time.sleep(wait_ms/1000.0)

def clearDigit(strip, digitNumber):
	offset = getOffset(digitNumber)
	for val in segments:
		for s in val:
			strip.setPixelColor(s + offset, off)

def getOffset(digitNumber):
	offset = 0
	if digitNumber <= 1:
		offset = segmentOffset*digitNumber
	else:	
		offset = segmentOffset*digitNumber + 2
	return offset

def recolorLast(strip, color):
	for i in range(4):
		offset = getOffset(i)
		for dd in lastDigit[i]:
			for d in digits[dd]:
				for s in segments[d]:
					strip.setPixelColor(s+offset, color)
	strip.show()
		
def displayDigit(strip, digitNumber, digitValue, color):
	global displayFileName

	offset = getOffset(digitNumber)
	if lastDigit[digitNumber] != digitValue:
		clearDigit(strip, digitNumber)

	for d in digits[digitValue]:
		for s in segments[d]:
			strip.setPixelColor(s + offset, color)
	lastDigit[digitNumber] = digitValue
	if digitNumber == 3:
		displayFile = open(displayFileName, "w")
		displayFile.write(lastDigit[0] + lastDigit[1] + ":" + lastDigit[2] + lastDigit[3])
		displayFile.close()

def theaterChase(strip, color, wait_ms=50, iterations=1):
	"""Movie theater light style chaser animation."""
	for j in range(iterations):
		for q in range(3):
			for i in range(0, strip.numPixels(), 3):
				strip.setPixelColor(i+q, color)
			strip.show()
			time.sleep(wait_ms/1000.0)
			for i in range(0, strip.numPixels(), 3):
				strip.setPixelColor(i+q, 0)

def wheel(pos):
	"""Generate rainbow colors across 0-255 positions."""
	if pos < 85:
		return Color(pos * 3, 255 - pos * 3, 0)
	elif pos < 170:
		pos -= 85
		return Color(255 - pos * 3, 0, pos * 3)
	else:
		pos -= 170
		return Color(0, pos * 3, 255 - pos * 3)

def rainbow(strip, wait_ms=20, iterations=1):
	"""Draw rainbow that fades across all pixels at once."""
	for j in range(256*iterations):
		for i in range(strip.numPixels()):
			strip.setPixelColor(i, wheel((i+j) & 255))
		strip.show()
		time.sleep(wait_ms/1000.0)

def rainbowCycle(strip, wait_ms=20, iterations=5):
	"""Draw rainbow that uniformly distributes itself across all pixels."""
	for j in range(256*iterations):
		for i in range(strip.numPixels()):
			strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
		strip.show()
		time.sleep(wait_ms/1000.0)

def theaterChaseRainbow(strip, wait_ms=50):
	"""Rainbow movie theater light style chaser animation."""
	for j in range(256):
		for q in range(3):
			for i in range(0, strip.numPixels(), 3):
				strip.setPixelColor(i+q, wheel((i+j) % 255))
			strip.show()
			time.sleep(wait_ms/1000.0)
			for i in range(0, strip.numPixels(), 3):
				strip.setPixelColor(i+q, 0)

def displayDigitLeft2(strip, digit, digit2, color, duration):
	for d in digits[digit]:
		for s in segments[d]:
			strip.setPixelColor(s, color)
	for d in digits[digit2]:
		for s in segments[d]:
			strip.setPixelColor(s + segmentOffset, color)
	logging.debug("Showing strip: ")
	logging.debug(strip)
	strip.show()
	time.sleep(duration)
	logging.debug("Clearing")
	clearMe(strip)

def displayDigitRight2(strip, digit, digit2, color, duration):
	offset = segmentOffset*2 + 2
	for d in digits[digit]:
		for s in segments[d]:
			strip.setPixelColor(s + offset, color)
	for d in digits[digit2]:
		for s in segments[d]:
			strip.setPixelColor(s + segmentOffset + offset, color)
	logging.debug("Showing strip: ")
	logging.debug(strip)
	strip.show()
	time.sleep(duration)
	logging.debug("Clearing")
	clearMe(strip)

def displayDigit4(strip, digit, digit2, digit3, digit4, color, duration):
	global displayFileName

	for d in digits[digit]:
		for s in segments[d]:
			strip.setPixelColor(s, color)
	for d in digits[digit2]:
		for s in segments[d]:
			strip.setPixelColor(s + segmentOffset, color)
	offset = segmentOffset*2 + 2
	for d in digits[digit3]:
		for s in segments[d]:
			strip.setPixelColor(s + offset, color)
	for d in digits[digit4]:
		for s in segments[d]:
			strip.setPixelColor(s + segmentOffset + offset, color)
	strip.show()
	if duration > 0:
		time.sleep(duration)
		logging.debug("Clearing")
		clearMe(strip)
	displayFile = open(displayFileName, "w")
	displayFile.write(digit + digit2 + ":" + digit3 + digit4)
	displayFile.close()

def displayDigitNoPause(strip, digit, digit2, digit3, digit4, color):
	global currentDigit1 
	global currentDigit2
	global currentDigit3
	global currentDigit4

	if currentDigit1 != digit:
		clearDigit(strip, 1)
		
	if currentDigit2 != digit:
		clearDigit(strip, 2)
		
	if currentDigit3 != digit:
		clearDigit(strip, 3)
		
	if currentDigit4 != digit:
		clearDigit(strip, 4)
		
	for d in digits[digit]:
		for s in segments[d]:
			strip.setPixelColor(s, color)
	for d in digits[digit2]:
		for s in segments[d]:
			strip.setPixelColor(s + segmentOffset, color)
	offset = segmentOffset*2 + 2
	for d in digits[digit3]:
		for s in segments[d]:
			strip.setPixelColor(s + offset, color)
	for d in digits[digit4]:
		for s in segments[d]:
			strip.setPixelColor(s + segmentOffset + offset, color)

	currentDigit1 = digit
	currentDigit2 = digit2
	currentDigit3 = digit3
	currentDigit4 = digit4
	strip.show()

	displayFile = open(displayFileName, "w")
	displayFile.write(digit + digit2 + ":" + digit3 + digit4)
	displayFile.close()

def getCurrentTime():
	return long((time.time() + 0.5) * 1000)

def flashDigit4(strip, digit, digit2, digit3, digit4, color, color2, duration):
	stopAt = getCurrentTime() + duration*1000


	for j in range(1000):
		displayDigitNoPause(strip, digit, digit2, digit3, digit4, color)
		time.sleep(100/1000.0)
		displayDigitNoPause(strip, digit, digit2, digit3, digit4, color2)
		time.sleep(100/1000.0)
		current = getCurrentTime()	
		if current > stopAt:
			break
	logging.debug("Clearing")
	clearMe(strip)

def clearColon(strip):
	strip.setPixelColor(segmentOffset*2 + 0, off)
	strip.setPixelColor(segmentOffset*2 + 1, off)
	strip.show()

def clearMe(strip):
	global displayFileName

	"""Wipe color across display a pixel at a time."""
	for i in range(strip.numPixels()):
		if i != segmentOffset*2 + 0 and i != segmentOffset*2 + 1:
			strip.setPixelColor(i, Color(0,0,0))
	strip.show()

	displayFile = open(displayFileName, "w")
	displayFile.write("     ")
	displayFile.close()

def showOnLCD(msg):
	global lcd
	global LCDFileName
	global lastLCDMsgShown

	if msg != "":
		if msg == lastLCDMsgShown:
			return
	lcd.clear()
	lastLCDMsgShown = msg
	lcd.message(msg)
	lcdFile = open(LCDFileName, "w")
	lcdFile.write(msg)
	lcdFile.close()
	logging.debug("LCD: " + msg)

def stopSound():
	logging.debug("Stopping sound!")
	os.system("/usr/bin/mpc clear;/usr/bin/mpc stop")
def playSound(sound):
	os.system("/usr/bin/mpc clear;/usr/bin/mpc add " + sound + ";/usr/bin/mpc play")
def playEffect(sound):
	os.popen("/usr/bin/mpg123 '/var/lib/mpd/music/" + sound + "' 2>&1 &").read()

def getCurrentVolume():
	x = list(os.popen('amixer sget Speaker | awk -F"[][]" \'/dB/ { print $2 }\' | head -1 | sed -e "s/\%//g"').read().rstrip())
	if len(x) == 3:
		return list([' ', x[0], x[1], x[2]])
	elif len(x) == 2:
		return list([' ', ' ', x[0], x[1]])
	elif len(x) == 1:
		return list([' ', ' ', ' ', x[0]])

	return list([' ', ' ', ' ', ' '])

def buzzer():
	#playSound("Buzzer1.mp3")
	playSound("Alert.mp3")

def areyouready():
	global countdownLightsActive
	playSound("AreYouReady.mp3")
	countdownLightsActive = True
	os.system("/usr/bin/mpc clear;/usr/bin/mpc add AreYouReady.mp3;/usr/bin/mpc play")
	while countdownLightsActive:
		for i in range(20):
			if countdownLightsActive == True:
				theaterChase(strip, Color(127, 127, 127))
		if countdownLightsActive == True:
			colorWipe(strip, Color(255, 255, 0))  # Blue wipe
	clearMe(strip)
	clearColon(strip)

def shutdownStep():
	clearMe(strip)
	time.sleep(.5)
	os.system("shutdown -h now")
	return 0.1

def volumeStep():
	digits = getCurrentVolume()
	displayDigit(strip, 0, digits[0], red)	
	displayDigit(strip, 1, digits[1], red)
	displayDigit(strip, 2, digits[2], red)
	displayDigit(strip, 3, digits[3], red)
	strip.show()
	return 0.1
def countdownToTimeStep():
	global countdownActive
	global countdownSeconds
	global countdownMinutes
	global countdownSecondsLeft
	global currentRunmode

	if countdownActive:
		
		digitsOne = ""
		digitsTwo = ""
		minutesLeft = countdownSecondsLeft/60
		if minutesLeft < 10:
			digitsOne = " " + str(minutesLeft)	
		else:
			digitsOne = str(minutesLeft)
		secLeft = countdownSecondsLeft - minutesLeft*60	
		if secLeft < 10:
			digitsTwo = "0" + str(secLeft)
		else:
			digitsTwo = str(secLeft)
		digits = digitsOne[-2:] + digitsTwo
		l = list(digits)
		for dig in range(4):
			displayDigit(strip, dig, l[dig], red)	

		color = red
		strip.setPixelColor(segmentOffset*2 + 0, color)
		strip.setPixelColor(segmentOffset*2 + 1, color)
		strip.show()
		time.sleep(.5)
		color = off
		strip.setPixelColor(segmentOffset*2 + 0, color)
		strip.setPixelColor(segmentOffset*2 + 1, color)
		strip.show()
		time.sleep(.5)
		countdownSecondsLeft = countdownSecondsLeft - 1
		showOnLCD(str(minutesLeft) + ":" + str(secLeft) + " left")

		if countdownSecondsLeft <= 0:
			buzzer()
			displayDigit4(strip, ' ', '0', '0', '0', red, 2)
			clearMe(strip)
			countdownActive = False
			showOnLCD("Done")
			currentRunmode = NONE_RUNMODE
	return 0.0

def countdownStep():
	global countdownActive
	global countdownSeconds
	global countdownMinutes
	global countdownSecondsLeft
	global currentRunmode

	if countdownActive:
		
		digitsOne = ""
		digitsTwo = ""
		minutesLeft = countdownSecondsLeft/60
		if minutesLeft < 10:
			digitsOne = " " + str(minutesLeft)	
		else:
			digitsOne = str(minutesLeft)
		secLeft = countdownSecondsLeft - minutesLeft*60	
		if secLeft < 10:
			digitsTwo = "0" + str(secLeft)
		else:
			digitsTwo = str(secLeft)
		digits = digitsOne + digitsTwo
		l = list(digits)
		for dig in range(4):
			displayDigit(strip, dig, l[dig], red)	

		color = red
		strip.setPixelColor(segmentOffset*2 + 0, color)
		strip.setPixelColor(segmentOffset*2 + 1, color)
		strip.show()
		time.sleep(.5)
		color = off
		strip.setPixelColor(segmentOffset*2 + 0, color)
		strip.setPixelColor(segmentOffset*2 + 1, color)
		strip.show()
		time.sleep(.5)
		countdownSecondsLeft = countdownSecondsLeft - 1
		showOnLCD(str(countdownSecondsLeft) + "seconds\nleft")

		if countdownSecondsLeft <= 0:
			buzzer()
			displayDigit4(strip, ' ', '0', '0', '0', red, 2)
			clearMe(strip)
			countdownActive = False
			showOnLCD("Done")
			currentRunmode = NONE_RUNMODE
	return 0.0

def doCountDown(minutes, seconds):
	global strip
	global countdownActive
	global countdownSeconds
	global countdownMinutes
	global countdownSecondsLeft
	global currentRunmode

	countdownSecondsLeft = minutes*60 + seconds
	countdownMinutes = minutes
	countdownSeconds = seconds
	currentRunmode = COUNTDOWN_RUNMODE
	countdownActive = True
	
def doCountDownToTime(minutes, seconds):
	global strip
	global countdownActive
	global countdownSeconds
	global countdownMinutes
	global countdownSecondsLeft
	global currentRunmode

	countdownSecondsLeft = minutes*60 + seconds
	countdownMinutes = minutes
	countdownSeconds = seconds
	currentRunmode = COUNTDOWN_TO_TIME_RUNMODE
	countdownActive = True
	

def getInterval(index):
	global mongodb
	intervals = mongodb.intervals.find({})
	try:
		return intervals[index]
	except IndexError:
		logging.error("No index!");
	return

def getMusic(index):
	global mongodb
	intervals = mongodb.music.find({})
	try:
		return intervals[index]
	except IndexError:
		logging.error("No index!");
	return

def getSongInfo(name):
	global mongodb
	songInfo = mongodb.sounds.find_one({"name" : name})
	return songInfo

def getCurrentIntervalState():
	global mongodb
	interval = mongodb.interval_state.find_one({})
	return interval
def updateIntervalState(doc):
	global mongodb
	mongodb.interval_state.drop()
	mongodb.interval_state.insert(doc)
	return 
def clearIntervalState():
	global mongodb
	mongodb.interval_state.drop()
	return 

def getCurrentScore():
	global mongodb
	currentScore = mongodb.score.find_one({})
	if bool(currentScore):
		homeScore = str(currentScore["home"])
		awayScore = str(currentScore["away"])
		homeColor = currentScore["homeColor"]
		awayColor = currentScore["awayColor"]
		return list([homeScore, awayScore, homeColor, awayColor])

	return list()

def increaseScore(homeFlag):
	global mongodb
	currentScore = getCurrentScore()
	logging.debug("Increasing score...");
	if len(currentScore) > 0:
		which = 'away'
		if homeFlag:
			which = 'home'
			score = currentScore[0]
		else:
			score = currentScore[1]

		logging.debug(which + "-" + score)

		if int(score) < 99:
			newscore = int(score) + 1
			logging.debug("Updating score to be " + str(newscore))
			ret = mongodb.score.update({}, {'$set' : {which : newscore}})
			logging.debug(ret)
def decreaseScore(homeFlag):
	global mongodb
	currentScore = getCurrentScore()
	logging.debug("Increasing score...");
	if len(currentScore) > 0:
		which = 'away'
		if homeFlag:
			which = 'home'
			score = currentScore[0]
		else:
			score = currentScore[1]

		logging.debug(which + "-" + score)
		if int(score) > 0:
			newscore = int(score) - 1
			mongodb.score.update({}, {'$set' : {which : newscore}})
			
	
# Step functions
def scoreboardStep():
	global mongodb
	currentScore = getCurrentScore()
	if len(currentScore) > 0:
		homeScore = currentScore[0]
		awayScore = currentScore[1]
		homeColor = currentScore[2]
		awayColor = currentScore[3]

		if len(homeScore) == 1:
			homeScore = " " + homeScore
		
		if len(awayScore) == 1:
			awayScore = " " + awayScore

		totalScore = homeScore + awayScore
		l = list(totalScore)
		displayDigit(strip, 0, l[0], getColor(homeColor))	
		displayDigit(strip, 1, l[1], getColor(homeColor))	
		displayDigit(strip, 2, l[2], getColor(awayColor))	
		displayDigit(strip, 3, l[3], getColor(awayColor))	
		strip.show()
	return 0.1

def menuStep():
	global mongodb
	global currentMenuMode
	global prevMenuMode
	global totalPauseTime
	global totalPauseStartTime
	global lastMenuShown

	currentMode = mongodb.mode.find_one({})
	if bool(currentMode):
		mode = int(currentMode["current"])

		updateDisplay = False

		if currentMenuMode == -1:
			clearMe(strip)
			updateDisplay = True
			currentMenuMode = CLOCK_RUNMODE
			prevMenuMode = currentMenuMode
		
		#if currentMenuMode != prevMenuMode:
		#	logging.debug("Current: " + str(currentMenuMode) + ", Prev: " + str(prevMenuMode))
		#	updateDisplay = True
		#	if prevMenuMode != -1:
		#		logging.debug("Prev:" + str(prevMenuMode) + ", Current: " + str(currentMenuMode))
		
		c = [' ', ' ', ' ', ' ']
		lcdMsg = ''
		if currentMenuMode == CLOCK_RUNMODE:
			c = ['C', 'L', 'O', 'C']
			lcdMsg = 'Clock'
		if currentMenuMode == COUNTDOWN_RUNMODE:
			c = ['T', 'I', 'M', 'R']
			lcdMsg = 'Timer'
		if currentMenuMode == COUNTDOWN_TO_TIME_RUNMODE:
			c = ['T', 'I', 'M', '2']
			lcdMsg = 'Timer To Time'
		if currentMenuMode == INTERVAL_PICK_RUNMODE:
			c = ['I', 'N', 'T', 'R']
			lcdMsg = 'Intervals'
		if currentMenuMode == SCOREBOARD_RUNMODE:
			c = ['S', 'C', 'O', 'R']
			lcdMsg = 'Scoreboard'
		if currentMenuMode == MENU_RUNMODE:
			c = ['M', 'E', 'N', 'U']
			lcdMsg = 'Menu'
		if currentMenuMode == SYSMENU_RUNMODE:
			c = ['S', 'Y', 'S', 'T']
			lcdMsg = 'System Menu'
		if currentMenuMode == NONE_RUNMODE:
			c = [' ', ' ', ' ', ' ']
			lcdMsg = ''
		if currentMenuMode == MUSIC_PICK_RUNMODE:
			c = ['M', 'U', 'S', 'I']
			lcdMsg = 'Music'
		if currentMenuMode == MUSIC_STOP_RUNMODE:
			c = ['S', 'T', 'O', 'P']
			lcdMsg = 'Stop Music'
		if lastMenuShown != lcdMsg:
			updateDisplay = True
		else:
			updateDisplay = False

		if updateDisplay:
			clearMe(strip)
			displayDigit(strip, 0, c[0], red)	
			displayDigit(strip, 1, c[1], red)
			displayDigit(strip, 2, c[2], red)
			displayDigit(strip, 3, c[3], red)
			strip.show()
			showOnLCD(lcdMsg)	
			lastMenuShown = lcdMsg
	return 0.1

def clockStep():
	for i in range(2):
		c = list(datetime.datetime.now().strftime("%I%M"))
		if c[0] == "0":
			c[0] = " "
		for dig in range(4):
			#logging.debug(c[dig])
			displayDigit(strip, dig, c[dig], red)	

		color = red
		if i == 1:
			color = off

		strip.setPixelColor(segmentOffset*2 + 0, color)
		strip.setPixelColor(segmentOffset*2 + 1, color)
		strip.show()
		time.sleep(.5)

	return 0.5

def extendInterval(secs):
	global mongodb
	current = getCurrentIntervalState()
	logging.debug("BEFORE: " + str(current))
	if current is not None:
		for step in current["steps"]:
			step["endTime"] = step["endTime"] + secs
			if step["status"] != "running":
				step["startTime"] = step["startTime"] + secs
		updateIntervalState(current)
		logging.debug("AFTER: " + str(current))
		current = getCurrentIntervalState()
		logging.debug("AFTER2: " + str(current))

def get_sec(time_str):
	m, s = time_str.split(':')
	return int(m) * 60 + int(s)

def showTimeOnStrip(deltaTime, color):
	global lastTimeOnStrip

	if deltaTime == lastTimeOnStrip:
		return

	m, s = divmod(deltaTime, 60)
	clockTime = "%02d%02d" % (m, s)
	#for i in range(2):
	#	c = list(clockTime)
	#	if c[0] == "0":
	#		c[0] = " "
	#	for dig in range(4):
	#		#logging.debug(c[dig])
	#		displayDigit(strip, dig, c[dig], color)	
#
#
#		if i == 1:
#			color = off
#
#		strip.setPixelColor(segmentOffset*2 + 0, color)
#		strip.setPixelColor(segmentOffset*2 + 1, color)
#		strip.show()
#		time.sleep(.5)
	c = list(clockTime)
	if c[0] == "0":
		c[0] = " "
	for dig in range(4):
		#logging.debug(c[dig])
		displayDigit(strip, dig, c[dig], color)	

	strip.setPixelColor(segmentOffset*2 + 0, color)
	strip.setPixelColor(segmentOffset*2 + 1, color)
	strip.show()

def intervalStep():
	global mongodb
	global reloadIntervalName
	global currentInterval
	global updateLCD
	global totalPauseStartTime
	global totalPauseTime
	global isPaused

	current = getCurrentIntervalState()
	if current is None:
		return 0.1

	gotoNextStep = False
	allDone = False
	stepCount = 0
	nextStepIndex = 0
	for step in current["steps"]:
		stepCount = stepCount + 1
		if step["status"] == "running":
			if updateLCD == True:
				updateLCD = False
				showOnLCD(current["name"] + "\n" + str(stepCount) + " of " + str(len(current["steps"])))
			logging.debug("Running interval: " + current["name"])
			endTime = step["endTime"]
			startTime = step["startTime"]
			currentTime = int(time.time())
			totalTime = endTime - startTime

			currentPauseTime = 0

			if isPaused:
				if totalPauseStartTime > 0:
					currentPauseTime = currentTime - totalPauseStartTime

			endTime = endTime + currentPauseTime
			logging.debug("Total Pause Time: " + str(totalPauseTime) + " - Current Pause Time:" + str(currentPauseTime) + " - End Time: " + str(endTime))

			if isPaused:
				showOnLCD("Paused...")
				logging.debug("Recoloring to purple")
				recolorLast(strip, purple)
				continue

			deltaTime = endTime - currentTime
			logging.debug("DeltaTime: " + str(deltaTime) + " TotalTime: " + str(totalTime))
			pctLeft = 1
			if totalTime > 0:
				pctLeft = float(deltaTime)/float(totalTime)

			if deltaTime < 0:
				step["status"] = "after"
			else:
				showTimeOnStrip(deltaTime, red)
			continue
		if step["status"] == "before":
			beforeStep = step["beforeStep"]
			logging.debug("Running before step action: " + beforeStep)
			if beforeStep == "PLAYSOUND":
				beforeStepSong = step["beforeStepSong"]
				songInfo = getSongInfo(beforeStepSong)
				if songInfo is not None:
					logging.debug("Playing song: " + songInfo["file"])
					playSound(songInfo["file"])
				step["status"] = "running"
			if beforeStep == "NONE":
				step["status"] = "running"
			if beforeStep == "TIMER":
				currentTime = int(time.time())
				beforeStartTime = step["beforeStartTime"]
				stepStartTime = step["startTime"]
				timerLength = stepStartTime - beforeStartTime
				deltaTime = stepStartTime - currentTime

				logging.debug("Delta Time: " + str(deltaTime))
				if deltaTime > 0:
					showTimeOnStrip(deltaTime, blue)
				else:
					step["status"] = "running"
			showOnLCD(current["name"] + "\n" + str(stepCount) + " of " + str(len(current["steps"])))
			continue
		if step["status"] == "after":
			beforeStep = step["afterStep"]
			logging.debug("Running after step action: " + beforeStep)
			if beforeStep == "PLAYSOUND":
				afterStepSong = step["afterStepSong"]
				songInfo = getSongInfo(afterStepSong)
				if songInfo is not None:
					logging.debug("Playing song: " + songInfo["file"])
					playSound(songInfo["file"])
			step["status"] = "complete"
			gotoNextStep = True
			nextStepIndex = stepCount
			continue

	if gotoNextStep:
		numSteps = len(current["steps"])
		if nextStepIndex < numSteps:
			logging.debug("Going to nextStep: " + str(nextStepIndex))
			current["steps"][nextStepIndex]["status"] = "before"
		else:
			logging.debug("End of Interval!")
			updateMode(NONE_RUNMODE)
			allDone = True
	if allDone:
		clearIntervalState()
		showOnLCD(current["name"] + "\nComplete")
		clearMe(strip)
		clearColon(strip)
	else:	
		updateIntervalState(current)
	return 0.1

def intervalPickStep():
	global mongodb
	global reloadIntervalName
	global currentInterval
	global currentIntervalIndex

	logging.debug("Interval Pick Step")
	if reloadIntervalName:
		reloadIntervalName = False
		currentInterval = getInterval(currentIntervalIndex)
		logging.debug("Interval Index " + str(currentIntervalIndex))
		if currentInterval is not None:
			lcdMsg = currentInterval["intervalData"]["name"]
			logging.debug("Interval Name " + lcdMsg)
			showOnLCD(lcdMsg)
		else:
			currentIntervalIndex = 0
			reloadIntervalName = True
	return 0.5
def musicPickStep():
	global mongodb
	global reloadMusicName
	global currentMusic
	global currentMusicIndex

	if reloadMusicName:
		reloadMusicName = False
		currentMusic = getMusic(currentMusicIndex)
		logging.debug("Music Index " + str(currentMusicIndex))
		if currentMusic is not None:
			lcdMsg = currentMusic["name"]
			logging.debug("Music Name " + lcdMsg)
			showOnLCD(lcdMsg)
		else:
			currentMusicIndex = 0
			reloadMusicName = True
	return 0.5
def sysMenuStep():
	global mongodb
	global currentSysMenuMode
	global prevSysMenuMode

	currentMode = mongodb.mode.find_one({})
	if bool(currentMode):
		mode = int(currentMode["current"])

		updateDisplay = False

		if currentSysMenuMode == -1:
			clearMe(strip)
			updateDisplay = True
			currentSysMenuMode = VOLUME_SYSMENU_RUNMODE
			prevSysMenuMode = currentSysMenuMode
		
		if currentSysMenuMode != prevSysMenuMode:
			updateDisplay = True
			prevSysMenuMode = currentSysMenuMode
	
		
		c = [' ', ' ', ' ', ' ']
		lcdMsg = ''
		if currentSysMenuMode == VOLUME_SYSMENU_RUNMODE:
			c = ['V', 'O', 'L', ' ']
			lcdMsg = 'Volume'
		if currentSysMenuMode == SHUTDOWN_SYSMENU_RUNMODE:
			c = ['S', 'H', 'U', 'T']
			lcdMsg = 'Shutdown'
		
		if updateDisplay:
			clearMe(strip)
			displayDigit(strip, 0, c[0], red)	
			displayDigit(strip, 1, c[1], red)
			displayDigit(strip, 2, c[2], red)
			displayDigit(strip, 3, c[3], red)
			strip.show()
			showOnLCD(lcdMsg)
	return 0.1

def doStartClock(string):
	global clockRunning

	clockRunning = True
	while clockRunning:
		clockStep()
	clearMe(strip)

def doStrandtest(strip):
	global strandtestActive

	strandtestActive = True
	while strandtestActive:
		logging.debug("Strandtest active: " + str(strandtestActive))
		colorWipe(strip, Color(255, 0, 0))  # Red wipe
		if strandtestActive:
			colorWipe(strip, Color(0, 255, 0))  # Blue wipe
		if strandtestActive:
			colorWipe(strip, Color(0, 0, 255))  # Green wipe
		# Theater chase animations.
		if strandtestActive:
			theaterChase(strip, Color(127, 127, 127))  # White theater chase
		if strandtestActive:
			theaterChase(strip, Color(127,   0,   0))  # Red theater chase
		if strandtestActive:
			theaterChase(strip, Color(  0,   0, 127))  # Blue theater chase
		# Rainbow animations.
		if strandtestActive:
			rainbow(strip)
		if strandtestActive:
			rainbowCycle(strip)
		if strandtestActive:
			theaterChaseRainbow(strip)
	clearMe(strip)
	clearColon(strip)
	logging.debug("Done with Strandtests")

def modeMonitor():
	global strip
	global modeMonitorActive
	global mongodb
	global currentMode
	global totalPauseTime
	global totalPauseStartTime
	global currentRunmode
	
	logging.debug('Starting mode monitoring')
	modeMonitorActive = True 
	while(modeMonitorActive):
		doc = mongodb.mode.find_one({})
		sleepTime = .50
		if bool(doc):
			existingMode = currentMode
			currentMode = doc["current"]
			currentRunmode = currentMode
			if existingMode != currentMode:
				logging.debug("Switching to mode " + str(currentMode))
				if currentMode == COUNTDOWN_RUNMODE:
					showOnLCD("Enter Time")	
				if currentMode == COUNTDOWN_TO_TIME_RUNMODE:
					showOnLCD("Enter Time 24H:MM")	
				if currentMode == INTERVAL_RUNMODE:
					totalPauseTime = 0
					totalPauseStartTime = 0
				if currentMode == NONE_RUNMODE:
					clearMe(strip)
					clearColon(strip)
					showOnLCD("   ")
			if currentMode == SCOREBOARD_RUNMODE:
				sleepTime = scoreboardStep()
			if currentMode == CLOCK_RUNMODE:
				sleepTime = clockStep()
			if currentMode == COUNTDOWN_RUNMODE:
				sleepTime = countdownStep()
			if currentMode == COUNTDOWN_TO_TIME_RUNMODE:
				sleepTime = countdownToTimeStep()
			if currentMode == INTERVAL_PICK_RUNMODE:
				sleepTime = intervalPickStep()
			if currentMode == MUSIC_PICK_RUNMODE:
				sleepTime = musicPickStep()
			if currentMode == INTERVAL_RUNMODE:
				sleepTime = intervalStep()
			if currentMode == MENU_RUNMODE:
				sleepTime = menuStep()
			if currentMode == VOLUME_RUNMODE:
				sleepTime = volumeStep()
			if currentMode == SYSMENU_RUNMODE:
				sleepTime = sysMenuStep()
		time.sleep(sleepTime)
	clearMe(strip)
	clearColon(strip)
	logging.debug("Done with mode monitor")

def stopAll():
	global modeMonitorActive
	
	modeMonitorActive = False
	#updateMode(NONE_RUNMODE)
	
def turnoff():
	commandClear()
	updateMode(NONE_RUNMODE)

def commandClear():
	global countdownLightsActive
	global strip
	global strandtestActive
	global keypadActive

	keypadActive = False
	strandtestActive = False
	countdownLightsActive = False
	clearMe(strip)

def commandStrandtest():
	global strip

	thread = Thread(target = doStrandtest, args = (strip,))
	thread.start()

def startupDisplay():
	playEffect("PlayBall.mp3")
	flashDigit4(strip, "H", "E", "A", "T", red,orange, 3)
	displayDigit4(strip, "H", "E", "A", "T", red,1)
	showOnLCD('HEATBOX 1.0\nBy Ed Zaleski')

def processCountdownKeyPress(key):
	global countdownActive
	global currentTimerD1
	global currentTimerD2
	global currentTimerD3
	global currentTimerD4
	global currentTimerState
	global strip

	if countdownActive != True:
		logging.debug("CurrentTimerState: " + str(currentTimerState))

		if currentTimerState == -1:
			currentTimerD1 = " "
			currentTimerD2 = " "
			currentTimerD3 = " "
			currentTimerD4 = key
		elif currentTimerState == 0:
			currentTimerD3 = currentTimerD4
			currentTimerD4 = key
		elif currentTimerState == 1:
			currentTimerD2 = currentTimerD3
			currentTimerD3 = currentTimerD4
			currentTimerD4 = key
		elif currentTimerState == 2:
			currentTimerD1 = currentTimerD2
			currentTimerD2 = currentTimerD3
			currentTimerD3 = currentTimerD4
			currentTimerD4 = key

		if currentTimerState == 3:
			currentTimerState = -1
		else:
			currentTimerState = currentTimerState + 1

		logging.debug("TIME: " + currentTimerD1 + currentTimerD2 + currentTimerD3 + currentTimerD4)
		displayDigit(strip, 0, currentTimerD1, red)	
		displayDigit(strip, 1, currentTimerD2, red)	
		displayDigit(strip, 2, currentTimerD3, red)	
		displayDigit(strip, 3, currentTimerD4, red)	
		strip.show()

def processCountdownToTimeKeyPress(key):
	global countdownActive
	global currentTimerD1
	global currentTimerD2
	global currentTimerD3
	global currentTimerD4
	global currentTimerState
	global strip

	if countdownActive != True:
		logging.debug("CurrentTimerState: " + str(currentTimerState))

		if currentTimerState == -1:
			currentTimerD1 = " "
			currentTimerD2 = " "
			currentTimerD3 = " "
			currentTimerD4 = key
		elif currentTimerState == 0:
			currentTimerD3 = currentTimerD4
			currentTimerD4 = key
		elif currentTimerState == 1:
			currentTimerD2 = currentTimerD3
			currentTimerD3 = currentTimerD4
			currentTimerD4 = key
		elif currentTimerState == 2:
			currentTimerD1 = currentTimerD2
			currentTimerD2 = currentTimerD3
			currentTimerD3 = currentTimerD4
			currentTimerD4 = key

		if currentTimerState == 3:
			currentTimerState = -1
		else:
			currentTimerState = currentTimerState + 1

		logging.debug("TIME: " + currentTimerD1 + currentTimerD2 + currentTimerD3 + currentTimerD4)
		displayDigit(strip, 0, currentTimerD1, red)	
		displayDigit(strip, 1, currentTimerD2, red)	
		displayDigit(strip, 2, currentTimerD3, red)	
		displayDigit(strip, 3, currentTimerD4, red)	
		strip.show()

def handleKeypress(key):
	global currentRunmode
	global prevRunmode
	global currentMenuMode
	global currentSysMenuMode
	global prevMenuMode
	global countdownActive
	global currentTimerD1
	global currentTimerD2
	global currentTimerD3
	global currentTimerD4
	global currentTimerState
	global countdownSeconds
	global countdownMinutes
	global countdownSecondsLeft
	global reloadIntervalName
	global reloadMusicName
	global currentIntervalIndex
	global currentMusicIndex
	global updateLCD
	global isPaused
	global totalPauseStartTime
	global totalPauseTime
	global lastLCDMsgShown
	global shutdownCount


	logging.debug("Handle Keypress: " + key)
	logging.debug("Current Mode: " + str(currentRunmode) + " : " + str(MENU_RUNMODE))
	logging.debug("Current SysMode: " + str(currentSysMenuMode))
	logging.debug("Current MenuMode: " + str(currentMenuMode))

	shutdownKeyPressed = False

	if key == "A":
		logging.debug("Current Mode: " + str(currentRunmode) + " : " + str(MENU_RUNMODE))
		logging.debug("Current SysMode: " + str(currentSysMenuMode))
		logging.debug("Current MenuMode: " + str(currentMenuMode))
		if currentRunmode == MENU_RUNMODE:
			if currentMenuMode == CLOCK_RUNMODE:
				currentMenuMode = COUNTDOWN_RUNMODE
			elif currentMenuMode == COUNTDOWN_RUNMODE:
				currentMenuMode = COUNTDOWN_TO_TIME_RUNMODE
			elif currentMenuMode == COUNTDOWN_TO_TIME_RUNMODE:
				currentMenuMode = INTERVAL_PICK_RUNMODE
			elif currentMenuMode == INTERVAL_PICK_RUNMODE:
				currentMenuMode = MUSIC_PICK_RUNMODE
			elif currentMenuMode == MUSIC_PICK_RUNMODE:
				currentMenuMode = MUSIC_STOP_RUNMODE
			elif currentMenuMode == MUSIC_STOP_RUNMODE:
				currentMenuMode = SCOREBOARD_RUNMODE
			elif currentMenuMode == SCOREBOARD_RUNMODE:
				currentMenuMode = SYSMENU_RUNMODE
				currentSysMenuMode = -1
			elif currentMenuMode == MENU_RUNMODE:
				currentMenuMode = MENU_RUNMODE
			elif currentMenuMode == SYSMENU_RUNMODE:
				currentMenuMode = CLOCK_RUNMODE	
			elif currentMenuMode == NONE_RUNMODE:
				currentMenuMode = NONE_RUNMODE
			else:
				currentMenuMode = NONE_RUNMODE
		elif currentRunmode == SYSMENU_RUNMODE:
			if currentSysMenuMode == VOLUME_SYSMENU_RUNMODE:
				currentSysMenuMode = SHUTDOWN_SYSMENU_RUNMODE
			elif currentSysMenuMode == SHUTDOWN_SYSMENU_RUNMODE:
				currentSysMenuMode = VOLUME_SYSMENU_RUNMODE
			elif currentSysMenuMode == -1:
				currentMenuMode = CLOCK_RUNMODE	
		elif currentRunmode == INTERVAL_PICK_RUNMODE:
			nextIntervalIndex = currentIntervalIndex + 1
			if getInterval(nextIntervalIndex):
				currentIntervalIndex = nextIntervalIndex
			else:
				currentIntervalIndex = 0
			reloadIntervalName = True
		elif currentRunmode == MUSIC_PICK_RUNMODE:
			logging.debug("Switching to Music pick mode")
			nextMusicIndex = currentMusicIndex + 1
			if getMusic(nextMusicIndex):
				currentMusicIndex = nextMusicIndex
			else:
				currentMusicIndex = 0
			reloadMusicName = True
		else:
			logging.debug("A")
			logging.debug("Switching to Menu mode")
			prevRunmode = currentRunmode
			updateMode(MENU_RUNMODE)
			currentRunmode = MENU_RUNMODE
			currentMenuMode = CLOCK_RUNMODE
			prevMenuMode = -1

	if key == "B":
		if currentRunmode == VOLUME_RUNMODE:
			os.popen("/usr/bin/amixer set Speaker 5%+ 2>&1 > /dev/null").read()
		if currentRunmode == SCOREBOARD_RUNMODE:
			increaseScore(False)
	if key == "C":
		if currentRunmode == VOLUME_RUNMODE:
			os.popen("/usr/bin/amixer set Speaker 5%- 2>&1 > /dev/null").read()
		if currentRunmode == SCOREBOARD_RUNMODE:
			decreaseScore(False)
	if key == "1":
		if currentRunmode == COUNTDOWN_RUNMODE:
			processCountdownKeyPress(key)
		if currentRunmode == COUNTDOWN_TO_TIME_RUNMODE:
			processCountdownToTimeKeyPress(key)
	if key == "2":
		if currentRunmode == COUNTDOWN_RUNMODE:
			processCountdownKeyPress(key)
		if currentRunmode == COUNTDOWN_TO_TIME_RUNMODE:
			processCountdownToTimeKeyPress(key)
	if key == "3":
		if currentRunmode == COUNTDOWN_RUNMODE:
			processCountdownKeyPress(key)
		if currentRunmode == COUNTDOWN_TO_TIME_RUNMODE:
			processCountdownToTimeKeyPress(key)
	if key == "4":
		if currentRunmode == COUNTDOWN_RUNMODE:
			processCountdownKeyPress(key)
		if currentRunmode == SCOREBOARD_RUNMODE:
			increaseScore(True)
		if currentRunmode == COUNTDOWN_TO_TIME_RUNMODE:
			processCountdownToTimeKeyPress(key)
	if key == "5":
		if currentRunmode == INTERVAL_RUNMODE:
			logging.debug("FIVE PRESSED")
			if isPaused:
				showOnLCD("Resumed")
				isPaused = False
				updateLCD = True	
				currentTime = int(time.time())
				logging.debug("extending intervals by " + str(currentTime - totalPauseStartTime) + " seconds.")
				extendInterval(currentTime - totalPauseStartTime)
				totalPauseStartTime = int(time.time())
			else:
				totalPauseStartTime = int(time.time())
				showOnLCD("Paused")
				isPaused = True
		if currentRunmode == COUNTDOWN_RUNMODE:
			processCountdownKeyPress(key)
		if currentRunmode == COUNTDOWN_TO_TIME_RUNMODE:
			processCountdownToTimeKeyPress(key)
		stopSound()
	if key == "6":
		if currentRunmode == COUNTDOWN_RUNMODE:
			processCountdownKeyPress(key)
		if currentRunmode == COUNTDOWN_TO_TIME_RUNMODE:
			processCountdownToTimeKeyPress(key)
	if key == "7":
		if currentRunmode == COUNTDOWN_RUNMODE:
			processCountdownKeyPress(key)
		if currentRunmode == COUNTDOWN_TO_TIME_RUNMODE:
			processCountdownToTimeKeyPress(key)
		if currentRunmode == SCOREBOARD_RUNMODE:
			decreaseScore(True)
	if key == "8":
		if currentRunmode == COUNTDOWN_RUNMODE:
			processCountdownKeyPress(key)
		if currentRunmode == COUNTDOWN_TO_TIME_RUNMODE:
			processCountdownToTimeKeyPress(key)
	if key == "9":
		if currentRunmode == COUNTDOWN_RUNMODE:
			processCountdownKeyPress(key)
		if currentRunmode == COUNTDOWN_TO_TIME_RUNMODE:
			processCountdownToTimeKeyPress(key)
	if key == "0":
		if currentRunmode == COUNTDOWN_RUNMODE:
			processCountdownKeyPress(key)
		else:
			if currentRunmode == COUNTDOWN_TO_TIME_RUNMODE:
				processCountdownToTimeKeyPress(key)
			else:
				msg = lastLCDMsgShown
				resetLCD()
				showOnLCD(msg)

	if key == "#":
		if currentRunmode == MENU_RUNMODE:
			updateMode(currentMenuMode)
			currentRunmode = currentMenuMode
			if currentRunmode == INTERVAL_PICK_RUNMODE:
				reloadIntervalName = True
			if currentRunmode == MUSIC_PICK_RUNMODE:
				reloadMusicName = True
			if currentRunmode == MUSIC_STOP_RUNMODE:
				stopSound()
		elif currentRunmode == COUNTDOWN_RUNMODE:
			updateMode(currentMenuMode)
			currentRunmode = currentMenuMode
			showOnLCD("Enter Time")	
	
			if countdownActive != True:
				d1 = currentTimerD1
				d2 = currentTimerD2
				d3 = currentTimerD3
				d4 = currentTimerD4
				if d1 == ' ':
					d1 = '0'
				if d2 == ' ':
					d2 = '0'
				if d3 == ' ':
					d3 = '0'
				if d4 == ' ':
					d4 = '0'

				minutes = int(d1)*10 + int(d2)
				seconds = int(d3)*10 + int(currentTimerD4)
				countdownSecondsLeft = minutes*60 + seconds
				countdownMinutes = minutes
				countdownSeconds = seconds
				countdownActive = True
		elif currentRunmode == COUNTDOWN_TO_TIME_RUNMODE:
			updateMode(currentMenuMode)
			currentRunmode = currentMenuMode
			showOnLCD("Enter Time 24H:MM")	
	
			if countdownActive != True:
				d1 = currentTimerD1
				d2 = currentTimerD2
				d3 = currentTimerD3
				d4 = currentTimerD4
				if d1 == ' ':
					d1 = '0'
				if d2 == ' ':
					d2 = '0'
				if d3 == ' ':
					d3 = '0'
				if d4 == ' ':
					d4 = '0'

				time = d1 + d2 + d3 + d4
				today = datetime.datetime.today()
				s = today.strftime("%m/%d/%Y")
				d = datetime.datetime.strptime(s + " " + time, "%m/%d/%Y %H%M")
				diff = (d-today).total_seconds()

				logging.debug("Diff: " + str(diff))
				countdownSecondsLeft = int(diff)
				countdownMinutes = 0
				countdownSeconds = 0
				countdownActive = True
		elif currentRunmode == SYSMENU_RUNMODE:
			if currentSysMenuMode == VOLUME_SYSMENU_RUNMODE:
				currentRunmode = VOLUME_RUNMODE
				updateMode(currentRunmode)
			elif currentSysMenuMode == SHUTDOWN_SYSMENU_RUNMODE:
				currentRunmode = NONE_RUNMODE
				updateMode(currentRunmode)
				shutdownStep()
		elif currentRunmode == INTERVAL_PICK_RUNMODE:
			currentInterval = getInterval(currentIntervalIndex)
			if currentInterval is not None:
				intervalId = currentInterval["intervalId"]
				logging.debug("Going to start interval " + currentInterval["intervalData"]["name"] + " (" + intervalId + ")")
				urllib2.urlopen("http://localhost/api.php?action=startInterval&intervalId=" + intervalId)
				currentRunmode = INTERVAL_RUNMODE
		elif currentRunmode == MUSIC_PICK_RUNMODE:
			currentMusic = getMusic(currentMusicIndex)
			if currentMusic is not None:
				fileName = currentMusic["link"]
				logging.debug("Going to play " + fileName)
				# Play HERE
				playSound(fileName)
				currentRunmode = MENU_RUNMODE
			
		clearMe(strip)
	
	if key == "*":
		shutdownKeyPressed = True
		if currentRunmode == INTERVAL_RUNMODE:
			updateLCD = True
			stopSound()
		if currentRunmode == INTERVAL_PICK_RUNMODE:
			currentRunmode = MENU_RUNMODE
		else:
			if currentRunmode == MUSIC_PICK_RUNMODE:
				currentRunmode = MENU_RUNMODE
			else:
				currentRunmode = NONE_RUNMODE
		updateMode(currentRunmode)
		countdownActive = False
		clearMe(strip)
		resetLCD()
		if shutdownCount == 3:
			showOnLCD("Shutdown ?")	
		if shutdownCount > 3:
			shutdownStep()	

	if shutdownKeyPressed:
		shutdownCount = shutdownCount + 1
	else:
		shutdownCount = 0

def startMe():
	global strip
	global countdownLightsActive

	clearMe(strip)

	thread = Thread(target = startupDisplay, args = ())
	thread.start()

	logging.debug('Started...');
	try:
		pipein = open(pipe_name, 'r')
		while True:
			line = pipein.readline()[:-1]
			if line != "":
				parms = line.split(",")
				command = parms[0]
				logging.debug('Command: ' + command + ' Value: ' + parms[1]);
				if command == "turnoff":
					turnoff()
				if command == "set":
					upper = parms[1].upper()
					logging.debug('Received (%s)' % (upper))
					l = list(upper)
					displayDigit4(strip, l[0], l[1], l[2], l[3], green, 5)
				if command == "countDown":
					minutes = int(parms[1])
					seconds = int(parms[2])
					doCountDown(minutes, seconds)
				if command == "countDownToTime":
					minutes = int(parms[1])
					seconds = int(parms[2])
					doCountDownToTime(minutes, seconds)
				if command == "startclock":
					thread = Thread(target = doStartClock, args = (strip,))
					thread.start()
				if command == "stopclock":
					global clockRunning
					global blinkingColon
					global countdownLightsActive
					blinkingColon = False
					clockRunning = False
					countdownLightsActive = False
				if command == "strandtest":
					commandStrandtest()
				if command == "strandteststop":
					commandClear()
				if command == "clear":
					commandClear()
				if command == "shutdown":
					os.system("shutdown -h now")
				if command == "keypress":
					keypressed = parms[1]
					handleKeypress(keypressed)
					playEffect("Boop.mp3")
				if command == "hotspotup":
					os.system("ifdown eth0;ifup wlan1")
				if command == "hotspotdown":
					os.system("ifdown wlan1;ifup eth0")
				logging.debug('Done processing command: ' + command)
			else:
				time.sleep(.10)
	except KeyboardInterrupt:
		commandClear()
		stopAll()


if __name__ == "__main__":
	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			print "Starting ..."
			sys.stdout.flush()
			os.system("nohup /root/heatbox/hb.py daemon & >/dev/null 2>&1")
		elif 'daemon' == sys.argv[1]:
			initMongo()
			thread2 = Thread(target = modeMonitor, args = ())
			thread2.start()
			startUp()

		elif 'stop' == sys.argv[1]:
			print "Stopping ..."
			sys.stdout.flush()
			os.system("pkill hb.py")

		elif 'restart' == sys.argv[1]:
			print "Stopping ..."
			sys.stdout.flush()
			os.system("pkill -f 'hb.py daemon'")
			time.sleep(1)
			print "Restarting ..."
			sys.stdout.flush()
			os.system("/root/heatbox/hb.py start")

		elif 'status' == sys.argv[1]:
			os.system("ps -ef | grep 'hb.py daemon' | grep -v grep")

		else:
			print "Unknown command"
			sys.exit(2)
			sys.exit(0)
	else:
		print "usage: %s start|stop|restart|status" % sys.argv[0]
		sys.exit(2)
