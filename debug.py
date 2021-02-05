import random
import time
import json
import os
from collections import namedtuple
from kivy.logger import Logger

from global_props import (
    LOG_PATH,
    save,
    load,
    check_path_exists
)


class Debug:
    
    @staticmethod
    def log_object(obj):
        for item in dir(obj):
            Logger.info(f"Object: {item}")
    
    @staticmethod
    def log(event_type="APP", obj=None, **kwargs):
        """
        place key value pairs
        """
        text = f"{event_type}: "
        for key, value in kwargs.items():
            text += f"{key}={value}, "
        if len(text) >= 2:
            Logger.info(text[:-2])
    
    @staticmethod
    def log_file(event, function_name, message):
        """
        log_file(str, str, str)
            saves a log message to the log file on disk
        """

        check_path_exists()
        logs = ""
        if os.path.exists(LOG_PATH):
            stat = os.stat(LOG_PATH)
            if stat.st_size <= 1000000:
                # if logs is less than 1MB then load
                with open(LOG_PATH, "r") as fp:
                    logs = fp.read()
        current_time = time.ctime(time.time())
        logs += f"\n[{current_time}]:{function_name}:{message}"
        save(LOG_PATH, logs)
    
    @staticmethod
    def getlogfromfile():
        return load(LOG_PATH)
    
    @staticmethod
    def save_object_properties(filename, obj):
        text = "\n".join(list(map(lambda item : f"{item}", dir(obj))))
        with open(filename, "w") as fp:
            fp.write(text)
        


        