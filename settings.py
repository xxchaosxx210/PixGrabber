from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder

from global_props import Settings

from kivy.properties import (
    StringProperty,
    ObjectProperty
)

from dirdialog import create_dirdialog

Builder.load_file("settings.kv")


class SettingsContainer(MDBoxLayout):

    dirdialog = ObjectProperty(None)

    tga_check = ObjectProperty(None)
    tiff_check = ObjectProperty(None)
    ico_check = ObjectProperty(None)
    bmp_check = ObjectProperty(None)
    gif_check = ObjectProperty(None)
    png_check = ObjectProperty(None)
    jpg_check = ObjectProperty(None)

    max_connections_slider = ObjectProperty(None)
    connection_timeout_text = StringProperty("")

    min_width_text = StringProperty("")
    min_height_text = StringProperty("")

    thumbs_only_check = ObjectProperty(None)

    save_path_text = StringProperty("")
    unique_folder_name = ObjectProperty(None)

    gen_filenames = ObjectProperty(None)
    gen_prefix_text = StringProperty("")

    firefox_check = ObjectProperty(None)
    chrome_check = ObjectProperty(None)
    opera_check = ObjectProperty(None)
    edge_check = ObjectProperty(None)

    skip_file_check = ObjectProperty(None)
    overwrite_check = ObjectProperty(None)
    rename_check = ObjectProperty(None)

    def on_dir_button(self, *args):
        self.dirdialog.path = self.save_path_text
        self.dirdialog.open()

    def on_dirdialog_cancel(self, *args):
        self.dirdialog.dismiss()
    
    def on_dirdialog_ok(self, *args):
        self.save_path_text = self.dirdialog.get_path()
        settings = Settings.load()
        settings["save_path"] = self.save_path_text
        Settings.save(settings)
        self.dirdialog.dismiss()

    def on_file_exists(self, radiobutton):
        settings = Settings.load()
        if self.skip_file_check.active:
            settings["file_exists"] = "skip"
        elif self.overwrite_check.active:
            settings["file_exists"] = "overwrite"
        else:
            settings["file_exists"] = "rename"
        Settings.save(settings)

    def on_image_ext_check(self, checkbox):
        settings = Settings.load()
        ext = settings["images_to_search"]
        ext["jpg"] = self.jpg_check.active
        ext["png"] = self.png_check.active
        ext["gif"] = self.gif_check.active
        ext["bmp"] = self.bmp_check.active
        ext["ico"] = self.ico_check.active
        ext["tiff"] = self.tiff_check.active
        ext["tga"] = self.tga_check.active
        Settings.save(settings)

    def on_gen_filename_check(self, switch):
        settings = Settings.load()
        settings["generate_filenames"]["enabled"] = switch.active
        Settings.save(settings)

    def on_gen_filename_text(self, text):
        if text:
            settings = Settings.load()
            settings["generate_filenames"]["name"] = text
            Settings.save(settings)

    def on_unique_name(self, switch):
        settings = Settings.load()
        settings["unique_pathname"] = switch.active
        Settings.save(settings)

    def on_thumbnails_only(self, switch):
        settings = Settings.load()
        settings["thumbnails_only"] = switch.active
        Settings.save(settings)

    def on_min_width(self, text):
        if text:
            settings = Settings.load()
            settings["minimum_image_resolution"]["width"] = int(text)
            Settings.save(settings)
    
    def on_min_height(self, text):
        if text:
            settings = Settings.load()
            settings["minimum_image_resolution"]["height"] = int(text)
            Settings.save(settings)

    def on_timeout(self, text):
        if text:
            settings = Settings.load()
            settings["connection_timeout"] = int(text)
            Settings.save(settings)

    def on_max_connections(self, slider):
        settings = Settings.load()
        settings["max_connections"] = slider.value
        Settings.save(settings)

    def on_save_path_text(self, *args):
        settings = Settings.load()
        settings["save_path"] = self.save_path_text
        Settings.save(settings)
    
    def on_cookies_checkbox(self, checkbox):
        settings = Settings.load()
        cookies = settings["cookies"]
        cookies["firefox"] = self.firefox_check.active
        cookies["chrome"] = self.chrome_check.active
        cookies["opera"] = self.opera_check.active
        cookies["edge"] = self.edge_check.active
        Settings.save(settings)
    
    def load_settings(self, settings):

        # create the dirdialog
        self.dirdialog = create_dirdialog("Save Path",
        settings["save_path"], self.on_dirdialog_cancel,
        self.on_dirdialog_ok)

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
        self.gen_prefix_text = temp["name"]

        cookies = settings["cookies"]
        self.firefox_check.active = cookies["firefox"]
        self.chrome_check.active = cookies["chrome"]
        self.opera_check.active = cookies["opera"]
        self.edge_check.active = cookies["edge"]

        i = settings["images_to_search"]
        self.jpg_check.active = i["jpg"]
        self.png_check.active = i["png"]
        self.gif_check.active = i["gif"]
        self.bmp_check.active = i["bmp"]
        self.ico_check.active = i["ico"]
        self.tiff_check.active = i["tiff"]
        self.tga_check.active = i["tga"]

        i = settings["file_exists"]
        if i == "skip":
            self.skip_file_check.active = True
        elif i == "overwrite":
            self.overwrite_check.active = True
        else:
            self.rename_check.active = True


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