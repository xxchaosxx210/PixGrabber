from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout

from kivy.properties import (
    ObjectProperty
)

from scraper import Handler

from debug import Debug

class MainContainer(MDBoxLayout):

    download_container = ObjectProperty(None)

class MainApp(MDApp):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # create global thread for handling web requests and worker threads
        Handler.thread = Handler(self.message_from_handler)
    
    def on_start(self):
        # start the handler thread this will stay looping for the remainder
        # of the app lifecycle
        Handler.thread.start()
    
    def message_from_handler(self, response, **kwargs):
        """
        function callback from the main handler thread
        """
        if response == "start-thread":
            Debug.log("HANDLER_THREAD", self, thread_start=True)
        elif response == "quit":
            Debug.log("HANDLER_THREAD", self, quit=True)
    
    def on_stop(self):
        if Handler.thread.is_alive():
            Handler.thread.send_message(request="quit")
            Handler.thread.join()
        return super().on_stop()

def main():
    MainApp().run()

if __name__ == '__main__':
    main()