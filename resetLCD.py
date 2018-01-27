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

exec(compile(source=open('variables.py').read(), filename='variables.py', mode='exec'))

lcd.enable_display(False)
lcd.enable_display(True)
lcd.clear()
lcd.message("")

