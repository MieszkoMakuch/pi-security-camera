# Raspberry Pi Smart Security Camera
Security camera running open-cv for object and motion detection. The camera will send an email with an image of any objects it detects. It also runs a server that provides a web interface with live stream video.

Informations about:

- **Setup**
- **Installing Dependencies**
- **Saving email addresses**
- **Running the Program**

are available under the *Functionality* section.

## Functionality
### Email notifications

You can specify receiver's and sender email address though web interface:

![emailNotifications](https://raw.githubusercontent.com/MieszkoMakuch/pi-security-camera/master/readme_files/emailNotifications.png)

After detecting an object the camera will sent and email with a image preview.

Email notification             |  Email with image preview
:-------------------------:|:-------------------------:
![MotionDetection](https://raw.githubusercontent.com/MieszkoMakuch/pi-security-camera/master/readme_files/emailNotificationPhone.jpg)  |  ![MotionDetection](https://raw.githubusercontent.com/MieszkoMakuch/pi-security-camera/master/readme_files/emailPreview.jpg)

### Object detection

You can also specify what will trigger a security alert. Here are some examples:

#### Motion detection
![MotionDetection](https://raw.githubusercontent.com/MieszkoMakuch/pi-security-camera/master/readme_files/MotionDetection.png)
#### Face detection
![FaceDetection](https://raw.githubusercontent.com/MieszkoMakuch/pi-security-camera/master/readme_files/FaceDetection.png)
#### Cat face detection
![CatFaceDetection](https://raw.githubusercontent.com/MieszkoMakuch/pi-security-camera/master/readme_files/CatFaceDetection.png)

**Note that some of the available detectors are experimental and their accuracy leaves something to be desired. Particularly:**
- Upper body detection
- Smile detection
- Silverware detection


## Setup

This project uses a USB Camera to stream video. Before running the code, make sure you have connected a USB Camera to your device.


## Installing Dependencies

This project uses openCV to detect objects in the video feed. You can install openCV by using the following [tutorial](http://www.pyimagesearch.com/2016/04/18/install-guide-raspberry-pi-3-raspbian-jessie-opencv-3/). In this project Python 2.7 version was used.

The installation took about 1-2 hours on Raspberry Pi 3 Model B, but it would be considerably slower on a less powerful board like the Raspberry Pi Zero (it may even take about 8 hours).

The tutorial will prompt you to create a virtual environment. Make sure you are using the virtual environment by typing the following commands

```bash
source ~/.profile
workon cv
```

Next, navigate to the repository directory

```bash
cd pi-security-camera
```

and install the dependencies for the project

```bash
pip install -r requirements.txt
```

*Note: If you're running python3, you'll have to change the import statements at the top of the `mail_config.py` file*

```python
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
```

## Saving email addresses

If you don't wand to specify email addresses each time you run the app you can save them in `secret.py` file.
```python
# Email you want to send the update from (only works with gmail)
from_email = ''           # 'example@gmail.com' - must be a gmail account!
from_email_password = ''  # 'password'

# Email you want to send the update to:
to_email = ''             # 'example@example.com'
```
Replace empty strings - `''` with with your own email/credentials. Application logs into a gmail SMTP server and sends an email with an image of the object detected by the security camera..

## Running the Program

Run the program

```bash
source ~/.profile
workon cv
python application.py
```

You can view a live stream by visiting the ip address of your Raspberry Pi in a browser on the same network. You can find the ip address of your Raspberry Pi by typing `ifconfig` in the terminal and looking for the `inet` or `wlan` address.

Visit `<raspberrypi_ip>:5000` in your browser to view the stream.

Note: To view the live stream on a different network than your Raspberry Pi, you can use [ngrok](https://ngrok.com/) to expose a local tunnel. Once downloaded, run ngrok with `./ngrok http 5000` and visit one of the generated links in your browser. 