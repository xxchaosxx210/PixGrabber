from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder

from kivy.properties import (
    StringProperty,
    ObjectProperty,
    NumericProperty
)

Builder.load_file("settings.kv")

"""
DEFAULT_SETTINGS = {
    "app_version": VERSION,
    "browser_cookies": {"firefox": True, "chrome": False, "opera": False, "edge": False},
    "proxy": {"enable": False, "ip": "", "port": 0, "username": "", "password": ""},
    "max_connections": 10,
    "connection_timeout": 5,
    "minimum_image_resolution": {"width": 200, "height": 200},
    "thumbnails_only": True,
    "save_path": os.path.join(PATH, DEFAULT_PICTURE_PATH),
    "unique_pathname": True,
    "generate_filenames": {"enabled": True, "name": "image"},
    "images_to_search": {
        "jpg": True, 
        "png": False,
        "gif": False,
        "bmp": False,
        "ico": False,
        "tiff": False,
        "tga": False},
    "filter_search": {
        "filters": []}
    }
"""

class SettingsContainer(MDBoxLayout):

    max_connections_slider = ObjectProperty(None)
    connection_timeout_text = StringProperty("")
    min_width_text = StringProperty("")
    min_height_text = StringProperty("")
    thumbs_only_check = ObjectProperty(None)
    save_path_text = StringProperty("")
    unique_folder_name = ObjectProperty(None)
    gen_filenames = ObjectProperty(None)
    gen_prefix_text = StringProperty("")
    
    def load_settings(self, settings):
        self.max_connections_slider.value = settings["max_connections"]
        self.connection_timeout_text = str(settings["connection_timeout"])

        minsize = settings["minimum_image_resolution"]
        self.min_width_text = str(minsize["width"])
        self.min_height_text = str(minsize["height"])

        self.thumbs_only_check.active = settings["thumbnails_only"]

        self.save_path_text = settings["save_path"]

        self.unique_folder_name.active = settings["unique_pathname"]

        temp = settings["generate_filenames"]
        self.gen_filenames.active = temp["enabled"]
        if temp["enabled"]:
            self.gen_prefix_text = temp["name"]



def _test():
    from kivymd.app import MDApp
    from global_props import Settings
    class MyTestApp(MDApp):
        def build(self):
            return SettingsContainer()
        def on_start(self):
            self.root.load_settings(Settings.load())
            return super().on_start()

    MyTestApp().run()
if __name__ == '__main__':
    _test()