#!/usr/bin/python
# 3x4 Matrix membrane keypad

import os, sys
import RPi.GPIO as GPIO
import time
from daemon import Daemon
import logging


PIDFILE = '/var/run/keypadMonitor.pid'
LOGFILE = '/var/log/keypadMonitor.log'
pipe_name = '/tmp/heatbox_pipe'

logging.basicConfig(filename=LOGFILE,level=logging.DEBUG)


def sendKeypress(keypress):
	pipe = open(pipe_name, 'w')
	pipe.write('keypress,' + keypress + '\n')
	pipe.flush()
	pipe.close()

def startUp():
	GPIO.setmode(GPIO.BOARD)

	MATRIX= [['1','2','3','A'], ['4','5','6','B'], ['7','8','9', 'C'], ['*','0','#', 'D'] ]
	#ROW=[29,31,33,35]
	#COL=[36,37,38,40]
	ROW=[36,37,38,40]
	COL=[29,31,33,35]

	for j in range(4):
	    GPIO.setup(COL[j],GPIO.OUT)
	    GPIO.output(COL[j],1)

	for i in range(4):
	    GPIO.setup(ROW[i],GPIO.IN,pull_up_down = GPIO.PUD_UP)

	try:
	    while(True):
			for j in range(4):
			    GPIO.output(COL[j],0)
			    for i in range(4):
				if GPIO.input(ROW[i]) == 0:
				    logging.debug("Key Pressed: " + MATRIX [i][j])
				    sendKeypress(MATRIX [i][j])
				    time.sleep(0.2)
				    while (GPIO.input(ROW[i])==0):
					pass

			    GPIO.output(COL[j],1)
	except KeyboardInterrupt:
	    GPIO.cleanup()

if __name__ == "__main__":
        if len(sys.argv) == 2:
                if 'start' == sys.argv[1]:
                        print "Starting ..."
                        sys.stdout.flush()
                        os.system("nohup /root/heatbox/keypadMonitor.py daemon & >/dev/null 2>&1")
                elif 'daemon' == sys.argv[1]:
                        startUp()

                elif 'stop' == sys.argv[1]:
                        print "Stopping ..."
                        sys.stdout.flush()
                        os.system("pkill -f 'keypadMonitor.py daemon'")

                elif 'restart' == sys.argv[1]:
                        print "Stopping ..."
                        sys.stdout.flush()
                        os.system("pkill -f 'keypadMonitor.py daemon'")
                        time.sleep(1)
                        print "Restarting ..."
                        sys.stdout.flush()
                        os.system("/root/heatbox/keypadMonitor.py start")

                elif 'status' == sys.argv[1]:
                        os.system("ps -ef | grep 'keypadMonitor.py daemon' | grep -v grep")

                else:
                        print "Unknown command"
                        sys.exit(2)
                        sys.exit(0)
        else:
                print "usage: %s start|stop|restart|status" % sys.argv[0]
                sys.exit(2)
