#!/usr/bin/env python

import datetime
import json
import math
import nodebox.graphics
import os
import pyglet.gl
import time

try:
    os.mkdir("warped")
except OSError:
    pass

with open("all_imgs.json") as fh:
    all_imgs = json.load(fh)

with open("warp.frag") as fh:
    warpshader = nodebox.graphics.Shader(fragment = fh.read())

height = 2048
aspect_ratio = math.sqrt(3) # Turns Wagner projection into Kavrayskiy
width = int(height*aspect_ratio)
width -= width%2 #make the width even so libx264 is happy


night_tex = nodebox.graphics.Image("earth_lights_lrg.jpg").texture
ye_olde_buffer = nodebox.graphics.OffscreenBuffer(width, height)

date_txt = nodebox.graphics.Text("foo")
date_txt.fontsize = 50
date_txt.fill = nodebox.graphics.Color(0.9,0.9,0.9)

t = {"warping":0,"saving":0,"count":0}

def warpShot(shot):
    outfn = "warped/%s.jpg"%shot['image']
    if os.path.exists(outfn):
        return
    tic = time.time()
    img = nodebox.graphics.Image("images/%s.png"%shot['image'])
    if img.texture.height==0:
#         print shot['image']
        return
    centroid = shot['centroid_coordinates']
    pos = shot['dscovr_j2000_position']
    earth_rad = 0.99*6371
    dscovr_distance = math.sqrt(pos['x']*pos['x']+pos['y']*pos['y']+pos['z']*pos['z'])/earth_rad
    warpshader.set("centroid",nodebox.graphics.vec2(centroid['lon']*math.pi/180,centroid['lat']*math.pi/180))
    warpshader.set("dscovr_distance",dscovr_distance)      
    pyglet.gl.glActiveTexture(pyglet.gl.GL_TEXTURE1)
    pyglet.gl.glBindTexture(night_tex.target, night_tex.id)
    pyglet.gl.glActiveTexture(pyglet.gl.GL_TEXTURE0)
    warpshader.set("night_tex",1)
    warpshader.set("night_scale",nodebox.graphics.vec2(1200.0/2048,1200.0/2048))
    ye_olde_buffer.push()
    ye_olde_buffer.clear()
    warpshader.push()
    nodebox.graphics.image(img,width=width)
    warpshader.pop()
    date_txt.text = datetime.datetime.strptime(shot['date'],"%Y-%m-%d %H:%M:%S").strftime("%b %d, %Y").replace(" 0", " ")
    date_txt.draw(50,50)
    ye_olde_buffer.pop()
    t['warping'] += time.time()-tic
    tic = time.time()
    img.copy(texture=ye_olde_buffer.texture).save(outfn)
    t['saving'] += time.time()-tic
    t['count'] += 1
    print t['saving']/(t['saving']+t['warping'])
    print (t['saving']+t['warping'])/t['count']

for i in reversed(all_imgs):
    print i['date']
    warpShot(i)