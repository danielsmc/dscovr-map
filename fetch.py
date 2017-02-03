#!/usr/bin/env python

import json
import os
import requests

server = "https://epic.gsfc.nasa.gov"
img_type = "natural"

all_imgs = []

try:
    os.mkdir("images")
except OSError:
    pass

days = requests.get("%s/api/%s/available"%(server,img_type)).json()
for day in days:
    print day
    day_imgs = requests.get("%s/api/%s/date/%s"%(server,img_type,day)).json()
    all_imgs.extend(day_imgs)

all_imgs.sort(key=lambda x:x['date'])

for image_data in all_imgs:
    img = image_data['image']
    fn = "images/%s.png"%img
    if os.path.exists(fn):
        continue
    print img
    content = requests.get("%s/epic-archive/png/%s.png"%(server,img)).content
    with open(fn,'wb') as fh:
        fh.write(content)

with open("all_imgs.json",'wb') as fh:
    json.dump(all_imgs,fh)