from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout

from widgets.navdrawer.settingsmenu.SettingsContent import SettingsContent
from widgets.navdrawer.aboutmenu.AboutMenu import AboutDialog

Builder.load_file("widgets/navdrawer/ContentNavigationDrawer.kv")


class ContentNavigationDrawer(BoxLayout):
    window_manager = ObjectProperty()
    nav_drawer = ObjectProperty()
    md_list = ObjectProperty()

    settings_expansion = ObjectProperty()
    settings_activated = False

    def settings_menu(self):
        if not self.settings_activated:
            widget = SettingsContent()
            self.settings_expansion.add_widget(widget)
            self.settings_expansion.height = widget.height
            self.settings_activated = True
        else:
            self.settings_expansion.clear_widgets()
            self.settings_expansion.height = 0
            self.settings_activated = False

    @staticmethod
    def about_menu():
        dialog = AboutDialog()
        dialog.about_menu()

    def help_menu(self):
        self.window_manager.current = self.window_manager.help_screen.name
