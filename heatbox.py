#!/usr/bin/python
# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.
import time
import SimpleHTTPServer
import SocketServer
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer


from threading import Timer

from neopixel import *

segments = [[0, 1, 2, 3],[4, 5, 6, 7],[8, 9, 10, 11],[12, 13, 14, 15],[16, 17, 18, 19],[20, 21, 22, 23],[24, 25, 26, 27]]
segmentOffset = 28
	#"0" : [0, 1, 2, 4, 5, 6],
digits = {
	"0" : [3, 4, 5, 6],
	"1" : [2, 6],
	"2" : [1, 2, 3, 4, 5],
	"3" : [1, 2, 3, 5, 6],
	"4" : [0, 2, 3, 6],
	"5" : [0, 1, 3, 5, 6],
	"6" : [0, 1, 3, 4, 5, 6],
	"7" : [1, 2, 6],
	"8" : [0, 1, 2, 3, 4, 5, 6],
	"9" : [0, 1, 3, 2, 5, 6],
	"A" : [0, 1, 2, 3, 4, 6],
	"B" : [0, 3, 4, 5, 6],
	"C" : [0, 1, 4, 5],
	"D" : [2, 3, 4, 5, 6],
	"E" : [0, 1, 3, 4, 5],
	"F" : [0, 1, 3, 4],
	"G" : [0, 1, 2, 5, 6],
	"H" : [0, 2, 3, 4, 6],
	"I" : [0, 4],
	"J" : [2, 4, 5, 6],
	"K" : [0, 2, 3, 4, 6],
	"L" : [0, 4, 5],
	"M" : [1, 4, 6],
	"N" : [3, 4, 6],
	"O" : [0, 1, 2, 4, 5, 6],
	"P" : [0, 1, 2, 3, 4],
	"Q" : [0, 1, 2, 3, 6],
	"R" : [3, 4],
	"S" : [0, 1, 3, 5, 6],
	"T" : [0, 3, 4, 5],
	"U" : [0, 2, 4, 5, 6],
	"V" : [4, 5, 6], 
	"W" : [0, 2, 5],
	"X" : [0, 2, 3, 4, 6],
	"Y" : [0, 2, 3, 5, 6],
	"Z" : [1, 2, 3, 4, 5],
	" " : []
	}


# LED strip configuration:
LED_COUNT      = 60      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)


# Define functions which animate LEDs in various ways.

def pulseColor():
	while True:
		for j in range(256):
			for i in range(strip.numPixels()):
				if strip.getPixelColor(i) == 0:			
					strip.setPixelColor(i, wheel((i+j) & 255))
			strip.show()
			time.sleep(30/1000.0)
		time.sleep(.3)

def displayDigit(strip, digit, color,duration):
	for d in digits[digit]:
		for s in segments[d]:
			strip.setPixelColor(s, color)
	strip.show()
	time.sleep(duration)
	clearMe(strip)
def displayDigit2(strip, digit, digit2, color, duration):
	for d in digits[digit]:
		for s in segments[d]:
			strip.setPixelColor(s, color)
	for d in digits[digit2]:
		for s in segments[d]:
			strip.setPixelColor(s + segmentOffset, color)
	strip.show()
	time.sleep(duration)
	clearMe(strip)
	
def colorWipe(strip, color, wait_ms=50):
	"""Wipe color across display a pixel at a time."""
	for i in range(strip.numPixels()):
		strip.setPixelColor(i, color)
		strip.show()
		time.sleep(wait_ms/1000.0)
def clearMe(strip):
	"""Wipe color across display a pixel at a time."""
	for i in range(strip.numPixels()):
		strip.setPixelColor(i, Color(0,0,0))
	strip.show()

def theaterChase(strip, color, wait_ms=50, iterations=10):
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

def doCountUp():
	for d in range(100):
		l = list(str(d).zfill(2))
		displayDigit2(strip, l[0], l[1], green, .05)
	clearMe(strip)

green = Color(127,   0,   0)
red = Color(0,   127,   0)
blue = Color(0,   127,   127)
numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
text = "ED ZALESKI"
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)

PORT = 8000
class myHandler(BaseHTTPRequestHandler):
	#Handler for the GET requests
	def do_GET(self):
		self.send_response(200)
		self.send_header('Content-type','text/html')
		self.end_headers()
		# Send the html message
		if self.path == "/countup":
			doCountUp()
			self.wfile.write("OK")
		else:
			self.wfile.write("Unknown request: (" + self.path + ")")
		return
strip.begin()
clearMe(strip)
Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
httpd = SocketServer.TCPServer(("", PORT), myHandler)
print "serving at port", PORT
httpd.serve_forever()
# Main program logic follows:
if __name__ == '__main__':
	# Create NeoPixel object with appropriate configuration.
	# Intialize the library (must be called once before other functions).
	#for d in list(text):
	#for d in range(100):
	#	l = list(str(d).zfill(2))
	#	displayDigit2(strip, l[0], l[1], green, .25)
	clearMe(strip)
	#displayDigit2(strip, "E", "D", blue, 2)
