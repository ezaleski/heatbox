#!/bin/sh
pkill hostapd
wpa_supplicant -B -Dwext -iwlan0 -c /etc/wpa_supplicant/wpa_supplicant.conf
ifconfig wlan0 up
ifdown wlan0
ifup wlan0

