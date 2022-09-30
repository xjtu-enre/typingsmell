import threading
import time


class MyThread(threading.Thread):

    def __init__(self, target_func=None, delay=0, args=()):
        super(MyThread, self).__init__()
        self.func = target_func
        self.args = args
        self.res = None
        self.delay = delay

    def run(self) -> None:
        time.sleep(self.delay)
        self.res = self.func(*self.args)

    def get_res(self):
        try:
            return self.res
        except Exception:
            return None
