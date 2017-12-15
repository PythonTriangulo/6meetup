#!/usr/bin/env python
#
# Project: Video Streaming with Flask
# Author: Log0 <im [dot] ckieric [at] gmail [dot] com>
# Date: 2014/12/21
# Website: http://www.chioka.in/
# Description:
# Modified to support streaming out with webcams, and not just raw JPEGs.
# Most of the code credits to Miguel Grinberg, except that I made a small tweak. Thanks!
# Credits: http://blog.miguelgrinberg.com/post/video-streaming-with-flask
#
# Usage:
# 1. Install Python dependencies: cv2, flask. (wish that pip install works like a charm)
# 2. Run "python main.py".
# 3. Navigate the browser to the local webpage.
from flask import Flask, render_template, Response, request, abort
from camera import VideoCamera
import json
import time
import os
from os import getpid
import psutil

flag = True

app = Flask(__name__)

def read(diretory):

    with open(str(diretory)) as f:
        lines = f.readlines()
    lines = [x.strip() for x in lines]
    l = lines[0].split(',')
    __roi_x = (int(l[0]),int(l[2]))#int(l[0]+l[2]))
    __roi_y = (int(l[1]),int(l[3]))#int(l[1]+l[3]))

    l = lines[1].split(',')
    __roi_x_template = (int(l[0]),int(l[2]))#int(l[0]+l[2]))
    __roi_y_template = (int(l[1]),int(l[3]))#int(l[1]+l[3]))

    l = lines[2].split(',')
    __canny_upper = float(l[0])
    __canny_lower = float(l[1])


    return __roi_x, __roi_y, __roi_x_template, __roi_y_template, __canny_upper, __canny_lower

@app.route('/')
def index():
    return render_template('index.html')

def gen(camera):
    timecomp = None
    while True:
        #frame = camera.get_frame()
        moddate = os.stat("operator_params.txt")[8]
        if time.ctime(moddate) != timecomp:
            timecomp = time.ctime(moddate)
            #print(time.ctime(moddate))
            __roi_x, __roi_y, __roi_x_template, __roi_y_template, __canny_upper, __canny_lower = read(diretory="operator_params.txt")
        if flag == True:
            frame = camera.canny(thrs1=__canny_upper, thrs2=__canny_lower)
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    global video_camera
    video_camera = VideoCamera()
    return Response(gen(video_camera),mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/post', methods=['POST'])
def post_route():

    if request.method == 'POST':
        data = request.get_json(force=True)
        text_file= open("operator_params.txt", "w")
        text_file.write("%s,%s,%s,%s\n" %(data[0], data[1], data[2], data[3]))
        text_file.write("%s,%s,%s,%s\n" %(data[4], data[5], data[6], data[7]))
        text_file.write("%s,%s\n" %(data[8], data[9]))
        text_file.close()
        time.sleep(1)
        print('Data Received: "{data}"'.format(data=data))
        return "Request Processed.\n"

@app.route('/start', methods=['POST'])
def post_start():
    global flag
    global video_camera
    if request.method == 'POST':
        print("fiz")
        flag = False
        data = request.get_json(force=True)
        os.system("sudo rm ../data/images/*")
        video_camera.__del__()
        os.system("bin/solvecam &")
        print('Data Received: "{data}"'.format(data=data))

        return "Request Processed.\n"

@app.route('/stop', methods=['POST'])
def post_stop():
    global video_camera
    global flag
    if request.method == 'POST':
        data = request.get_json(force=True)
        mynames = ["solvecam", "central", "tracker"]
        mypid = getpid()
        for process in psutil.process_iter():
            if process.pid != mypid:
                for path in process.cmdline():
                    for myname in mynames:
                        if myname in path:
                            print "process found"
                            process.terminate()
        flag = True
        gen(video_camera)
        print('Data Received: "{data}"'.format(data=data))
        return "Request Processed.\n"


if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', debug=True)

