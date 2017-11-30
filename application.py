import threading
import time

import cv2
import sys
from flask import Flask, render_template, Response

from camera import Camera
from mail_config import sendEmail

email_update_interval = 60  # sends an email only once in this time interval
video_camera_1 = Camera(flip=False, src=0)  # creates a camera object, flip vertically
video_camera_2 = Camera(flip=False, src=1)  # creates a camera object, flip vertically

fullbody_classifier_path = "models/fullbody_recognition_model.xml"
facial_classifier_path = "models/facial_recognition_model.xml"
upperbody_classifier_path = "models/upperbody_recognition_model.xml"

object_classifier = cv2.CascadeClassifier(fullbody_classifier_path)  # an opencv classifier

# App Globals (do not edit)
app = Flask(__name__)
last_epoch1 = 0
last_epoch2 = 0


def check_for_objects():
    global last_epoch1
    global last_epoch2
    while True:
        try:
            frame, found_obj = video_camera_1.get_object(object_classifier)
            if found_obj and (time.time() - last_epoch1) > email_update_interval:
                last_epoch1 = time.time()
                print "Sending email... Cam1"
                sendEmail(frame)
                print "done!"
            frame, found_obj = video_camera_2.get_object(object_classifier)
            if found_obj and (time.time() - last_epoch2) > email_update_interval:
                last_epoch2 = time.time()
                print "Sending email... Cam2"
                sendEmail(frame)
                print "done!"
        except:
            print "Error sending email: ", sys.exc_info()[0]


@app.route('/')
def index():
    return render_template('index.html')


def gen(camera):
    while True:
        # frame = camera.get_frame()
        for i in range(0, 5):
            frame = camera.get_frame()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

        frame, found_obj = camera.get_object(object_classifier)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed1')
def video_feed1():
    return Response(gen(video_camera_1),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed2')
def video_feed2():
    return Response(gen(video_camera_2),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    video_camera_1.vs.start()
    video_camera_2.vs.start()
    t = threading.Thread(target=check_for_objects, args=())
    t.daemon = True
    t.start()
    app.run(host='0.0.0.0', debug=False, threaded=True)
