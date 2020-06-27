from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.utils import get_hex_from_color
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog

Builder.load_file("widgets/navdrawer/aboutmenu/AboutContent.kv")


class AboutContent(MDBoxLayout):
    about_label = ObjectProperty()

    def __init__(self, parent, **kwargs):
        super(MDBoxLayout, self).__init__(**kwargs)
        self.app = App.get_running_app()
        parent.about_label = self.about_label


class AboutDialog(MDBoxLayout):
    about_dialog = None
    app = App.get_running_app()

    def __init__(self, **kwargs):
        super(MDBoxLayout, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.dismissed = False
        self.about_label = ObjectProperty()

    def about_menu(self):
        if not self.about_dialog:
            self.about_dialog = MDDialog(
                title=f"[color=%s]About this software[/color]" %
                      get_hex_from_color(self.app.theme_cls.text_color),
                type="custom",
                content_cls=AboutContent(self),
                buttons=[
                    MDRaisedButton(
                        text="CLOSE", text_color=self.app.theme_cls.primary_color,
                        on_release=self.dismiss_dialog
                    )],
                size_hint_x=None, width=dp(850)
            )
        self.about_label.text = self.get_text()
        self.about_dialog.set_normal_height()
        self.about_dialog.open()

    @staticmethod
    def get_text():
        with open("widgets/navdrawer/aboutmenu/about_dialog.txt", "r") as file:
            return file.read()

    def dismiss_dialog(self, *args):
        self.about_dialog.dismiss()
