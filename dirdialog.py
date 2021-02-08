from kivy.lang import Builder
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.list import OneLineIconListItem

from kivy.utils import platform

if platform == "win":
    from win32.win32api import GetLogicalDriveStrings

from kivy.properties import (
    ObjectProperty,
    StringProperty
)

import os

Builder.load_file("dirdialog.kv")


class FolderListItem(OneLineIconListItem):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class FolderBackListItem(OneLineIconListItem):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Content(MDBoxLayout):

    path = StringProperty("")
    dirlist = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


def create_dirdialog(title, path, on_cancel, on_ok):
    buttons = [
        MDFlatButton(text="Close", on_release=on_cancel),
        MDFlatButton(text="OK", on_release=on_ok)
    ]
    return DirDialog(
        path=path,
        title=title,
        auto_dismiss=False,
        content_cls=Content(),
        buttons=buttons)


class DirDialog(MDDialog):

    def __init__(self, path="", **kwargs):
        super().__init__(**kwargs)
        self.content_cls.path = path
    
    def set_path(self, path):
        """
        set_path(str)
        Sets the directory path
        """
        # clear the MDList
        self.content_cls.dirlist.clear_widgets()
        # Create a Folder back item append it to the top of the MDList
        folder_back = FolderBackListItem(on_press=self.on_clicked_back)
        self.content_cls.dirlist.add_widget(folder_back)
        # Initialize the path
        self.content_cls.path = path

        # Windows Specific
        # add the drive paths if windows
        if platform == "win":
            for drive_letter in GetLogicalDriveStrings().split("\x00"):
                if drive_letter:
                    item = FolderListItem(text=drive_letter, 
                    on_press=self.on_clicked_folder)
                    self.content_cls.dirlist.add_widget(item)

        folderitems = os.listdir(path)
        for folderitem in folderitems:
            fullpath = os.path.join(path, folderitem)
            if os.path.isdir(fullpath):
                item = FolderListItem(text=folderitem, 
                on_press=self.on_clicked_folder)
                self.content_cls.dirlist.add_widget(item)
    
    def on_clicked_folder(self, listitem):
        full_path = os.path.join(self.content_cls.path, listitem.text)
        if os.path.exists(full_path):
            self.set_path(full_path)
    
    def on_clicked_back(self, *args):
        self.set_path(os.path.dirname(self.content_cls.path))
    
    def on_open(self, *args):
        self.set_path(self.path)
    
    def get_path(self):
        return self.content_cls.path