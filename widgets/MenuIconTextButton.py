from kivy.metrics import dp
from kivy.uix.button import Button
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel


class MenuIconTextButton(MDBoxLayout, Button):
    def __init__(self, icon, text, **kwargs):
        super(MenuIconTextButton, self).__init__(**kwargs)
        self.size_hint_x = None
        self.adaptive_width = True
        self.background_color = 0, 0, 0, 0

        self.icon = icon
        self.icon_button = MDIconButton(icon=icon, pos_hint={"center_x": 0.5, "center_y": 0.5})
        self.label = MDLabel(text=text, halign='left', pos_hint={"center_y": 0.5},
                             theme_text_color="Primary", size_hint_x=None, width=dp(56))

        self.add_widget(self.icon_button)
        self.add_widget(self.label)
