import smtplib

from email.MIMEImage import MIMEImage
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

# Email you want to send the update from (only works with gmail)


# You can generate an app password here to avoid storing your password in plain text
# https://support.google.com/accounts/answer/185833?hl=en


def send_email(image, config):
    msg_root = MIMEMultipart('related')
    msg_root['Subject'] = 'Security Update'
    msg_root['From'] = config.email_sender_address
    msg_root['To'] = config.receiver_email_address
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
    smtp.login(config.email_sender_address, config.email_sender_password)
    smtp.sendmail(config.email_sender_address, config.receiver_email_address, msg_root.as_string())
    smtp.quit()
