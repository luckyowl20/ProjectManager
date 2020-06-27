import json
import os
import shutil
import tkinter
from tkinter import filedialog
from functools import partial

from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import SwapTransition, Screen
from kivy.utils import get_hex_from_color, get_color_from_hex
from kivymd.color_definitions import colors
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel

from widgets import utils
from widgets.Window import Window
from widgets.MenuIconTextButton import MenuIconTextButton

Builder.load_file("widgets/homepage/HomePage.kv")


class DeleteDialogContent(BoxLayout):
    """Content for the delete project popup dialog"""
    new_text = StringProperty()


# Card widget for each project each ObjectProperty belongs to one aspect of the widget
class ProjectCard(MDCard):
    """
    Card that represents each project
    """
    project_filename = ObjectProperty()
    home_page = ObjectProperty()
    project = StringProperty()
    project_card = ObjectProperty()
    project_image = ObjectProperty()
    image_edit = ObjectProperty()
    home_project_title = ObjectProperty()
    home_progress_label = ObjectProperty()
    home_progress_bar = ObjectProperty()
    home_project_desc = ObjectProperty()
    delete_project = ObjectProperty()
    open_project = ObjectProperty()
    cancel_button = ObjectProperty()

    def __init__(self, **kwargs):
        super(MDCard, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.delete_dialog = None

    def update_colors(self):
        """Update title color in the delete dialog and the color of the CANCEL button"""
        self.delete_dialog.title = f"[color=%s]Are you sure?[/color]" % \
                                   get_hex_from_color(self.app.theme_cls.text_color)
        self.delete_dialog.buttons[0].text_color = self.app.theme_cls.text_color


class HomeSelectPage(MDBoxLayout):
    """
    Homepage with cards for each project, only created once and has a card for each project
    """
    home_title = ObjectProperty()
    home_subtitle = ObjectProperty()
    card_layout = ObjectProperty()
    delete_dialog = None

    def __init__(self, manager, **kwargs):
        """Init page, adds a card for each project in utils.keys"""
        super(MDBoxLayout, self).__init__(**kwargs)
        self.manager = manager
        self.app = App.get_running_app()
        for project in utils.keys:
            self.add_card(project)

    def add_card(self, project):
        """Adds a new ProjectCard"""
        card = ProjectCard()
        card.home_page = self
        card.project = project
        card.delete_dialog = None
        # creates the card dialog in advance, TODO might want to change this
        self.delete_project(card, project, open_dialog=False)
        card.project_image.source = self.get_image(project, utils.data[project]['proj_image'])
        card.project_image.reload()
        card.home_project_title.text = self.shorten_title(utils.data[project]["title"])
        card.home_project_desc.text = self.get_project_desc(project)
        card.home_progress_label.text = f"{utils.data[project]['progress']}%"
        card.home_progress_bar.value = utils.data[project]["progress"]
        card.open_project.bind(on_release=partial(self.open_project, project))
        card.delete_project.bind(on_release=partial(self.delete_project, card, project))
        card.project_filename.text = f"Filename: {project}"
        utils.project_cards.append(card)
        self.card_layout.add_widget(card)

    def open_project(self, project, *args):
        """changes screen to selected project based on which ProjectCard is clicked"""
        self.manager.transition = SwapTransition()
        self.manager.current = project

    def delete_project(self, card, project, open_dialog=True, *args):
        """
        Deletes selected project when delete project button is pressed
        :param card: ProjectCard()
        :param project: str
        :param open_dialog: bool
        :param args: button args
        :return: None
        """
        # create the delete dialog if not created
        if not card.delete_dialog:
            card.delete_dialog = MDDialog(
                title=f"[color=%s]Are you sure?[/color]" %
                      get_hex_from_color(self.app.theme_cls.text_color),
                type="custom",
                content_cls=DeleteDialogContent(new_text=utils.data[project]['title']),
                buttons=[
                    MDFlatButton(
                        text="CANCEL", text_color=self.app.theme_cls.text_color,
                        on_release=partial(self.close_delete_dialog, card)
                    ),
                    MDRaisedButton(
                        text="DELETE", text_color=self.app.theme_cls.primary_color,
                        on_release=partial(self.confirm_delete, card, project)
                    )]
            )
        if open_dialog:
            card.delete_dialog.set_normal_height()
            card.delete_dialog.open()

    @staticmethod
    def close_delete_dialog(card, *args):
        """Closes the delete dialog for the given card"""
        card.delete_dialog.dismiss()

    def confirm_delete(self, card, project, *args):
        """
        Confirms the delete for the selected project and deletes it
        :param card: ProjectCard()
        :param project: str
        :param args: button args
        :return: None
        """
        # dismisses the delete dialog
        card.delete_dialog.dismiss()

        # deletes the project from the projects path
        del_dir = os.path.abspath(utils.data[project]['proj_path'].replace("/", "\\"))
        shutil.rmtree(del_dir, True)

        # removes project references to this project in required places
        # utils.update_keys()
        key_index = utils.keys.index(project)
        '''
        print("\nkey index:", key_index)
        print("windows", utils.windows)
        print("keys", utils.keys)
        print("data", utils.data)
        '''
        remove_window = utils.windows.pop(key_index)
        utils.keys.remove(project)
        utils.project_cards.remove(card)

        # removes the project from the navigation drawer menu
        self.app.remove_menu_entry(utils.menu_projects.pop(key_index))

        # remove the window from the window manager so only 1 instance of the window exists if the user imports a
        # project with the same name
        self.manager.remove_widget(remove_window)

        # when introducing the import feature, this was added, seems like without it, utils.update_data()
        # is called each clock cycle and the app hangs/stalls this is needed to be removed
        # raises error if the project was added after initialization or not from import, no project_data_path is
        # created if not loaded when initialized, all projects created after app startup will error
        # THIS IS NO LONGER AN ERROR, here in case something is missed
        try:
            utils.project_data_paths.pop(key_index)
        except IndexError:
            pass
        # removes the card from the home page
        card.home_page.card_layout.remove_widget(card)

        # if the project id is the ending project, decrement the ending project number
        # TODO: rework id system and move towards hash id (utils.generate_hash_id())
        if utils.data[project]["id"] == utils.get_num_projects():
            utils.num_projects -= 1
            utils.save_settings({"num_projects": utils.num_projects})

        # remove the project data
        utils.data.pop(project)
        # update the remaining windows to make sure their navigation buttons and name are correct
        utils.update_changes(False, False)

    @staticmethod
    def get_image(project, image_name):
        """
        Sets the image to the path of the image in the project data,
        gets the image_icon.png for the project, if none returns default image
        :param project: str
        :param image_name: str
        :return: str
        """
        path = utils.data[project]["proj_path"] + f"\\{image_name}"
        if os.path.isfile(path):
            return path
        else:
            return "default_image.png"

    @staticmethod
    def edit_image(project, image_widget):
        """
        asks user to select an image of .png or .jpg and copies selection to the project folder
        and renames it to "project_image".extension
        :param image_widget: object
            the image widget that contains the project image
        :param project: str
        :return: str
        """
        root = tkinter.Tk()
        root.withdraw()
        selected_image = tkinter.filedialog.askopenfilename(initialdir="C:/", title="Select an image",
                                                            filetypes=(("png files", "png"),
                                                                       ("jpg files", "jpg"))).replace("/", "\\")
        image_name = selected_image.split("\\")[-1]
        image_extension = image_name.split(".")[-1]
        copied_file = utils.data[project]["proj_path"] + f"\\project_image.{image_extension}"
        try:
            shutil.copyfile(selected_image, copied_file)
            utils.update_data()
            utils.data[project]["proj_image"] = f"project_image.{image_extension}"
            new_data = {'data': utils.data[project]}
            with open(f"{utils.data[project]['proj_path']}\\project_data.json", "w") as file:
                json.dump(new_data, file)
            utils.update_data()

        except FileNotFoundError:
            pass

        source = os.path.abspath(utils.data[project]["proj_path"] +
                                 f"/project_image.{image_extension}").replace("\\", "/")
        image_widget.source = source
        image_widget.reload()
        return source

    @staticmethod
    def shorten_title(title):
        """
        shortens the title of the project to fit on one line inside the card, 32 characters
        :param title: str
        :return: str
        """
        if len(title) >= 32:
            return title[0:32] + "..."
        else:
            return title

    @staticmethod
    def get_project_desc(project):
        """
        sets the description field, if greater than 100 characters shorten it
        :param project: str
        :return: str
        """
        desc_path = utils.data[project]["proj_path"] + f"/DESCRIPTION.txt"

        with open(desc_path, "r") as file:
            desc = file.read()

        if len(desc) > 100:
            return desc[0:100] + "..."
        else:
            return desc

    @staticmethod
    def get_lighter(color, percentage):
        """returns a lighter alpha value for a given color"""
        color[3] = percentage
        return color


class HomeMenu(MDBoxLayout):
    """
    Everything in the home screen layout besides the bottom navigation bar that includes the "Menu" button and the
    "Add" button, basically a container for everything else
    """
    def __init__(self, **kwargs):
        super(MDBoxLayout, self).__init__(**kwargs)
        self.app = App.get_running_app()

    @staticmethod
    def get_bg_color():
        """Returns the CardDialogs theme color, used as background color"""
        return get_color_from_hex(colors[App.get_running_app().theme_cls.theme_style]["CardsDialogs"])


class HomeScreen(Screen):
    """
    Screen for the home page
    """

    def __init__(self, manager, screen_name, **kwargs):
        """
        Creates page layout, consists of a layout containing HomeSelectPage and a layout created the
        same as the MenuLayout in each project page, HomeMenu class is not used

        :param manager: screen manager
        :param screen_name: str
        :param kwargs:
        """
        super(Screen, self).__init__(**kwargs)
        self.name = screen_name
        self.app = App.get_running_app()
        self.home_select_page = HomeSelectPage(manager)
        self.home_menu = HomeMenu()

        # screen layout
        layout = MDBoxLayout(orientation='vertical')
        layout.add_widget(self.home_select_page)

        # add button layout
        add_layout = MDBoxLayout()
        add_layout.padding = 0, 0, 0, dp(5)
        add_layout.orientation = 'vertical'
        add_layout.adaptive_height = True
        add_layout.adaptive_width = True
        button_add = MDIconButton(icon="plus", pos_hint={"center_x": 0.5, "center_y": 0.9}, user_font_size=30)

        # binds button press to add new page
        button_add.bind(on_release=self.add_page_from_home)
        add_layout.add_widget(button_add)
        add_layout.add_widget(MDLabel(text="Add", font_size=8, theme_text_color="Primary", halign='center'))

        # bottom banner layout
        layout2 = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(button_add.height + 8),
                              padding=dp(10))

        # menu hamburger button and menu label
        menu_button = MenuIconTextButton('menu', "Menu")
        menu_button.bind(on_release=self.app.menu_btn_bind)
        menu_button.icon_button.bind(on_release=self.app.menu_btn_bind)
        layout2.add_widget(menu_button)

        # separator
        separator = MDBoxLayout(size_hint_x=None, width=dp(1), md_bg_color=self.app.theme_cls.primary_light)
        utils.separators.append(separator)
        layout2.add_widget(separator)

        # import button to import projects
        import_button = MenuIconTextButton('folder-download-outline', "Import")
        import_button.bind(on_release=self.app.import_btn_bind)
        import_button.icon_button.bind(on_release=self.app.import_btn_bind)
        layout2.add_widget(import_button)

        # debug button
        # layout2.add_widget(MDRaisedButton(text="DEBUG", on_release=partial(print, utils.data, "\n", utils.windows,
        #                                                                    self.test)))

        layout2.md_bg_color = get_color_from_hex(colors[self.app.theme_cls.theme_style]["CardsDialogs"])

        # spacer label
        layout2.add_widget(Label())

        layout2.add_widget(add_layout)
        layout.add_widget(layout2)

        utils.bottom_banners.append(layout2)

        self.add_widget(layout)

    def test(self):
        test = self.app.test()
        return test

    def add_page_from_home(self, *args):
        """Adds a new project page/window and updates the other pages so the back/next buttons work correctly"""
        self.manager.add_widget(Window("", "", "", "", True))
        utils.update_changes()
