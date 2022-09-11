import time
import subprocess
import os
import glob
from datetime import datetime

path = '\\\\10.10.10.10\\Promos\\Feeds\\'
out_path = '\\\\10.10.10.10\\Promos\\Output\\'
pattern = '*[0-9][0-9][0-9]H.mxf'

# Store promo files as basename in promos list.
promos = [os.path.basename(x) for x in glob.glob(f'{path}{pattern}')]

# FFMPEG transcode function.
# Overlays a local network sponsor tag file to the end of a raw promo video file from a syndicator.
# Utilizes a complex filter with a sidechain compressor to lower the promo audio relative to the tag audio.
def transcode(feed_file, file_path, output_path, audio_start, tag_start, file_timestamp, dur):
    print(f'Rendering {feed_file}...')
    render_start = time.perf_counter()
    subprocess.call(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-ss', '00:00:00.067', '-i', f'{feed_file}', '-i', f'{file_path}tag.mxf', '-filter_complex', 
                    f'[1:v]setpts=PTS+{tag_start}/TB[1v];[0:v][1v]overlay=enable=gte(t\\,{tag_start})[vout];[1:a]adelay={audio_start}|{audio_start},apad,asplit=2[1amix][1aref];[0:a][1aref]sidechaincompress[0asc];[0asc][1amix]amix=inputs=2:duration=first[aout1]', 
                    '-map', '[vout]', '-map', '[aout1]', '-c:v', 'mpeg2video', '-b:v', '10M', '-pix_fmt', 'yuv422p', '-c:a', 'pcm_s16le', '-profile:v', '0', '-level', '2', 
                    '-ar', '48k', '-shortest', '-s', '1280x720', '-flags', 'ilme', '-r', '59.94', '-preset', 'ultrafast', '-t', f'{dur}', f'{output_path}{file_timestamp}.mxf'])
    render_stop = time.perf_counter()
    print(f"Completed in {render_stop - render_start:0.1f} seconds.")

for promo in promos:
    duration = promo[-7:-5]
    date_obj = datetime.now()
    timestamp = date_obj.strftime('%H-%M-%S')
    t_start = 7
    a_start = t_start * 1000
    transcode(promo, path, out_path, a_start, t_start, timestamp, duration)

    