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

    from_email = secret.from_email
    from_email_password = secret.from_email_password
    to_email = secret.to_email
