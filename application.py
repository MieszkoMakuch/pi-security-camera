from __future__ import print_function
from __future__ import print_function
from __future__ import print_function
from __future__ import print_function

import atexit
import threading
import time

from flask import Flask, render_template, Response, request

from camera import Camera
from config import Config
from mail_config import send_email

video_camera_1 = Camera(flip=False, src=0)  # creates a camera object, flip vertically

config = Config()

# App Globals (do not edit)
app = Flask(__name__)


def check_for_objects():
    last_epoch = 0
    while True:
        if config.send_email_notifications:
            if config.classifier_name == 'motion_detector':
                frame, found_obj = video_camera_1.get_object_with_basic_motion_detection()
            else:
                frame, found_obj = video_camera_1.get_object(config.classifier)
            last_epoch = detect_object(found_obj, frame, last_epoch, camera_id="Cam1")
        else:
            time.sleep(2)


def detect_object(found_obj, frame, last_epoch, camera_id="Cam1"):
    if found_obj:
        print("Detected object: %s" % camera_id)
        if (time.time() - last_epoch) > int(config.email_send_interval):
            last_epoch = time.time()
            print("Sending email to " + config.receiver_email_address + "...")
            send_email(frame, config)
            print("done!")
    return last_epoch


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        print('in post request')

        # live preview checkbox
        config.live_preview_with_detection = 'live_preview_with_detection' in request.form

        # classifier radio
        if 'classifier' in request.form:
            classifier_name = request.form['classifier']
            config.set_classifier(classifier_name)

        # email textbox
        config.send_email_notifications = 'send_email_notifications' in request.form
        if config.send_email_notifications:
            receiver_email_address = request.form['receiver_email_address']
            if receiver_email_address:
                print("setting config.receiver_email_address to " + receiver_email_address)
                config.receiver_email_address = receiver_email_address

            email_send_interval = request.form['email_send_interval']
            if email_send_interval: config.email_send_interval = email_send_interval

            # sender email textbox
            sender_email_address = request.form['sender_email_address']
            sender_email_password = request.form['sender_email_password']
            if sender_email_address and sender_email_password:
                config.sender_email_address = sender_email_address
                config.sender_email_password = sender_email_password

        config.to_string()

    return render_template('index.html', classifiers=config.classifierNameLocationDict, config=config)


def gen(camera):
    while True:
        try:
            if config.classifier_name == 'motion_detector':
                frame, found_obj = camera.get_object_with_basic_motion_detection()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            elif config.live_preview_with_detection:
                frame, found_obj = camera.get_object(config.classifier2)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            else:
                frame = camera.get_frame()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        except Exception as e:
            print(e)




@app.route('/video_feed1')
def video_feed1():
    return Response(gen(video_camera_1),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def stop_camera(camera):
    print("Stopping camera..")
    camera.stop()


if __name__ == '__main__':
    video_camera_1.vs.start()

    t = threading.Thread(target=check_for_objects, args=())
    t.daemon = True
    t.start()

    # stop camera on exit
    atexit.register(stop_camera, video_camera_1.vs)

    app.run(host='0.0.0.0', debug=False, threaded=True)
