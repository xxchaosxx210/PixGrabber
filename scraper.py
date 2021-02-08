import threading
import queue
import json
import time
import random
import functools
import os
from io import BytesIO
from PIL import Image

from dataclasses import dataclass

from global_props import Settings

from debug import Debug

import web

@dataclass
class Message:
    """
    for message handling sending to and from threads
    thread - thread name
    type   - the type of message
    id     - the thread index
    status - the types status
    data   - extra data. Depends on message type
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
    # commander thread reference
    commander = None
    # global list for containing runnning threads
    grunts = []
    # commander thread messaging queue
    commander_queue = queue.Queue()
    # lock for the print function. Used for debugging
    # will remove later
    stdout_lock = threading.Lock()
    # global semaphore. this is related to max_connections
    # found in the settings file
    semaphore = threading.Semaphore(10)
    # global event to cancel current running task
    cancel = threading.Event()

class Urls:

    """
    thread safe container class for storing global links
    this is to check there arent duplicate links
    saves a lot of time and less scraping
    """

    links = []
    lock = threading.Lock()

    @staticmethod
    def clear():
        Urls.lock.acquire()
        Urls.links.clear()
        Urls.lock.release()

    @staticmethod
    def add_url(url):
        Urls.lock.acquire()
        Urls.links.append(url)
        Urls.lock.release()
    
    @staticmethod
    def url_exists(url):
        Urls.lock.acquire()
        try:
            index = Urls.links.index(url)
        except ValueError:
            index = -1
        finally:
            Urls.lock.release()
        return index >= 0


class ImageFile:

    """
    thread safe. saves bytes read from requests
    and saves to disk
    """

    file_lock = threading.Lock()

    @staticmethod
    def write_to_file(path, filename, bytes_stream):
        ImageFile.file_lock.acquire()
        if not os.path.exists(path):
            os.mkdir(path)
        with open(os.path.join(path, filename), "wb") as fp:
            fp.write(bytes_stream.getbuffer())
            fp.close()
        ImageFile.file_lock.release()


def request_from_url(url):
    """
    request_from_url(str)

    gets the request from url and returns the requests object
    """
    cj = web.browser_cookie3.firefox()
    r = web.requests.get(url, 
                        cookies=cj, 
                        headers={"User-Agent": web.FIREFOX_USER_AGENT})
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

def download_image(path, filename, response):
    """
    download_image(str, str, object)

    path should be the file path, filename should be the name of the file
    os.path.join is used to append path to filename
    response is the response returned from requests.get
    """
    # read from socket
    # store in memory
    # images shouldnt be too large
    byte_stream = BytesIO()
    for buff in response.iter_content(1000):
        byte_stream.write(buff)
    # load image from buffer io
    image = Image.open(byte_stream)
    width, height = image.size
    # if image requirements met then save
    if width > 200 and height > 200:
        ImageFile.write_to_file(path, filename, byte_stream)
    byte_stream.close()        
    image.close()


class Grunt(threading.Thread):

    """
    Worker thread which will search for images on the url passed into __init__
    """

    def __init__(self, thread_index, url, settings, **kwargs):
        """
        __init__(int, str, **kwargs)
        thread_index should be a unique number
        this can be used to create a unique filename
        and can also identify the thread
        first thread will be 0 and indexed that way
        url is the universal resource locator to search and parse
        """
        super().__init__(**kwargs)
        self.thread_index = thread_index
        self.url = url
        self.settings = settings
    
    def run(self):
        # partial function to avoid repetitive typing
        GruntMessage = functools.partial(Message, id=self.thread_index, thread="grunt")
        Threads.semaphore.acquire()
        if not Threads.cancel.is_set():
            notify_commander(GruntMessage(status="ok", type="scanning"))
            # request the url
            r = request_from_url(self.url)
            ext = web.is_valid_content_type(self.url, r.headers.get("Content-Type"), None)
            if ".html" == ext:
                imgs = []
                # parse the document and search for images only
                if web.parse_html(self.url, r.text, imgs, images_only=True, thumbnails_only=False) > 0:
                    r.close()

                    for index, imgurl in enumerate(imgs):
                        # check if url has already in global list
                        if not Urls.url_exists(imgurl):
                            # its ok then add it to the global list
                            Urls.add_url(imgurl)
                            # download each one and save it
                            imgresp = request_from_url(imgurl)
                            # check the content-type matches and image
                            ext = web.is_valid_content_type(imgurl, imgresp.headers.get("Content-Type"), None)
                            if ext in web.IMAGE_EXTS:
                                # if image then create a file path and check
                                # the image resolution size matches
                                # if it does then save to file
                                path = os.path.join(os.getcwd(), "test")
                                filename = f"test{self.thread_index}_{index}{ext}"
                                download_image(path, filename, imgresp)
                            # close the image request handle
                            imgresp.close()
            else:
                if ext in web.IMAGE_EXTS:
                    if not Urls.url_exists(self.url):
                        Urls.add_url(self.url)
                        path = os.path.join(os.getcwd(), "test")
                        filename = f"test{self.thread_index}{ext}"
                        download_image(path, filename, r)
                r.close()
        Threads.semaphore.release()
        if Threads.cancel.is_set():
            notify_commander(GruntMessage(status="cancelled", type="finished"))
        else:
            notify_commander(GruntMessage(status="complete", type="finished"))


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
    # settings dict will contain the settings at start of scraping
    settings = {}
    while not quit:
        try:
            # Get the json object from the global queue
            r = Threads.commander_queue.get(0.5)
            if r.thread == "main":
                if r.type == "quit":
                    Threads.cancel.set()
                    callback(Message(thread="commander", type="quit"))
                    quit = True
                elif r.type == "start":
                    if not _task_running:
                        grunts = []
                        _task_running = True

                        # load the settings from file
                        # create a new instance of it in memory
                        # we dont want these values to change
                        # whilst downloading and saving to file
                        settings = dict(Settings.load())

                        callback(MessageMain(data={"message": "Starting Threads..."}))
                        for thread_index, url in enumerate(r.data["urls"]):
                            grunts.append(Grunt(thread_index, url, settings))
                        for _grunt in grunts:
                            _grunt.start()

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
            
            elif r.thread == "settings":
                callback(MessageMain(data=r.data))

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
                    Urls.clear()
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