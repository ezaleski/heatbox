# heatbox

This is a set of python scripts and and a web interface that I wrote to control a custom LED 4 digit display that I built.

It is intended to run on a raspberry pi with the leds connected via the GPIO ports.  I also have a keypad that I have connected as well which will be used to control the display as well.

It is also currently in progress and not yet functional.

## Hardware

This section contains some description of the hardware that I used to build the heatbox.  I have no intention in writing the software to support
anything other than my own custom hardware so if you ever intend on using this software without modification, you'll need to make sure to 
build everything according to what I did.

There are 3 major hardware components :

1. Raspberry Pi (I used a model 3b)
2. LEDs like these (https://www.adafruit.com/products/1461) or these (https://www.amazon.com/gp/product/B00VQ0D2TY) 
3. Keypad like this : (https://www.amazon.com/gp/product/B004XZQ084)

Unfortunately I cannot provide exact setup instructions for this, but I did follow the following set of instructions :

1. (https://learn.adafruit.com/neopixels-on-raspberry-pi) for how to wire up the led strips to the Raspberry Pi.  I cut the LEDs into strips of 4 LED sub-strips and then arranged them on a board in the shape of the standard 7 segment digit (https://www.youtube.com/watch?v=sFggpp8It-s) that is a good idea of what I did.
2. I also had a standard breadboard that I was able to wire the PI's GPIO connectors and be able to access them much easier (https://www.amazon.com/gp/product/B01E93M4P2)  Using this allowed me to hook the keypad directly into the breadboard which made things much neater.  The breadboard can also be used to hold the power connetors for the LED strip as well.

For power I had 1 USB cable that I spliced using this method (https://www.youtube.com/watch?v=Vw4d0oMl0Mg) and the USB cable that came with the PI.  I have a dual USB power connector (https://www.amazon.com/gp/product/B00QTE09SY) that I use when I have access to power, or I can also run both the PI and the LEDs off 2 Jackery portable chargers.
 
## Software

There are 2 python-based daemon processes that run on the PI, one for monitoring the keypad and one for controlling all the LEDs.  [hb.py] is the main controlling logic script and takes it's commands from a named pipe running on the PI.  This allows not only the keypad to communicate commands to the controller, but also a web-based front end that I wrote which can be used to provide a much richer interface than the keypad ever could.

So you will need an apache server running PHP to run the front end.  I also followed these instructions (https://frillip.com/using-your-raspberry-pi-3-as-a-wifi-access-point-with-hostapd/) which allows me to connect to the PI using my mobile device thereby allowing the mobile device to be able to access the web-based front end.

Additionally, I am storing a bunch of persistent configuration data using mongo running also on the PI.  I thought for sure the PI wouldn't be able to handle running mongo, apache AND communicate with the LEDs, but it works just fine much to my surprise.


To be continued...
