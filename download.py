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
    width: dp(48)

<VerticalSpacer@Widget>:
    size_hint: 1, None
    height: dp(48)
<DownloadBoxContainer>:
    size_hint: 1, 1
    orientation: "vertical"
    listbox: id_listbox
    app: app
    path_textfield: id_path.text
    statusbox: id_statusbox

    MDFloatLayout:
        size_hint: 1, .1
        orientation: "horizontal"
        MDTextField:
            pos_hint: {"left": 1, "top": 1}
            size_hint: .9, None
            height: dp(48)
            mode: "rectangle"
            hint_text: "Url"
            id: id_path
            text: root.path_textfield
        MDFloatingActionButton:
            pos_hint: {"top": 1, "left": 0, "right": .8}
            icon: "stop"
            opposite_colors: True
            elevation: 8
            md_bg_color: 30/255, 144/255, 255/255, 1
            on_release: root.on_cancel_button()
        MDFloatingActionButton:
            pos_hint: {"top": 1, "left": 0, "right": 1}
            icon: "download"
            opposite_colors: True
            elevation: 8
            md_bg_color: 30/255, 144/255, 255/255, 1
            on_release: root.on_fetch_button()
    VerticalSpacer:
    ScrollView:
        scroll_type: ["bars"]
        bar_width: "20dp"
        MDList:
            id: id_listbox
    MDProgressBar:
        size_hint: 1, .1
        min: 0
        max: 100
        value: 50
        id: progress_bar
    StatusBox:
        orientation: "vertical"
        size_hint: 1, .3
        text: id_status_label.text
        id: id_statusbox
        scrollview: id_scrollview
        ScrollView:
            scroll_type: ["bars"]
            bar_width: "20dp"
            id: id_scrollview
            MDLabel:
                size_hint_y: None
                height: self.texture_size[1]
                text: root.statusbox.text
                id: id_status_label
""")

class StatusBox(MDBoxLayout):

    text = StringProperty("")
    scrollview = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def update(self, name, text):
        self.text += f"[{name}]: {text}\n "


class UrlListItem(OneLineAvatarIconListItem):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class DownloadBoxContainer(MDBoxLayout):

    listbox = ObjectProperty(None)
    path_textfield = ObjectProperty("")
    app = ObjectProperty(None)
    statusbox = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_fetch_button(self):
        data = {"url": "http://vintage-erotica-forum.com/t18747-p79-milena-velba-cze.html"}
        notify_commander(Message(thread="main", type="fetch", data=data))
    
    def on_cancel_button(self):
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