import json
import os
from datetime import date

from kivy.app import App
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.utils import get_color_from_hex
from kivymd.color_definitions import colors
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel

from widgets import utils
from widgets.header.Header import Header
from widgets.mainlayout.MainLayout import MainLayout
from widgets.MenuIconTextButton import MenuIconTextButton
from widgets.exportbutton.ExportButton import ExportPopup


class VerticalSeparator(MDBoxLayout):
    def __init__(self, **kwargs):
        super(VerticalSeparator, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.size_hint_x = None
        self.width = dp(1)
        self.md_bg_color = self.app.theme_cls.primary_light


class Window(Screen):
    # the screen for each page, should be called page but is not

    nav_drawer = ObjectProperty()
    btn = ObjectProperty()

    # TODO clean up the __init__ method, template items into classes (separator and buttons layout)
    # ^ changing separator into class is done
    def __init__(self, name, back, next_page, page_data, no_pages=False, **kwargs):
        super(Window, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.no_pages = no_pages

        if no_pages:
            self.add_page()

        else:
            self.name = name
            self.back = back
            self.next_page = next_page
            self.page_data = page_data
            utils.windows.append(self)
        layout = MDBoxLayout(orientation='vertical')
        layout.add_widget(Header(self))
        layout.add_widget(MainLayout(self))
        layout.add_widget(Label())

        # layout containing all the navigation buttons
        buttons_layout = MDBoxLayout()
        buttons_layout.orientation = 'horizontal'
        buttons_layout.adaptive_height = True
        buttons_layout.adaptive_width = True
        buttons_layout.padding = 0, 0, 0, 5

        # layout for back button
        back_layout = MDBoxLayout()
        back_layout.orientation = 'vertical'
        back_layout.adaptive_height = True
        back_layout.adaptive_width = True
        button_back = MDIconButton(icon="arrow-left", pos_hint={"center_x": 0.5, "center_y": 0.5}, user_font_size=30)
        button_back.bind(on_release=self.btn_back_press)
        back_layout.add_widget(button_back)
        back_layout.add_widget(MDLabel(text="Back", font_size=8, theme_text_color="Primary", halign='center'))
        buttons_layout.add_widget(back_layout)

        # next button layout
        next_layout = MDBoxLayout()
        next_layout.orientation = 'vertical'
        next_layout.adaptive_height = True
        next_layout.adaptive_width = True
        button_next = MDIconButton(icon="arrow-right", pos_hint={"center_x": 0.5, "center_y": 0.5}, user_font_size=30)
        button_next.bind(on_release=self.btn_next_press)
        next_layout.add_widget(button_next)
        next_layout.add_widget(MDLabel(text="Next", font_size=8, theme_text_color="Primary", halign='center'))
        buttons_layout.add_widget(next_layout)

        # add button layout
        add_layout = MDBoxLayout()
        add_layout.orientation = 'vertical'
        add_layout.adaptive_height = True
        add_layout.adaptive_width = True
        button_add = MDIconButton(icon="plus", pos_hint={"center_x": 0.5, "center_y": 0.5}, user_font_size=30)
        button_add.bind(on_release=self.add_page)
        add_layout.add_widget(button_add)
        add_layout.add_widget(MDLabel(text="Add", font_size=8, theme_text_color="Primary", halign='center'))
        buttons_layout.add_widget(add_layout)
        layout2 = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(button_back.height + 8),
                              padding=dp(10))

        layout2.md_bg_color = get_color_from_hex(colors[self.app.theme_cls.theme_style]["CardsDialogs"])

        self.menu_button = MenuIconTextButton('menu', 'Menu')
        layout2.add_widget(self.menu_button)

        # menu separator
        separator = VerticalSeparator()
        utils.separators.append(separator)
        layout2.add_widget(separator)

        home_button = MenuIconTextButton('home', 'Home')
        self.home_button = home_button
        layout2.add_widget(home_button)

        # second separator
        separator = VerticalSeparator()
        utils.separators.append(separator)
        layout2.add_widget(separator)

        export_button = MenuIconTextButton('folder-upload-outline', 'Export')
        export_button.bind(on_release=self.export_project)
        export_button.icon_button.bind(on_release=self.export_project)
        layout2.add_widget(export_button)

        # third separator
        separator = VerticalSeparator()
        utils.separators.append(separator)
        layout2.add_widget(separator)

        # import button to import projects
        import_button = MenuIconTextButton('folder-download-outline', "Import")
        import_button.bind(on_release=self.app.import_btn_bind)
        import_button.icon_button.bind(on_release=self.app.import_btn_bind)
        layout2.add_widget(import_button)

        layout2.add_widget(Label())

        layout2.add_widget(buttons_layout)

        utils.bottom_banners.append(layout2)
        layout.add_widget(layout2)
        self.add_widget(layout)

    def export_project(self, *args):
        export_popup = ExportPopup(self)
        export_popup.open_export_menu()

    # check if new project dir exists, if not make it, return that path
    @staticmethod
    def check_path(new_dir):
        original_path = os.getcwd()
        temp_path = utils.projects_directory.replace("/", "\\")
        addition = 1

        try:
            os.chdir(temp_path)
            if not os.path.exists(new_dir):
                os.mkdir(new_dir)
                os.chdir(new_dir)
                new_proj_path = os.getcwd().replace("\\", "/")
                os.chdir(original_path)
                return new_proj_path, new_dir, addition

            else:
                while True:
                    newer_dir = new_dir + f"({addition})"

                    if not os.path.exists(newer_dir):
                        os.mkdir(newer_dir)
                        os.chdir(newer_dir)
                        new_proj_path = os.getcwd().replace("\\", "/")
                        os.chdir(original_path)
                        return new_proj_path, newer_dir, addition

                    addition += 1

        except WindowsError or OSError:
            print("WINDOWS ERROR")

    # called when back button is pressed
    def btn_back_press(self, instance):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = self.back

    # called when next button is pressed
    def btn_next_press(self, instance):
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = self.next_page

    # called when add button is pressed
    def add_page(self, instance=None):
        utils.get_num_projects()
        new_key = f"project{utils.num_projects + 1}"
        new_path, new_folder, num_new_folders = self.check_path(new_key)

        if new_folder == new_key:
            title = f"Project {utils.num_projects + 1}"
        else:
            title = f"Project {utils.num_projects + 1} ({num_new_folders})"

        formatted_proj_path = f"{utils.projects_directory}\\{new_folder}".replace("/", "\\")
        new_data = {
            "data":
                {
                    "id": utils.num_projects + 1,
                    "title": title,
                    "subtitle": "Subtitle",
                    "start_date": date.today().strftime("%m/%d/%y%y"),
                    "completion": "In progress",
                    "progress": 0,
                    "recent_progress": "Never",
                    "recent_amount": 0,
                    "proj_path": formatted_proj_path,
                    "proj_image": "",
                    "links": [],
                    "todo_lists": []
                }
        }

        with open(f"{new_path}/project_data.json", "w") as f:
            json.dump(new_data, f)
        utils.project_data_paths.append(f"{new_path}/project_data.json")

        with open(f"{new_path}/DESCRIPTION.txt", "w") as file:
            file.write("Type a description here!")

        utils.data[new_key] = new_data['data']
        utils.keys.append(new_key)
        utils.num_projects += 1
        utils.save_settings({"num_projects": utils.num_projects})
        if self.no_pages:

            self.name = utils.keys[-1]
            self.back = utils.keys[-1]
            self.next_page = utils.keys[-1]
            self.page_data = utils.data[self.name]
            utils.windows.append(self)
            self.no_pages = False

        else:
            self.manager.add_widget(Window(new_key, utils.keys[-1], new_key, utils.data[new_key]))
            utils.update_changes()
        self.app.add_project_card(new_key)
