from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder

from scraper import (
    Threads,
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

Builder.load_string("""
<HorizontalSpacer@Widget>:
    size_hint: None, 1
    width: dp(10)

<VerticalSpacer@Widget>:
    size_hint: 1, None
    height: "30dp"

<DownloadBoxContainer>:
    size_hint: 1, 1
    orientation: "vertical"
    listbox: id_listbox
    app: app
    path_textfield: id_path.text
    statusbox: id_statusbox
    progressbar: id_progress_bar

    VerticalSpacer:

    MDBoxLayout:
        size_hint: 1, .1
        orientation: "horizontal"
        spacing: "10dp"

        HorizontalSpacer:
        MDTextField:
            size_hint: .9, None
            height: dp(48)
            mode: "rectangle"
            hint_text: "Url"
            id: id_path
            text: root.path_textfield
        HorizontalSpacer:
        MDFloatingActionButton:
            id: id_fetch_button
            icon: "image-search"
            opposite_colors: True
            elevation: 8
            md_bg_color: 0, 136/255, 204/255, 1
            on_release: root.on_fetch_button()
        MDFloatingActionButton:
            id: id_cancel_button
            icon: "stop"
            opposite_colors: True
            elevation: 8
            md_bg_color: 30/255, 144/255, 255/255, 1
            on_release: root.on_cancel_button()
        MDFloatingActionButton:
            on_release: root.on_start_button()
            id: id_start_button
            icon: "download"
            opposite_colors: True
            elevation: 8
            md_bg_color: 30/255, 144/255, 255/255, 1
        HorizontalSpacer:
    VerticalSpacer:
    ScrollView:
        scroll_type: ["bars", "content"]
        bar_width: "20dp"
        MDList:
            id: id_listbox
    MDProgressBar:
        size_hint: 1, .1
        min: 0
        max: 100
        value: 50
        id: id_progress_bar
    StatusBox:
        orientation: "vertical"
        size_hint: 1, .3
        text: id_status_label.text
        id: id_statusbox
        scrollview: id_scrollview
        label: id_status_label
        ScrollView:
            scroll_type: ["bars"]
            bar_width: "20dp"
            id: id_scrollview
            scroll_y: 0
            MDLabel:
                size_hint_y: None
                height: self.texture_size[1]
                text: root.statusbox.text
                id: id_status_label
""")


class StatusBox(MDBoxLayout):

    text = StringProperty("")
    label = ObjectProperty(None)
    scrollview = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def update(self, name, text):
        self.text += f"[{name}]: {text}\n "
    
    def clear(self):
        self.text = ""


class UrlListItem(OneLineAvatarIconListItem):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class DownloadBoxContainer(MDBoxLayout):

    listbox = ObjectProperty(None)
    path_textfield = ObjectProperty("")
    app = ObjectProperty(None)
    statusbox = ObjectProperty(None)
    progressbar = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def on_start_button(self, *args):
        urls = list(map(lambda listitem : listitem.text, self.listbox.children))
        urls.reverse()
        data = {"urls": urls}
        notify_commander(Message(thread="main", type="start", data=data))

    def on_fetch_button(self, *args):
        if self.path_textfield:
            data = {"url": self.path_textfield}
            notify_commander(Message(thread="main", type="fetch", data=data))
    
    def on_cancel_button(self, *args):
        notify_commander(Message(thread="main", type="cancel"))

    def load_list(self, links):
        self.listbox.clear_widgets()
        for link in links:
            listitem = UrlListItem(
                text=link
            )
            self.listbox.add_widget(listitem)
    
    def add_to_list(self, text):
        listitem = UrlListItem(
                text=text
                )
        self.listbox.add_widget(listitem)
