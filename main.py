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

from global_props import (
    Settings
)

from kivy.logger import Logger


class MainContainer(MDBoxLayout):

    download_container = ObjectProperty(None)
    settings_container = ObjectProperty(None)

class MainApp(MDApp):
    
    def on_start(self):
        # load the settings
        settings = Settings.load()
        self.root.settings_container.load_settings(settings)
        # create global thread for handling web requests and worker threads
        commander = create_commander(self.message_from_handler)
        # start the handler thread this will stay looping for the remainder
        # of the app lifecycle
        commander.start()
        super().on_start()
    
    @mainthread
    def message_from_handler(self, msg):
        """
        function callback from the main handler thread
        """
        if msg.thread == "commander":
            if msg.type == "quit":
                self.root.download_container.statusbox.update(
                        "COMMANDER",
                        "I have quit")
            elif msg.type == "message":
                self.root.download_container.statusbox.update(
                        "COMMANDER",
                        msg.data["message"])
            elif msg.type == "fetch":
                if msg.status == "finished":
                    value = len(msg.data.get("urls"))
                    self.root.download_container.progressbar.max = value
                    self.root.download_container.progressbar.value = 0
            elif msg.type == "cancelled":
                self.root.download_container.statusbox.update(
                        "COMMANDER",
                        "Cancelling Tasks...")
            elif msg.type == "complete":
                self.root.download_container.statusbox.update(
                    "COMMANDER",
                    "Task complete"
                )
                self.root.download_container.progressbar.value = 0
                self.root.download_container.path_textfield = ""
        elif msg.thread == "grunt":
            if msg.type == "finished":
                if msg.status == "complete":
                    self.root.download_container.progressbar.value += 1
                elif msg.status == "cancelled":
                    Logger.info(f"GRUNT#{msg.id}: has cancelled")
            elif msg.type == "started":
                Logger.info(f"GRUNT#{msg.id}: has started...")
            elif msg.type == "image":
                if msg.status == "ok":
                    self.root.download_container.statusbox.update(
                        "Image Saved",
                        f"{msg.data['pathname']}")
                
    def on_stop(self):
        if Threads.commander.is_alive():
            notify_commander(Message(thread="main", type="quit"))
            Threads.commander.join()
        return super().on_stop()

def main():
    MainApp().run()

if __name__ == '__main__':
    main()