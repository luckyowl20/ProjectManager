import json
import os
import shutil

from kivy.config import Config

# icon issue https://github.com/kivy/kivy/issues/2202

Config.set('kivy', 'window_icon', 'icon.png')
Config.set('kivy', 'exit_on_escape', 0)
Config.set('graphics', 'window_state', 'maximized')
Config.set('graphics', 'minimum_width', 1000)
Config.set('graphics', 'width', 1000)
Config.set('graphics', 'minimum_height', 820)
Config.set('graphics', 'height', 820)

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp

from widgets import utils
from widgets.importbutton.ImportButton import ImportPopup
from widgets.navdrawer.ProjectListItem import ProjectListItem
from widgets.WindowManager import WindowManager

kv = Builder.load_file("main.kv")


class MainScreen(Screen):
    """
    The main screen, contains every other screen
    """
    pass


class ProjectManager(MDApp):

    def build(self):
        """
        Builds the main screen as the root widget
        :return: screen
        """
        self.load_settings()
        self.title = "Project Manager v1.0.0"

        # icon issue https://github.com/kivy/kivy/issues/2202
        self.icon = "icon.png"

        utils.project_manager = self
        # Window.bind(on_resize=self.window_resize)
        return MainScreen()

    def on_stop(self):
        try:
            # remove users google login info
            os.remove("token.pickle")
        except FileNotFoundError:
            # no token
            pass

        shutil.rmtree("temp", True)
        os.mkdir("temp")

    def on_start(self):
        """
        Called when the app is launched, initializes important binds and updates widgets if they need to be updated
        :return:
        """
        # TODO: remove all binds and put them into the Window __init__ method
        for index, window in enumerate(utils.windows):
            window.nav_manager = self.root.ids.nav_drawer
            menu_entry = ProjectListItem(window, utils.windows[index].name, self.root.ids.nav_drawer,
                                         text=utils.data[utils.windows[index].name]["title"])
            utils.menu_projects.append(menu_entry)
            self.root.ids.content_drawer.ids.md_list.add_widget(menu_entry)
            window.menu_button.bind(on_release=self.menu_btn_bind)
            window.menu_button.icon_button.bind(on_release=self.menu_btn_bind)

            window.home_button.bind(on_release=self.home_btn_bind)
            window.home_button.icon_button.bind(on_release=self.home_btn_bind)

            self.root.ids.nav_drawer.bind(state=self.close_bind)

    def add_project_card(self, project):
        """
        Adds a new project card to the home page
        :param project: dict key for project in utils.data
        :return: None
        """
        self.root.ids.window_manager.home_screen.home_select_page.add_card(project)

    def close_bind(self, *args):
        """Bind for when the navigation drawer is closed, called when its state changes"""
        if self.root.ids.nav_drawer.state == 'close':
            self.root.ids.content_drawer.ids.settings_expansion.clear_widgets()
            self.root.ids.content_drawer.ids.settings_expansion.height = 0
            self.root.ids.content_drawer.activated = False

    def home_btn_bind(self, *args):
        """TThe bind for the home button, changes the screen to the home screen"""
        self.root.ids.window_manager.current = "home_select"

    def menu_btn_bind(self, *args):
        """Bind for the menu button, opens the navigation drawer"""
        self.root.ids.nav_drawer.set_state("open")

    @staticmethod
    def import_btn_bind(*args):
        """Bind for import button, prompts the import menu"""
        import_popup = ImportPopup()
        import_popup.open_import_popup()

    def remove_menu_entry(self, entry):
        """
        Removes a project from the menu navigation drawer
        :param entry: dict key for project in utils.data
        :return: None
        """
        self.root.ids.content_drawer.ids.md_list.remove_widget(entry)

    def update_nav(self, new_win, add_proj_list, *args):
        """
        Updates the navigation drawer for the new project, binds the new menu and home buttons and adds project to
        the nav drawer under "projects" layout
        :param add_proj_list: bool
            add the new project with a ProjectListItem
        :param new_win: new project
        :param args: button args
        :return: None
        """
        new_win.nav_manager = self.root.ids.nav_drawer
        if add_proj_list:
            new_menu_entry = ProjectListItem(new_win, new_win.name, self.root.ids.nav_drawer,
                                             text=utils.data[new_win.name]["title"])
            utils.menu_projects.append(new_menu_entry)
            self.root.ids.content_drawer.ids.md_list.add_widget(new_menu_entry)
        new_win.menu_button.bind(on_release=self.menu_btn_bind)
        new_win.menu_button.icon_button.bind(on_release=self.menu_btn_bind)

        new_win.home_button.bind(on_release=self.home_btn_bind)
        new_win.home_button.icon_button.bind(on_release=self.home_btn_bind)

    def load_settings(self):
        """Loads the project settings and sets theme and style based on those"""
        with open('settings.json', 'r') as file:
            theme_settings = json.load(file)
        self.theme_cls.theme_style = theme_settings["style"]
        self.theme_cls.primary_palette = theme_settings["theme"]

    # TODO update this to utils.save_settings
    @staticmethod
    def save_settings(new_settings):
        """Saves project preference settings"""
        new_settings["project_path"] = utils.projects_directory
        with open('settings.json', 'w') as file:
            json.dump(new_settings, file)

    @staticmethod
    def window_resize(*args):
        """Makes sure that the window is never smaller than 1000 * 800 and resize widgets when resized"""
        if Window.width < 1000:
            Window.size = (1000, Window.height)

        if Window.height < 820:
            Window.size = (Window.width, 820)
        for layout in utils.info_layouts:
            layout.height = Window.height - 300


if __name__ == "__main__":
    ProjectManager().run()
