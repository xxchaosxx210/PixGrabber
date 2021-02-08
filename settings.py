from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder

Builder.load_string("""
#:include app_theme.kv
<SettingsContainer>:
    orientation: "vertical"
    VerticalSpacer:
    MDBoxLayout:
        size_hint: 1, None
        height: dp(48)
        orientation: "horizontal"
        HorizontalSpacer:
        MDLabel:
            size_hint: .2, 1
            text: "Max Connections"
        MDSlider:
            min: 1
            max: 30
            id: id_max_connections
            value: 10
        MDTextField:
            size_hint: .2, 1
            hint_text: "Connection Timeout"
            text: "5"
            input_filter: "int"
        HorizontalSpacer:
    MDBoxLayout:
        orientation: "horizontal"
        size_hint: 1, .2
        HorizontalSpacer:
        MDBoxLayout:
            size_hint: None, None
            height: dp(36)
            width: dp(220)
            orientation: "horizontal"
            MDTextField:
                hint_text: "Min image width"
                text: "200"
                input_filter: "int"
                id: id_min_width_text
            HorizontalSpacer:
            MDTextField:
                hint_text: "Min image height"
                text: "200"
                input_filter: "int"
                id: id_min_height_text
        HorizontalSpacer:
        MDBoxLayout:
            orientation: "horizontal"
            size_hint: None, None
            height: dp(36)
            width: dp(220)
            MDLabel:
                text: "Thumbnail links only"
                HorizontalSpacer:
            MDSwitch:
                active: True

    MDBoxLayout:
        orientation: "horizontal"
        MDTextField:
            text: ""
            hint_text: "Save Path"
""")

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