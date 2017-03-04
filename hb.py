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
from time import gmtime, strftime
from daemon import Daemon

PIDFILE = '/var/run/heatbox.pid'
LOGFILE = '/var/log/heatbox.log'

logging.basicConfig(filename=LOGFILE,level=logging.DEBUG)
exec(compile(source=open('variables.py').read(), filename='variables.py', mode='exec'))

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
	except:
		commandClear()
		stopAll()


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

def displayDigit(strip, digitNumber, digitValue, color):
	offset = getOffset(digitNumber)
	if lastDigit[digitNumber] != digitValue:
		clearDigit(strip, digitNumber)

	for d in digits[digitValue]:
		for s in segments[d]:
			strip.setPixelColor(s + offset, color)
	lastDigit[digitNumber] = digitValue

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

def displayDigitNoPause(strip, digit, digit2, digit3, digit4, color):
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

def blinkColonStop():
	global blinkingColon
	blinkingColon = False
	

def blinkColonStart(strip, color):
	global blinkingColon
	blinkingColon = True
	while blinkingColon:
		strip.setPixelColor(segmentOffset*2 + 0, color)
		strip.setPixelColor(segmentOffset*2 + 1, color)
		strip.show()
		time.sleep(.5)
		clearColon(strip)
		strip.show()
		time.sleep(.5)
	clearColon(strip)
	
def clearColon(strip):
	strip.setPixelColor(segmentOffset*2 + 0, off)
	strip.setPixelColor(segmentOffset*2 + 1, off)
	strip.show()

def clearMe(strip):
	"""Wipe color across display a pixel at a time."""
	for i in range(strip.numPixels()):
		if i != segmentOffset*2 + 0 and i != segmentOffset*2 + 1:
			strip.setPixelColor(i, Color(0,0,0))
	strip.show()

def playSound(sound):
	os.system("/usr/bin/mpc clear;/usr/bin/mpc add " + sound + ";/usr/bin/mpc play")

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

def doCountDown(minutes, seconds):
	global strip
	global countdownActive
	global blinkingColon

	totalSeconds = minutes*60 + seconds

	countdownActive = True
	secondsLeft = totalSeconds
	while countdownActive:
		if secondsLeft <= 0:
			areyouready()
			clearMe(strip)
			countdownActive = False
			blinkColonStop()
		else:
			digitsOne = ""
			digitsTwo = ""
			minutesLeft = secondsLeft/60
			if minutesLeft < 10:
				digitsOne = " " + str(minutesLeft)	
			else:
				digitsOne = str(minutesLeft)
			secLeft = secondsLeft - minutesLeft*60	
			if secLeft < 10:
				digitsTwo = "0" + str(secLeft)
			else:
				digitsTwo = str(secLeft)
			digits = digitsOne + digitsTwo
			l = list(digits)
			for dig in range(4):
				displayDigit(strip, dig, l[dig], red)	
		strip.show()
		time.sleep(1)
		secondsLeft = secondsLeft - 1
	clearMe(strip)

def doStartClock(string):
	global clockRunning

	clockRunning = True
	while clockRunning:
		c = list(datetime.datetime.now().strftime("%I%M"))
		if c[0] == "0":
			c[0] = " "
		for dig in range(4):
			logging.debug(c[dig])
			displayDigit(strip, dig, c[dig], red)	
		strip.show()
		time.sleep(1)
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
	
	logging.debug('Starting mode monitoring')
	modeMonitorActive = True 
	while(modeMonitorActive):
		doc = mongodb.mode.find_one({})
		if bool(doc):
			currentMode = doc["current"]
			if currentMode == "SCOREBOARD":
				currentScore = mongodb.score.find_one({})
				if bool(currentScore):
					homeScore = str(currentScore["home"])
					awayScore = str(currentScore["away"])
					homeColor = currentScore["homeColor"]
					awayColor = currentScore["awayColor"]
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
		time.sleep(.50)
	clearMe(strip)
	clearColon(strip)
	logging.debug("Done with mode monitor")

def stopAll():
	global modeMonitorActive
	
	modeMonitorActive = False
	
def turnoff():
	commandClear()
	updateMode('OFF')

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
	playSound("PlayBall.mp3")
	flashDigit4(strip, "H", "E", "A", "T", red,orange, 3)
	displayDigit4(strip, "H", "E", "A", "T", red,1)

def startMe():
	global strip
	global countdownLightsActive

	clearMe(strip)

	thread = Thread(target = startupDisplay, args = ())
	thread.start()

	logging.debug('Started...');
	pipein = open(pipe_name, 'r')
	try:
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
					thread = Thread(target = doCountDown, args = (minutes,seconds))
					thread.start()
					thread2 = Thread(target = blinkColonStart, args = (strip, red))
					thread2.start()
				if command == "startclock":
					thread = Thread(target = doStartClock, args = (strip,))
					thread.start()
					thread2 = Thread(target = blinkColonStart, args = (strip, red))
					thread2.start()
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
					playSound("click2.mp3")
				if command == "hotspotup":
					os.system("ifdown eth0;ifup wlan1")
				if command == "hotspotdown":
					os.system("ifdown wlan1;ifup eth0")
				logging.debug('Done processing command: ' + command)
			else:
				time.sleep(.10)
	except KeyboardInterrupt:
		commandClear()


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
