from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder

Builder.load_file("settings.kv")

class SettingsContainer(MDBoxLayout):
    pass

def _test():
    from kivymd.app import MDApp
    class MyTestApp(MDApp):
        def build(self):
            return SettingsContainer()

    MyTestApp().run()
if __name__ == '__main__':
    _test()