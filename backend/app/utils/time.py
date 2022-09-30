from datetime import datetime


class FormatTime:
    @classmethod
    def format_time(cls, time: datetime) -> str:
        return time.strftime("%Y-%m-%d-%H-%M-%S").split(' ')[0]

