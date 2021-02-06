from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder

Builder.load_string("""
<SettingsContainer>:
    orientation: "vertical"
    MDBoxLayout:
        size_hint: 1, None
        height: dp(48)
        orientation: "horizontal"
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
    MDBoxLayout:
        orientation: "horizontal"
        MDTextField:
            text: ""
            hint_text: "Save Path"
""")

class SettingsContainer(MDBoxLayout):
    pass