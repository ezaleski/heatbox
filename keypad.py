import RPi.GPIO as GPIO
import time
 
 
GPIO.setmode(GPIO.BOARD)
 
MATRIX = [ [1,2,3,'A'], [4,5,6,'B'], [7,8,9,'C'], ['*',0,'#','D'] ]
 
ROW = [29,31,33,35]
COL = [36,37,38,40]
 
for j in range(4):
	GPIO.setup(COL[j], GPIO.OUT)
	GPIO.output(COL[j], 1)
 
 
for i in range(4):
	GPIO.setup(ROW[i], GPIO.IN, pull_up_down = GPIO.PUD_UP)
 
 
try:
	while(True):
		for j in range(4):
			GPIO.output(COL[j],0)
 
		for i in range(4):
			if GPIO.input(ROW[i]) == 0:
				print MATRIX[i][j]
				time.sleep(0.2)
				while(GPIO.input(ROW[i]) == 0):
					pass
								     
			GPIO.output(COL[j],1)
except KeyboardInterupt:
	GPIO.cleanup()
