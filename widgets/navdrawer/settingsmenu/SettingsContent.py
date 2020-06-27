import json

from kivy.app import App
from kivy.lang import Builder
from kivy.utils import get_hex_from_color, get_color_from_hex
from kivymd.color_definitions import colors
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog

from widgets import utils
from widgets.navdrawer.settingsmenu.AppearanceContent import AppearanceContent
from widgets.navdrawer.settingsmenu.PreferencesContent import PreferencesContent

Builder.load_file("widgets/navdrawer/settingsmenu/SettingsContent.kv")


class SettingsContent(MDBoxLayout):
    appearance_dialog = None
    preferences_dialog = None
    
    app = App.get_running_app()

    def __init__(self, **kwargs):
        super(MDBoxLayout, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.appearance = self.app.theme_cls.primary_palette
        self.style = self.app.theme_cls.theme_style
        self.appearance_dismissed = False
        self.switch_active = True
        self.appearance_dialog = self.appearance_menu(False)

    def appearance_menu(self, open_dialog=True):
        if not self.appearance_dialog:
            if self.appearance_dismissed:
                self.appearance_dismissed = False
                self.appearance = self.app.theme_cls.primary_palette
                self.style = self.app.theme_cls.theme_style

            cancel_button = MDFlatButton(
                text="CANCEL", text_color=self.app.theme_cls.text_color,
                on_release=self.close_appearance_dialog
            )
            self.appearance_dialog = MDDialog(
                title=f"[color=%s]Change project appearance[/color]" %
                      get_hex_from_color(self.app.theme_cls.text_color),
                type="custom",
                content_cls=AppearanceContent(cancel_button),
                buttons=[
                    cancel_button,
                    MDRaisedButton(
                        text="SAVE", text_color=self.app.theme_cls.primary_color,
                        on_release=self.save_appearance
                    )]
            )
        if open_dialog:
            self.appearance_dialog.content_cls.active_theme = self.appearance
            self.appearance_dialog.buttons[0].text_color = self.app.theme_cls.text_color
            self.switch_active = self.appearance_dialog.content_cls.ids.style_switch.active
            self.appearance_dialog.bind(on_dismiss=self.close_appearance_dialog)
            self.appearance_dialog.set_normal_height()
            self.appearance_dialog.open()
        else:
            return self.appearance_dialog

    # called when dialog is dismissed and reverts to previous theme and style settings
    def close_appearance_dialog(self, *args):
        # to make sure we don't get infinite recursion
        if not self.appearance_dismissed:

            self.app.theme_cls.primary_palette = self.appearance
            self.app.theme_cls.theme_style = self.style
            self.appearance_dismissed = True
            self.appearance_dialog.dismiss()
            self.appearance_dialog.content_cls.ids.style_switch.active = self.switch_active
            # updating the bottom banner
            for layout in utils.bottom_banners:
                layout.md_bg_color = get_color_from_hex(
                    colors[App.get_running_app().theme_cls.theme_style]["CardsDialogs"])
            # there is a chance that the file is no longer in the viewer widget
            try:
                for file in utils.files:
                    file.color = App.get_running_app().theme_cls.text_color
            except ReferenceError:
                pass

        # for resetting the checkbox to the correct one on close
        for index, text in enumerate(utils.checkbox_text):
            if text == self.app.theme_cls.primary_palette:
                utils.theme_checkboxes[index].active = True
            else:
                utils.theme_checkboxes[index].active = False

        # allowing the dismiss call to be made again after the close has finished
        self.appearance_dismissed = False

    # saves the appearance, theme and style
    def save_appearance(self, *args):
        self.appearance = self.appearance_dialog.content_cls.active_theme
        self.style = self.appearance_dialog.content_cls.active_style
        utils.save_settings({"theme": self.appearance_dialog.content_cls.active_theme,
                             "style": self.appearance_dialog.content_cls.active_style})
        self.app.theme_cls.primary_palette = self.appearance_dialog.content_cls.active_theme
        self.appearance_dismissed = True
        self.appearance_dialog.dismiss()
        self.appearance_dismissed = False
    
    def preferences_menu(self, open_dialog=True):
        if not self.preferences_dialog:
            content = PreferencesContent()
            cancel_button = MDFlatButton(
                text="CANCEL", text_color=self.app.theme_cls.text_color,
                on_release=self.close_preferences_dialog
            )
            self.preferences_dialog = MDDialog(
                title=f"[color=%s]Change app preferences[/color]" %
                      get_hex_from_color(self.app.theme_cls.text_color),
                type="custom",
                content_cls=content,
                buttons=[
                    cancel_button,
                    MDRaisedButton(
                        text="SAVE", text_color=self.app.theme_cls.primary_color,
                        on_release=self.save_preferences
                    )],
                size_hint=(None, None), size=content.size
            )
        self.preferences_dialog.title = f"[color=%s]Change app preferences[/color]" % \
                                        get_hex_from_color(self.app.theme_cls.text_color)
        self.preferences_dialog.buttons[0].text_color = self.app.theme_cls.text_color
        self.preferences_dialog.set_normal_height()
        self.preferences_dialog.open()

    def close_preferences_dialog(self, *args):
        self.preferences_dialog.dismiss()

    def save_preferences(self, *args):
        # TODO update to utils.save_settings()
        utils.app_settings['project_path'] = self.preferences_dialog.content_cls.project_path
        utils.app_settings['default_export_path'] = self.preferences_dialog.content_cls.default_export_path
        utils.app_settings['default_export_type'] = self.preferences_dialog.content_cls.default_export_type

        utils.save_settings(utils.app_settings)

        self.preferences_dialog.dismiss()
