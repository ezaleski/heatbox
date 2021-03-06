off = Color(0,   0,   0)
green = Color(127,   0,   0)
red = Color(0,   127,   0)
blue = Color(0,   0,   171)
orange = Color(89, 119, 14)
purple = Color(85, 0, 171, 192)
pipe_name = '/tmp/heatbox_pipe'
blinkingColon = False
countdownActive = False
countdownLightsActive = False
keypadActive = False
segments = [[0, 1, 2, 3],[4, 5, 6, 7],[8, 9, 10, 11],[12, 13, 14, 15],[16, 17, 18, 19],[20, 21, 22, 23],[24, 25, 26, 27]]
segments = [[0, 1 ],[2, 3],[4, 5],[6, 7],[8, 9],[10, 11],[12, 13]]
segments = [[8, 9 ],[10, 11],[12, 13],[6, 7],[0, 1],[2, 3],[4, 5]]
segmentOffset = 28
segmentOffset = 14
currentMode = 'NONE'
digits = {
	"0" : [0, 1, 2, 4, 5, 6],
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


lastDigit = { 0: "", 1: "", 2: "", 3: ""}

# LED strip configuration:
LED_COUNT      = 114      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
lcd_rs        = 25  # Note this might need to be changed to 21 for older revision Pi's.
lcd_en        = 24
lcd_d4        = 23
lcd_d5        = 17
lcd_d6        = 12
lcd_d7        = 27
lcd_backlight = 4
# Define LCD column and row size for 16x2 LCD.
lcd_columns = 16
lcd_rows    = 2

lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows, lcd_backlight)

mongoclient = pymongo.MongoClient("localhost", 27017)
mongodb = mongoclient.heatbox
