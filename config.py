import secret


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Config(object):
    __metaclass__ = Singleton

    live_preview_with_detection = False
    send_email_notifications = False
    email_send_interval = 60

    email_sender_address = secret.from_email
    email_sender_password = secret.from_email_password
    receiver_email_address = secret.to_email
