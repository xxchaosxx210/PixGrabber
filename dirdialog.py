from kivy.lang import Builder
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton

from kivy.properties import (
    ObjectProperty,
    StringProperty
)

import os

Builder.load_file("dirdialog.kv")

class Content(MDBoxLayout):

    path = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

def create_dirdialog(title, path, on_cancel, on_ok):
    buttons = [
        MDFlatButton(text="Close", id="id_close", on_release=on_cancel),
        MDFlatButton(text="OK", id="id_ok", on_release=on_ok)
    ]
    return DirDialog(
        path=path,
        title=title,
        type="custom",
        auto_dismiss=False,
        content_cls=Content(),
        buttons=buttons)

class DirDialog(MDDialog):

    def __init__(self, path="", **kwargs):
        super().__init__(**kwargs)
        self.path = path