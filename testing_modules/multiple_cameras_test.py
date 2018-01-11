# USAGE
# python multiple_cameras_test.py

# import the necessary packages
from __future__ import print_function

import datetime
import time

import cv2
import imutils
import numpy as np
import sys
from imutils.video import VideoStream
from pyimagesearch.basicmotiondetector import BasicMotionDetector

# initialize the video streams and allow them to warmup
print("[INFO] starting cameras...")

number_of_cameras = int(1)

cameras = list()

# for camera_id in range(0, number_of_cameras):
#     camera = VideoStream(src=camera_id).start()
#     motion_stream = BasicMotionDetector(minArea=5)
#     cameras.append((camera, motion_stream))

camera_id = 0
while True:

    camera_is_available = cv2.VideoCapture().open(camera_id)
    if not camera_is_available:
        print("Available cameras: " + str(camera_id))
        break

    camera = VideoStream(src=camera_id)
    camera.start()
    motion_stream = BasicMotionDetector(accumWeight=0.2, deltaThresh=5, minArea=500)
    cameras.append((camera, motion_stream))
    camera_id += 1

time.sleep(2.0)

total = 0

# loop over frames from the video streams
while True:
    # initialize the list of frames that have been processed
    frames = []

    # loop over the frames and their respective motionDetector detectors
    for (stream, motion) in cameras:
        # read the next frame from the video stream and resize
        # it to have a maximum width of 400 pixels
        frame = stream.read()
        frame = imutils.resize(frame, width=500)

        # convert the frame to grayscale, blur it slightly, update
        # the motionDetector detector
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        locs = motion.update(gray)

        # we should allow the motionDetector detector to "run" for a bit
        # and accumulate a set of frames to form a nice average
        if total < 32:
            frames.append(frame)
            continue

        # otherwise, check to see if motionDetector was detected
        if len(locs) > 0:
            # initialize the minimum and maximum (x, y)-coordinates,
            # respectively
            (minX, minY) = (np.inf, np.inf)
            (maxX, maxY) = (-np.inf, -np.inf)

            # loop over the locations of motionDetector and accumulate the
            # minimum and maximum locations of the bounding boxes
            for l in locs:
                (x, y, w, h) = cv2.boundingRect(l)
                (minX, maxX) = (min(minX, x), max(maxX, x + w))
                (minY, maxY) = (min(minY, y), max(maxY, y + h))

            # draw the bounding box
            cv2.rectangle(frame, (minX, minY), (maxX, maxY),
                          (0, 0, 255), 3)

        # update the frames list
        frames.append(frame)

    # increment the scanned_frames_counter number of frames read and grab the
    # current timestamp
    total += 1
    timestamp = datetime.datetime.now()
    ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")

    # loop over the frames a second time
    for i, frame in enumerate(frames):
        # draw the timestamp on the frame and display it
        cv2.putText(frame, ts, (10, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
        cv2.imshow("cam" + str(i), frame)

    # check to see if a key was pressed
    key = cv2.waitKey(1) & 0xFF

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

# do a bit of cleanup
print("[INFO] cleaning up...")
cv2.destroyAllWindows()

for (camera, _) in cameras:
    camera.stop()
