from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout

from kivy.properties import (
    ObjectProperty
)

class MainContainer(MDBoxLayout):

    download_container = ObjectProperty(None)


class MainApp(MDApp):
    pass

def main():
    MainApp().run()

if __name__ == '__main__':
    main()