from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout

from kivy.clock import mainthread

from kivy.properties import (
    ObjectProperty
)

from scraper import (
    create_commander,
    Threads,
    notify_commander,
    Message
)

from kivy.logger import Logger

class MainContainer(MDBoxLayout):

    download_container = ObjectProperty(None)

class MainApp(MDApp):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # create global thread for handling web requests and worker threads
        commander = create_commander(self.message_from_handler)
        commander.start()
    
    def on_start(self):
        # start the handler thread this will stay looping for the remainder
        # of the app lifecycle
        super().on_start()
    
    @mainthread
    def message_from_handler(self, msg):
        """
        function callback from the main handler thread
        """
        if msg.thread == "commander":
            if msg.type == "quit":
                Logger.info("COMMANDER_RESPONSE: I have quit")
            elif msg.type == "start":
                if msg.status == "ok":
                    self.root.download_container.listbox.clear_widgets()
                    Logger.info(f"COMMANDER_RESPONSE: Fetching {msg.data['url']} ...")
                else:
                    Logger.info("COMMANDER_RESPONSE: Task already running")
            elif msg.type == "cancelled":
                Logger.info("COMMANDER_RESPONSE: Cancelling tasks...")
            elif msg.type == "complete":
                Logger.info("COMMANDER_RESPONSE: All Tasks have completed")
              
        elif msg.thread == "grunt":
            if msg.type == "finished":
                if msg.status == "complete":
                    Logger.info(f"GRUNT#{msg.id}: has completed")
                elif msg.status == "cancelled":
                    Logger.info(f"GRUNT#{msg.id}: has cancelled")
            elif msg.type == "started":
                Logger.info(f"GRUNT#{msg.id}: has started")
                
            
    
    def on_stop(self):
        if Threads.commander.is_alive():
            notify_commander(Message(thread="main", type="quit"))
            Threads.commander.join()
        return super().on_stop()

def main():
    MainApp().run()

if __name__ == '__main__':
    main()