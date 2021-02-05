"""
this file can be added to other projects and modified
loads and saves text on all platforms
"""

from kivy.utils import platform
import os
import json
from threading import Lock

is_android = platform == "android"

VERSION = "0.1"

DEFAULT_ZOOM = 10

# Get settings folder path

APP_NAME = "pixgrabber"

if platform == "win":
    PATH = os.path.join(os.environ.get("USERPROFILE"), APP_NAME)
elif platform == "android":
    from android.storage import app_storage_path
    PATH = app_storage_path()
else:
    PATH = os.path.join(os.environ.get("HOME"), APP_NAME)

LOG_PATH = os.path.join(PATH, "log.txt")
SETTINGS_PATH = os.path.join(PATH, "settings.json")

_file_lock = Lock()

DEFAULT_SETTINGS = {
                        "last_zoom_level": DEFAULT_ZOOM,
                        "saved_coords": [],
                        "app_version": VERSION}

def load_Settings():
    """
    returns json object stored on disk returns DEFAULT_SETTINGS if no file found
    """
    data = load(SETTINGS_PATH)
    if data:
        return json.loads(data)
    return DEFAULT_SETTINGS

def save_settings(data):
    save(SETTINGS_PATH, json.dumps(data))

def check_path_exists():
    if not os.path.exists(PATH):
        _file_lock.acquire()
        os.mkdir(PATH)
        _file_lock.release()

def delete_file(path):
    if os.path.exists(path):
        os.remove(path)

def load(path):
    """
    load(str)
    takes in the name of the file to load. Doesnt require full path just the name of the file and extension
    returns loaded json object or None if no file exists
    """
    data = None
    check_path_exists()
    _file_lock.acquire()
    if os.path.exists(path):
        with open(path, "r") as fp:
            data = fp.read()
    _file_lock.release()
    return data

def save(path, data):
    _file_lock.acquire()
    check_path_exists()
    with open(path, "w") as fp:
        fp.write(data)
    _file_lock.release()
