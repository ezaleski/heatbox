#!/bin/sh
pkill wpa_supplicant
ifconfig wlan0 up
ifdown wlan0
ifup wlan0
/usr/sbin/hostapd -B /etc/hostapd/hostapd.conf


