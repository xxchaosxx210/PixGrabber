import threading
import queue
import json
import time
import random
import functools

from dataclasses import dataclass

import web

@dataclass
class Message:
    """
    for message handling sending to and from threads
    thread - thread name
    type   - the type of message
    id     - the thread index
    status - the types status
    data   - extra data
    """
    type: str
    thread: str
    id: int = 0
    status: str = ""
    data: dict = None

class Threads:

    """
    static class holding global scope variables
    """
    commander = None
    grunts = []
    commander_queue = queue.Queue()
    stdout_lock = threading.Lock()
    semaphore = threading.Semaphore(10)
    cancel = threading.Event()

class Urls:

    """
    Contains the static containers for holding found image links and URLs
    these functions are thread safe
    """

    links = []
    lock = threading.Lock()

    @staticmethod
    def add_url(url):
        Urls.lock.acquire()
        Urls.links.append(url)
        Urls.lock.release()
    
    @staticmethod
    def is_url_exist(url):
        Urls.lock.acquire()
        index = Urls.links.index(url)
        Urls.lock.release()
        return index > 0

def request_from_url(url):
    cj = web.browser_cookie3.firefox()
    r = web.requests.get(url, cookies=cj)
    return r

def log_thread_safe(message):
    """
    print is synchronized.
    will remove this soon
    """
    Threads.stdout_lock.acquire()
    print(message)
    Threads.stdout_lock.release()

def create_commander(callback):
    """
    create the main handler thread.
    this thread will stay iterating for the
    remainder of the programs life cycle
    """
    Threads.commander = threading.Thread(
        target=commander_thread, kwargs={"callback": callback})
    return Threads.commander

class Grunt(threading.Thread):

    """
    Level 2 HTML parser and image finder thread
    """

    def __init__(self, thread_index, **kwargs):
        super().__init__(**kwargs)
        self.thread_index = thread_index
    
    def run(self):
        Threads.semaphore.acquire()
        if not Threads.cancel.is_set():
            #cj = web.browser_cookie3.firefox()
            pass
        Threads.semaphore.release()
        if Threads.cancel.is_set():
            notify_commander(Message(id=self.thread_index, thread="grunt", status="cancelled", type="finished"))
        else:
            notify_commander(Message(id=self.thread_index, thread="grunt", status="complete", type="finished"))


def commander_thread(callback):
    """
    main handler thread takes in filepath or url
    and then passes onto captain_thread for parsing

    Level 1 parser and image finder thread
    will create grunt threads if any links found on url
    """
    quit = False
    grunts = []
    _task_running = False
    callback(Message(thread="commander", type="message", data={"message": "Commander thread has loaded. Waiting to scan"}))
    # stops code getting to long verbose
    MessageMain = functools.partial(Message, thread="commander", type="message")
    while not quit:
        try:
            # Get the json object from the global queue
            r = Threads.commander_queue.get(0.5)
            if r.thread == "main":
                if r.type == "quit":
                    Threads.cancel.set()
                    callback(Message(thread="commander", type="quit"))
                    quit = True
                elif r.type == "fetch":                
                    if not _task_running:
                        callback(MessageMain(data={"message": "Initializing the global search filter..."}))
                        # compile our filter matches only add those from the filter list
                        web.compile_regex_global_filter()
                        # get the document from the URL
                        callback(MessageMain(data={"message": f"Connecting to {r.data['url']}"}))
                        webreq = request_from_url(r.data["url"])
                        # make sure is a text document to parse
                        ext = web.is_valid_content_type(r.data["url"], webreq.headers["Content-type"], None)
                        if ext == ".html":
                            callback(MessageMain(data={"message": "Parsing HTML Document..."}))
                            # scrape links and images from document
                            scanned_urls = []
                            if web.parse_html(url=r.data["url"], 
                                              html=webreq.text, 
                                              urls=scanned_urls,
                                              images_only=False, 
                                              thumbnails_only=True) > 0:
                                # send the scanned urls to the main thread for processing
                                callback(MessageMain(data={"message": f"Parsing succesful. Found {len(scanned_urls)} links"}))
                                data = {"urls": scanned_urls}
                                reqmsg = Message(thread="commander", type="fetch", status="finished", data=data)
                                callback(reqmsg)
                            else:
                                # Nothing found notify main thread
                                callback(MessageMain(data={"message": "No links found :("}))
                        webreq.close()
                    else:
                        callback(MessageMain(data={"message": "Still scanning for images please press cancel to start a new scan"}))

                elif r.type == "cancel":
                    Threads.cancel.set()

            elif r.thread == "grunt":
                callback(r)

        except queue.Empty as err:
            print(f"Queue error: {err.__str__()}")

        finally:
            if _task_running:
                # check if all grunts are finished if so cleanup
                # and notify main thread
                if len(grunts_alive(grunts)) == 0:
                    Threads.cancel.clear()
                    grunts = []
                    _task_running = False
                    callback(Message(thread="commander", type="complete"))

def grunts_alive(grunts):
    """
    returns a list of grunt threads that are still alive
    """
    return list(filter(lambda grunt : grunt.is_alive(), grunts))
    
def _simulate_grunts(grunts):
    # Debugging thread messaging system and synchronization
    for x in range(50):
        grunt = Grunt(x)
        grunts.append(grunt)
        grunt.start()

def notify_commander(r):
    """
    send_message(object)
    FIFO queue puts a no wait message on the queue

    r - Request namedtuple
    """
    Threads.commander_queue.put_nowait(r)