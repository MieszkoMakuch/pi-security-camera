import threading
import time

import cv2
import imutils
import numpy as np
from imutils.video import VideoStream

from basicmotiondetector import BasicMotionDetector


def synchronized(func):
    func.__lock__ = threading.Lock()

    def synced_func(*args, **kws):
        with func.__lock__:
            return func(*args, **kws)

    return synced_func


class Camera(object):
    motionDetector = BasicMotionDetector(accumWeight=0.5, deltaThresh=5, minArea=500)

    def __init__(self, flip=False, src=0):
        self.vs = VideoStream(src=src)
        self.flip = flip
        time.sleep(2.0)

    def __del__(self):
        self.vs.stop()

    def flip_if_needed(self, frame):
        if self.flip:
            return np.flip(frame, 0)
        return frame

    def get_frame(self):
        frame = self.flip_if_needed(self.vs.read())
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

    def get_object(self, classifier):
        found_objects = False
        frame = self.flip_if_needed(self.vs.read()).copy()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        objects = self.get_objects(classifier, gray)

        if len(objects) > 0:
            found_objects = True

        # Draw a rectangle around the objects
        for (x, y, w, h) in objects:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes(), found_objects

    # @synchronized
    def get_objects(self, classifier, gray):
        objects = classifier.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        return objects

    def get_object_with_basic_motion_detection(self):
        frames = []
        found_objects = False
        frame = self.vs.read()
        frame = imutils.resize(frame, width=500)
        # convert the frame to grayscale, blur it slightly, update
        # the motionDetector detector
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        locations_containing_motion = Camera.motionDetector.update(gray)
        # we should allow the motionDetector detector to "run" for a bit
        # and accumulate a set of frames to form a nice average
        if Camera.motionDetector.scanned_frames_counter < 32:
            frames.append(frame)

        else:
            # otherwise, check to see if motionDetector was detected
            if len(locations_containing_motion) > 0:
                found_objects = True
                # initialize the minimum and maximum (x, y)-coordinates,
                # respectively
                (minX, minY) = (np.inf, np.inf)
                (maxX, maxY) = (-np.inf, -np.inf)

                # loop over the locations of motionDetector and accumulate the
                # minimum and maximum locations of the bounding boxes
                for l in locations_containing_motion:
                    (x, y, w, h) = cv2.boundingRect(l)
                    (minX, maxX) = (min(minX, x), max(maxX, x + w))
                    (minY, maxY) = (min(minY, y), max(maxY, y + h))

                # draw the bounding box
                cv2.rectangle(frame, (minX, minY), (maxX, maxY),
                              (0, 0, 255), 3)

            frames.append(frame)

        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes(), found_objects
