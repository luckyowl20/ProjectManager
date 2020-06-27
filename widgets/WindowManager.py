from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import NoTransition, ScreenManager

from widgets import utils
from widgets.homepage.HomePage import HomeScreen
from widgets.Window import Window
from widgets.navdrawer.helpmenu.HelpPage import HelpPage


class WindowManager(ScreenManager):
    nav_drawer = ObjectProperty()

    def __init__(self, **kwargs):
        super(WindowManager, self).__init__(**kwargs)
        # adding all the pages found in the pages json file and creating a new project if none are found

        utils.window_manager = self
        if len(utils.keys) == 1:
            self.add_widget(Window(utils.keys[0], utils.keys[0], utils.keys[0], utils.data[utils.keys[0]]))
        else:
            for window in utils.keys:
                if window == utils.keys[0] and utils.keys[utils.keys.index(window) + 1] is not None:
                    self.add_widget(Window(window, window, utils.keys[utils.keys.index(window) + 1], utils.data[window]))
                elif window == utils.keys[-1] and utils.keys[utils.keys.index(window) - 1] is not None:
                    self.add_widget(Window(window, utils.keys[utils.keys.index(window) - 1], window, utils.data[window]))
                else:
                    self.add_widget(
                        Window(window, utils.keys[utils.keys.index(window) - 1],
                               utils.keys[utils.keys.index(window) + 1],
                               utils.data[window]))
        self.home_screen = HomeScreen(self, "home_select")
        self.add_widget(self.home_screen)
        self.transition = NoTransition()
        self.current = "home_select"

        self.help_screen = HelpPage("help_page")
        self.add_widget(self.help_screen)

    def add_null_window(self, window_data_key):
        # if len(utils.keys) == 1:
        new_win = Window(window_data_key, window_data_key, window_data_key, utils.data[window_data_key], False)
        # else:
        #     new_win = Window(window_data_key, utils.windows[-2], window_data_key[-1], utils.data[window_data_key], False)
        self.add_widget(new_win)
        self.home_screen.home_select_page.add_card(window_data_key)
        utils.update_changes()
