import threading
import time

import cv2
import sys
from flask import Flask, render_template, Response, request

from camera import Camera
from config import Config
from mail_config import send_email

video_camera_1 = Camera(flip=False, src=0)  # creates a camera object, flip vertically

config = Config()

fullbody_classifier_path = "models/fullbody_recognition_model.xml"
facial_classifier_path = "models/facial_recognition_model.xml"
upperbody_classifier_path = "models/upperbody_recognition_model.xml"

object_classifier = cv2.CascadeClassifier(facial_classifier_path)  # an opencv classifier

# App Globals (do not edit)
app = Flask(__name__)


def check_for_objects():
    last_epoch1 = 0
    last_epoch2 = 0
    while True:
        if config.send_email_notifications:
            frame, found_obj = video_camera_1.get_object(object_classifier)
            last_epoch1 = detect_object(found_obj, frame, last_epoch1, camera_id="Cam1")


def detect_object(found_obj, frame, last_epoch, camera_id="Cam1"):
    if found_obj:
        print "Detected object: %s" % camera_id
        if (time.time() - last_epoch) > config.email_send_interval:
            last_epoch = time.time()
            print "Sending email... Cam1"
            send_email(frame)
            print "done!"
    return last_epoch


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # url_to_clean = request.args.get('url_to_clean')
        # print url_to_clean;
        email = request.form['email']
        email_send_interval = request.form['email_send_interval']
        send_email_notifications = 'send_email_notifications' in request.form
        live_preview_with_detection = 'live_preview_with_detection' in request.form

        config.send_email_notifications = send_email_notifications
        config.live_preview_with_detection = live_preview_with_detection
        config.email_send_interval = email_send_interval
        return render_template('index.html')
    if request.method == 'GET':
        return render_template('index.html')


@app.route('/update_settings')
def show_article():
    url_to_clean = request.args.get('url_to_clean')
    print url_to_clean
    return render_template('index.html')
    # return render_template('article/index.html', article=article, url=url_to_clean)

    # return render_template('article/index.html')


def gen(camera):
    while True:
        if config.live_preview_with_detection:
            frame, found_obj = camera.get_object(object_classifier)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else:
            frame = camera.get_frame()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed1')
def video_feed1():
    return Response(gen(video_camera_1),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    video_camera_1.vs.start()

    t = threading.Thread(target=check_for_objects, args=())
    t.daemon = True
    t.start()
    app.run(host='0.0.0.0', debug=False, threaded=True)
