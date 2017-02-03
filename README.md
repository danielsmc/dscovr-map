# DSCOVR-MAP

This is a set of scripts for downloading images from NASA's DSCOVR EPIC instrument, projecting those images onto a world map, and assembling the projected images into [videos like this one](https://www.youtube.com/watch?v=YE9Oy-ga7nk). These scripts are somewhat fragile and experimental.

## fetch.py
Fetches a list of all available images and metadata from the [EPIC API](https://epic.gsfc.nasa.gov/about/api). Be aware that as of this writing, the images total almost 20GB. Each time the script is run, it will totally refresh the list of available images, but it will only download image that don't already exist locally. It doesn't verify that images files are valid; there are some that 404.

## warp.py
Transforms EPIC disc images into projected world maps and combines them with a nighttime base layer. The fun stuff happens in the fragment shader `warp.frag`. This script leaks memory like crazy. I suspect that nodebox is "helpfully" caching every texture that's loaded, but I can't figure out where or how to clear said cache.

## shotlist.py
Given a start date and end date, produces a ffconcat file that can be fed to ffmpeg to produce a video of that date range. FFmpeg can be invoked like `ffmpeg  -i frames.ffconcat -c:v libx264 -r 30 -pix_fmt yuv420p -movflags faststart out.mp4`.