from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout

from kivy.clock import mainthread

from kivy.properties import (
    ObjectProperty
)

from scraper import (
    create_commander,
    Threads,
    notify_commander
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
    def message_from_handler(self, **kwargs):
        """
        function callback from the main handler thread
        """
        response = kwargs["response"]
        if response == "quit":
            Logger.info("COMMANDER_RESPONSE: I have quit")
        elif response == "start":
            if kwargs["ok"]:
                self.root.download_container.listbox.clear_widgets()
                Logger.info(f"COMMANDER_RESPONSE: {kwargs['message']}")
            else:
                Logger.info(f"COMMANDER_RESPONSE: {kwargs['message']}")
        elif response == "cancelled":
            Logger.info("COMMANDER_RESPONSE: Cancelling tasks...")
        elif response == "complete":
            Logger.info("COMMANDER_RESPONSE: All Tasks have completed")
        elif response == "grunt":
            status = kwargs["status"]
            grunt_id = kwargs["threadid"]
            if status == "complete":
                Logger.info(f"GRUNT: Thread #{grunt_id} has complete")
            elif status == "starting":
                self.root.download_container.add_to_list(f"Thread #{grunt_id} has complete")
            elif status == "cancelled":
                Logger.info(f"GRUNT: Thread #{grunt_id} has cancelled")
            
    
    def on_stop(self):
        if Threads.commander.is_alive():
            notify_commander(thread="main", request="quit")
            Threads.commander.join()
        return super().on_stop()

def main():
    MainApp().run()

if __name__ == '__main__':
    main()