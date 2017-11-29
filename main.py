import threading
import time

import cv2
from flask import Flask, render_template, Response

from camera import VideoCamera
from mail import sendEmail

email_update_interval = 6  # sends an email only once in this time interval
video_camera = VideoCamera(flip=False)  # creates a camera object, flip vertically

fullbody_classifier_path = "models/fullbody_recognition_model.xml"
facial_classifier_path = "models/facial_recognition_model.xml"
upperbody_classifier_path = "models/upperbody_recognition_model.xml"

object_classifier = cv2.CascadeClassifier(fullbody_classifier_path)  # an opencv classifier

# App Globals (do not edit)
app = Flask(__name__)
last_epoch = 0


def check_for_objects():
    global last_epoch
    while True:
        try:
            frame, found_obj = video_camera.get_object(object_classifier)
            if found_obj and (time.time() - last_epoch) > email_update_interval:
                last_epoch = time.time()
                print "Sending email..."
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
        frame, found_obj = camera.get_object(object_classifier)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen(video_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    video_camera.vs.start()
    t = threading.Thread(target=check_for_objects, args=())
    t.daemon = True
    t.start()
    app.run(host='0.0.0.0', debug=False)
