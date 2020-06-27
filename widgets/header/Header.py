from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import get_hex_from_color
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog

from kivymd.uix.textfield import MDTextField

from widgets import utils

Builder.load_file("widgets/header/Header.kv")


class HeaderPopupContent(BoxLayout):
    """
    Popup content for the edit title and subtitle widget on each of the project pages
    """
    new_hint_text = StringProperty()
    new_text = StringProperty()


class Header(MDBoxLayout):
    """Header class for title and subtitle of each page"""
    title = ObjectProperty()
    subtitle = ObjectProperty()
    project_filename = ObjectProperty()

    dialog_title = None
    dialog_subtitle = None

    def __init__(self, parent_screen, **kwargs):
        """Init header"""
        super(MDBoxLayout, self).__init__(**kwargs)
        self.parent_screen = parent_screen
        self.app = App.get_running_app()
        self.data = parent_screen.page_data
        self.title.text = self.shorten_text(self.data["title"], 31)
        self.subtitle.text = self.shorten_text(self.data["subtitle"], 45)
        self.project_filename.text = f"Filename: {self.parent_screen.name}"

    # depends on grab_text_title() and close_dialog_title() methods as its binds
    def edit_title(self):
        """
        Edit the title of the project, method called when the pencil next to the title is clicked
        :return: None
        """
        # if this title dialog has not been created yet, create it.
        if not self.dialog_title:
            # Content class needs the hint text for the text field and the text to put into the text field,
            # in this case the project title
            self.dialog_title = MDDialog(
                title=f"[color=%s]Change project title, \nCurrent title: {self.data['title']}[/color]" %
                      get_hex_from_color(self.app.theme_cls.text_color),
                type="custom",
                content_cls=HeaderPopupContent(new_hint_text="New title", new_text=self.data['title']),
                buttons=[
                    MDFlatButton(
                        text="CANCEL", text_color=self.app.theme_cls.primary_color,
                        on_release=self.close_dialog_title
                    ),
                    MDRaisedButton(
                        text="SAVE", text_color=self.app.theme_cls.primary_color,
                        on_release=self.grab_text_title
                    )]
            )
        # adjust the size and open the dialog box
        self.dialog_title.set_normal_height()
        self.dialog_title.open()

    # depends on grab_text_subtitle() and close_dialog_subtitle() methods as its binds
    def edit_subtitle(self):
        """
        Edit the subtitle of the project, method called when the pencil next to the subtitle is clicked
        :return: None
        """
        # if subtitle dialog has not been created, create it
        if not self.dialog_subtitle:
            # Content class needs the hint text for the text field and the text to put into the text field,
            # in this case the project title
            self.dialog_subtitle = MDDialog(
                title=f"[color=%s]Change project subtitle, \nCurrent subtitle: {self.data['subtitle']}[/color]" %
                      get_hex_from_color(self.app.theme_cls.text_color),
                type="custom",
                content_cls=HeaderPopupContent(new_hint_text="New subtitle", new_text=self.data['subtitle']),
                buttons=[
                    MDFlatButton(
                        text="CANCEL", text_color=self.app.theme_cls.primary_color,
                        on_release=self.close_dialog_subtitle
                    ),
                    MDRaisedButton(
                        text="SAVE", text_color=self.app.theme_cls.primary_color,
                        on_release=self.grab_text_subtitle
                    )]
            )
        # adjust the size and open the dialog box
        self.dialog_subtitle.set_normal_height()
        self.dialog_subtitle.open()

    # to what was entered and shortens it if needed
    def grab_text_subtitle(self, inst):
        """
        Grab the altered text from the edited subtitle, update and save that data
        method called when the save button is pressed, saves the subtitle text to project json key and sets the subtitle
        :param inst: button instance
        :return: None
        """
        # this loops through all the children in the dialog_subtitle dialog box and if it is the text field,
        # set the subtitle to the shortened (if needed) text field text
        for obj in self.dialog_subtitle.content_cls.children:
            if isinstance(obj, MDTextField):
                if obj.text != "" and obj.text != self.subtitle.text:
                    self.subtitle.text = self.shorten_text(obj.text, 45)
                    self.data["subtitle"] = obj.text
        self.dialog_subtitle.title = f"[color=%s]Change project subtitle, Current subtitle: '{self.data['subtitle']}'" \
                                     f"[/color]" % get_hex_from_color(App.get_running_app().theme_cls.text_color)

        self.dialog_subtitle.dismiss()

        # update data with new subtitle
        utils.save_project_data(self.data, f"{self.data['proj_path']}/project_data.json")
        utils.update_data()
        self.data = utils.data[self.parent_screen.name]

    def grab_text_title(self, inst):
        """
        Grab the altered text from the edited title, update and save that data
        method called when the save button is pressed, saves the title text to project json key and sets the title
        :param inst: button instance
        :return: None
        """
        # this loops through all the children in the dialog_title dialog box and if it is the text field,
        # set the title to the shortened (if needed) text field text
        for obj in self.dialog_title.content_cls.children:
            if isinstance(obj, MDTextField):
                if obj.text != "" and obj.text != self.title.text:
                    self.title.text = self.shorten_text(obj.text, 31)
                    self.data["title"] = obj.text
        self.dialog_title.title = f"[color=%s]Change project title, Current title: '{self.title.text}'[/color]" \
                                  % get_hex_from_color(App.get_running_app().theme_cls.text_color)
        self.dialog_title.dismiss()

        # updates data with new title
        utils.save_project_data(self.data, f"{self.data['proj_path']}/project_data.json")
        utils.update_data()
        self.data = utils.data[self.parent_screen.name]

        # updates the title of the ProjectCard if the project cards name/project StringProperty match this page's parent
        # _screen's name
        for project_card in utils.project_cards:
            if project_card.project == self.parent_screen.name:
                project_card.home_project_title.text = project_card.home_page.shorten_title(self.title.text)

        # updates the project title for this project in the navigation drawer menu
        for project in utils.menu_projects:
            if project.next_win == self.parent_screen.name:
                utils.menu_projects[utils.menu_projects.index(project)].text = self.title.text

    def close_dialog_title(self, inst):
        """closes the edit title dialog box"""
        self.dialog_title.dismiss()

    def close_dialog_subtitle(self, inst):
        """closes the edit subtitle dialog box"""
        self.dialog_subtitle.dismiss()

    @staticmethod
    def shorten_text(text, length):
        """shortens given text to a given length if longer than length"""
        if len(text) >= length:
            return text[0:length] + "..."
        else:
            return text

    @staticmethod
    def get_lighter(color, percentage):
        """
        Get a lighter shade of color, changed alpha value to do so
        used to get a lighter shade of a theme color
        :param color: list
        :param percentage: float
        :return:
        """
        color[3] = percentage
        return color
