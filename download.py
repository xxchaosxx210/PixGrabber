from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder
from scraper import (
    Threads,
    notify_commander
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
        canvas.before:
            Color:
                rgba: 204/255, 230/255, 255/255, 1
            Rectangle:
                pos: self.pos
                size: self.size
        MDList:
            id: id_listbox
        
    MDProgressBar:
        size_hint: 1, .1
        min: 0
        max: 100
        value: 50
        id: progress_bar""")

class UrlListItem(OneLineAvatarIconListItem):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class DownloadBoxContainer(MDBoxLayout):

    listbox = ObjectProperty(None)
    path_textfield = ObjectProperty("")
    app = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_fetch_button(self):
        notify_commander(
            thread="main",
            request="start", 
            location_path="http://www.somewhere.com")
    
    def on_cancel_button(self):
        notify_commander(thread="main", request="cancel")

    def load_list(self, links):
        self.listbox.clear_widgets()
        for link in links:
            listitem = UrlListItem(
                text=link
            )
            self.listbox.add_widget(listitem)