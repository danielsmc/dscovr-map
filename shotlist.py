#!/usr/bin/env python

import datetime
import json
import os
import sys

with open("all_imgs.json") as fh:
    all_imgs = json.load(fh)

camera_ready = []
for shot in all_imgs:
    warped_path = "warped/%s.jpg"%shot['image']
    if os.path.exists(warped_path) and shot['date']>=sys.argv[1]and shot['date']<=sys.argv[2]:
        camera_ready.append({'dt': datetime.datetime.strptime(shot['date'],"%Y-%m-%d %H:%M:%S"),
                             'path': warped_path})

hour_dur = 1.0/24
glitch_max = 4 * hour_dur

with open("frames.ffconcat",'w') as fh:
    fh.write("ffconcat version 1.0\n")
    for i in xrange(1,len(camera_ready)-1):
        dur = hour_dur*(camera_ready[i+1]['dt']-camera_ready[i-1]['dt']).total_seconds()/(60*60*2)
        dur = min(dur,glitch_max)
        fh.write("file %s\nduration %s\n"%(camera_ready[i]['path'],dur))
        # if dur<glitch_max:
        #     fh.write("file %s\nduration %s\n"%(camera_ready[i]['path'],dur))
        # else:
        #     fh.write("file %s\nduration %s\n"%(camera_ready[i]['path'],glitch_max))
        #     # fh.write("file blankframe.jpg\nduration %s\n"%(dur-glitch_max))