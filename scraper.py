import threading
import queue
import json
import time
import random

class Threads:

    commander = None
    grunts = []
    commander_queue = queue.Queue()
    stdout_lock = threading.Lock()
    semaphore = threading.Semaphore(10)
    cancel = threading.Event()

def log_thread_safe(message):
    Threads.stdout_lock.acquire()
    print(message)
    Threads.stdout_lock.release()

def create_commander(callback):
    Threads.commander = threading.Thread(
        target=commander_thread, kwargs={"callback": callback})
    return Threads.commander


class Grunt(threading.Thread):

    def __init__(self, thread_index, **kwargs):
        super().__init__(**kwargs)
        self.thread_index = thread_index
    
    def run(self):
        Threads.semaphore.acquire()
        if not Threads.cancel.is_set():
            notify_commander(thread="grunt", threadid=self.thread_index, status="starting")
            for x in range(random.randint(1, 3)):
                time.sleep(random.uniform(0.1, 0.5))
                if Threads.cancel.is_set():
                    break
        Threads.semaphore.release()
        if Threads.cancel.is_set():
            notify_commander(thread="grunt", threadid=self.thread_index, status="cancelled")
        else:
            notify_commander(thread="grunt", threadid=self.thread_index, status="complete")


def commander_thread(callback):
    """
    main handler thread takes in filepath or url
    and then passes onto captain_thread for parsing
    """
    quit = False
    grunts = []
    _task_running = False
    while not quit:
        try:
            msg = json.loads(Threads.commander_queue.get(0.5))
            th = msg["thread"]
            request = msg.get("request", None)
            if th == "main":
                if request == "quit":
                    Threads.cancel.set()
                    callback(response="quit")
                    quit = True
                elif request == "start":                
                    if not _task_running:
                        grunts = []
                        _simulate_grunts(grunts)
                        _task_running = True
                        callback(response="start", ok=True, message="Starting new Task")
                    else:
                        callback(response="start", ok=False, message="Still working on current Task")

                elif request == "cancel":
                    Threads.cancel.set()

            elif th == "grunt":
                status = msg["status"]
                callback(response="grunt", status=status, threadid=msg["threadid"])

        except queue.Empty:
            pass

        finally:
            if _task_running:
                # check if all grunts are finished if so cleanup
                # and notify main thread
                if len(grunts_alive(grunts)) == 0:
                    Threads.cancel.clear()
                    grunts = []
                    _task_running = False
                    callback(response="complete")

def grunts_alive(grunts):
    return list(filter(lambda grunt : grunt.is_alive(), grunts))
    
def _simulate_grunts(grunts):
    for x in range(50):
        grunt = Grunt(x)
        grunts.append(grunt)
        grunt.start()

def notify_commander(**kwargs):
    """
    send_message(object, **kwargs)
    FIFO queue puts a no wait message on the queue
    """
    Threads.commander_queue.put_nowait(json.dumps(kwargs))