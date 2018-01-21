#!/bin/sh
cp $1 /var/lib/mpd/music
mpc update
mpc ls
