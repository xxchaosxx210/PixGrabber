from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder

from scraper import (
    notify_commander,
    Message
)

from kivymd.uix.list import (
    OneLineAvatarIconListItem
)

from kivy.properties import (
    ObjectProperty,
    StringProperty
)

Builder.load_file("download.kv")


class StatusBox(MDBoxLayout):

    text = StringProperty("")
    label = ObjectProperty(None)
    scrollview = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def update(self, name, text):
        self.text += f"[{name}]: {text}\n "
        self.scrollview.scroll_to
    
    def clear(self):
        self.text = ""


class UrlListItem(OneLineAvatarIconListItem):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class DownloadBoxContainer(MDBoxLayout):

    path_textfield = StringProperty("")
    app = ObjectProperty(None)
    statusbox = ObjectProperty(None)
    progressbar = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def on_start_button(self, *args):
        notify_commander(Message(thread="main", type="start"))

    def on_fetch_button(self, *args):
        if self.path_textfield:
            data = {"url": self.path_textfield}
            notify_commander(Message(thread="main", type="fetch", data=data))
    
    def on_cancel_button(self, *args):
        notify_commander(Message(thread="main", type="cancel"))
