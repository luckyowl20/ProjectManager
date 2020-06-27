from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty
from kivy.utils import get_hex_from_color, get_color_from_hex
from kivymd.color_definitions import colors
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import IRightBodyTouch, OneLineAvatarIconListItem

from widgets import utils

Builder.load_file("widgets/navdrawer/settingsmenu/AppearanceContent.kv")


class ThemeListItem(OneLineAvatarIconListItem):
    divider = None
    parent_object = ObjectProperty()
    icon = StringProperty(defaultvalue="")

    @staticmethod
    def get_active_theme(text, checkbox):
        utils.theme_checkboxes.append(checkbox)
        utils.checkbox_text.append(text)
        if App.get_running_app().theme_cls.primary_palette == text:
            return True
        else:
            return False


# simple checkbox button on the right
class AppearanceContainer(IRightBodyTouch, MDBoxLayout):
    adaptive_width = True


class AppearanceContent(MDBoxLayout):
    active_theme = StringProperty(defaultvalue="Blue")
    active_style = StringProperty(defaultvalue="Dark")

    def __init__(self, cancel_button, **kwargs):
        super(MDBoxLayout, self).__init__(**kwargs)
        self.cancel_button = cancel_button
        self.app = App.get_running_app()

    def set_theme(self, instance_check, item_text):
        instance_check.active = True
        check_list = instance_check.get_widgets(instance_check.group)
        for check in check_list:
            if check != instance_check:
                check.active = False
                instance_check.state = 'down'
        self.active_theme = item_text
        self.app.theme_cls.primary_palette = item_text

        # update separator colors
        for separator in utils.separators:
            separator.md_bg_color = self.app.theme_cls.primary_light

    def set_style(self, style_switch, dialog_object):
        # global files
        if style_switch.active:
            self.active_style = "Dark"
        else:
            self.active_style = "Light"
        self.cancel_button.theme_text_color = "Primary"
        self.app.theme_cls.theme_style = self.active_style
        dialog_object.title = f"[color=%s]Change project appearance[/color]" \
                              % get_hex_from_color(App.get_running_app().theme_cls.text_color)
        for banner in utils.bottom_banners:
            banner.md_bg_color = get_color_from_hex(colors[App.get_running_app().theme_cls.theme_style]["CardsDialogs"])
        # there is a chance that the file is no longer in the viewer widget
        try:
            for file in utils.files:
                file.color = self.app.theme_cls.text_color
        except ReferenceError:
            pass

        # update all the checkbox colors in the todo_lists
        if self.app.theme_cls.theme_style == "Dark":
            checkbox_color = [1, 1, 1, 0.7]
        else:
            checkbox_color = [0, 0, 0, 0.54]

        for checkbox in utils.todo_checkboxes:
            if not checkbox.item_checkbox.active:
                checkbox.item_checkbox.color = checkbox_color
        for card in utils.project_cards:
            card.update_colors()

    @staticmethod
    def get_theme_style():
        app = App.get_running_app()
        if app.theme_cls.theme_style == "Dark":
            return True
        else:
            return False
