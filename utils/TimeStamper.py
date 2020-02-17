from datetime import datetime


class TimeString:

    @staticmethod
    def now():
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
