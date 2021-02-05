import threading
import queue
import json

class Handler(threading.Thread):

    """
    Thread for handling scraping and the worker threads
    """

    # needs to be institated in main thread
    # global thread reference
    thread = None

    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.msg = queue.Queue()

    def run(self):
        self.callback("start-thread")
        kill = threading.Event()
        while not kill.is_set():
            try:
                msg = json.loads(self.msg.get(1))
                request = msg["request"]
                if request == "start":
                    # start scanning
                    self.callback("start")
                elif request == "quit":
                    self.callback("quit")
                    kill.set()
            except queue.Empty:
                pass
    
    def send_message(self, **kwargs):
        self.msg.put_nowait(json.dumps(kwargs))