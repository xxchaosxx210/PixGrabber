import threading
import queue
import json
import time
import random

class Threads:

    commander = None
    captain = None
    grunts = []
    commander_queue = None
    stdout_lock = threading.Lock()

def log_thread_safe(message):
    Threads.stdout_lock.acquire()
    print(message)
    Threads.stdout_lock.release()

def create_commander(callback):
    # global queue for handling requests
    Threads.commander_queue = queue.Queue()
    Threads.commander = threading.Thread(
        target=commander_thread, kwargs={"callback": callback})
    return Threads.commander

def grunt_thread(thread_id, cancel_event):
    log_thread_safe(f"Thread #{thread_id} is starting")
    for x in range(random.randint(1, 3)):
        time.sleep(random.uniform(0.1, 0.5))
        if cancel_event.is_set():
            break
    log_thread_safe(f"Thread #{thread_id} has completed task")

def captain_thread(callback, location_path, cancel_event):
    """
    scrape first page and send out the grunt threads
    """
    Threads.grunts = []
    for index in range(30):
        grunt = threading.Thread(
            target=grunt_thread,
            kwargs={
                "thread_id": index,
                "cancel_event": cancel_event
            }
        )
        Threads.grunts.append(grunt)
        grunt.start()
    for grunt in Threads.grunts:
        while grunt.is_alive():
            if cancel_event.is_set():
                break
        if cancel_event.is_set():
            break
    if cancel_event.is_set():
        notify_commander(thread="captain", request="cancelled")
    
    notify_commander(thread="captain", request="quit")

def commander_thread(callback):
    """
    main handler thread takes in filepath or url
    and then passes onto captain_thread for parsing
    """
    quit = False
    cancel_event = threading.Event()
    while not quit:
        try:
            msg = json.loads(Threads.commander_queue.get(0.5))
            th = msg["thread"]
            request = msg["request"]
            if th == "main":
                if request == "quit":
                    callback(response="quit")
                    quit = True
                elif request == "start":
                    # check if no jobs on
                    # notify main thread
                    if not Threads.captain:
                        # Create one
                        # clear cancel flag
                        cancel_event.clear()
                        Threads.captain = threading.Thread(
                            target=captain_thread, 
                            kwargs={
                                "callback": callback,
                                "location_path": msg["location_path"],
                                "cancel_event": cancel_event
                                })
                        Threads.captain.start()
                        callback(response="start", ok=True)
                    else:
                        # check if still alive
                        if Threads.captain.is_alive():
                            callback(response="start", ok=False)
                elif request == "cancel":
                    cancel_event.set()
            elif th == "captain":
                if request == "quit":
                    reset_captain(cancel_event)
                    callback(response="captain-quit")
                elif request == "cancelled":
                    callback(response="cancelled")
        except queue.Empty:
            pass

def reset_captain(cancel_event):
    cancel_event.clear()
    Threads.captain = None
    
def notify_commander(**kwargs):
    """
    send_message(object, **kwargs)
    FIFO queue puts a no wait message on the queue
    """
    Threads.commander_queue.put_nowait(json.dumps(kwargs))