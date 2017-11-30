import smtplib

from email.MIMEImage import MIMEImage
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

# Email you want to send the update from (only works with gmail)


# You can generate an app password here to avoid storing your password in plain text
# https://support.google.com/accounts/answer/185833?hl=en

# Email you want to send the update to
from config import Config


def send_email(image):
    msg_root = MIMEMultipart('related')
    msg_root['Subject'] = 'Security Update'
    msg_root['From'] = Config.from_email
    msg_root['To'] = Config.to_email
    msg_root.preamble = 'Raspberry pi security camera update'

    msg_alternative = MIMEMultipart('alternative')
    msg_root.attach(msg_alternative)
    msg_text = MIMEText('Smart security cam found object')
    msg_alternative.attach(msg_text)

    msg_text = MIMEText('<img src="cid:image1">', 'html')
    msg_alternative.attach(msg_text)

    msg_image = MIMEImage(image)
    msg_image.add_header('Content-ID', '<image1>')
    msg_root.attach(msg_image)

    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.starttls()
    smtp.login(Config.from_email, Config.from_email_password)
    smtp.sendmail(Config.from_email, Config.to_email, msg_root.as_string())
    smtp.quit()
