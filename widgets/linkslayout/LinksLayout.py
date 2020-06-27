import validators
from kivy.app import App
import webbrowser

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.list import OneLineAvatarIconListItem, IRightBodyTouch

from widgets import utils

Builder.load_file("widgets/linkslayout/LinksLayout.kv")


class DeleteButton(IRightBodyTouch, MDIconButton):
    """Delete button for the link"""
    pass


class LinkIconListItem(OneLineAvatarIconListItem):
    """
    List item for each link the user adds
    """
    link_layout = ObjectProperty()

    def __init__(self, link_layout, **kwargs):
        super(OneLineAvatarIconListItem, self).__init__(**kwargs)
        self.link_layout = link_layout

    def open_link(self):
        """Open the link"""
        webbrowser.get().open(self.text)

    def delete_link(self):
        """Remove the link from the layout"""
        self.link_layout.links_list.remove_widget(self)
        self.link_layout.links.remove(self.text)
        utils.update_data()
        utils.data[self.link_layout.parent_screen.name]['links'] = self.link_layout.links
        utils.save_project_data(utils.data[self.link_layout.parent_screen.name],
                                f"{utils.data[self.link_layout.parent_screen.name]['proj_path']}/project_data.json")


class LinksLayout(MDBoxLayout):
    """
    Layout containing all of the links and the text field to add links
    """
    link_field = ObjectProperty()
    links_list = ObjectProperty()
    add_link_button = ObjectProperty()

    def __init__(self, **kwargs):
        super(MDBoxLayout, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.parent_screen = None
        self.links = []

    def add_pressed(self):
        """
        Called when the plus button is pressed, if the link is valid add it
        :return: None
        """
        new_link = self.link_field.text
        self.links_list.add_widget(LinkIconListItem(self, text=new_link))
        self.link_field.text = ""
        self.add_link_button.disabled = True
        self.link_field.focus = False
        self.link_field.helper_text = "Please enter a valid url"
        self.links.append(new_link)
        utils.update_data()
        utils.data[self.parent_screen.name]["links"] = self.links
        utils.save_project_data(utils.data[self.parent_screen.name],
                                f"{utils.data[self.parent_screen.name]['proj_path']}/project_data.json")

    def validate_url(self, url):
        """
        Validate the given url and if it is invalid, disable the add/plus button
        :param url: str
        :return: None
        """
        if not validators.url(url):
            self.link_field.helper_text = "Please enter a valid url"
            self.add_link_button.disabled = True

        else:
            self.link_field.helper_text = ""
            self.add_link_button.disabled = False

    def validate_add(self, url):
        """
        Validate the url, if its valid, add it
        Called from on_text_validate, when the user presses enter
        :param url:
        :return:
        """
        if validators.url(url):
            self.add_pressed()

    def update_screen(self, screen):
        """
        Adds a new link widget to the given screen
        :param screen: str
        :return:
        """
        self.parent_screen = screen
        self.links = utils.data[self.parent_screen.name]["links"]
        for link in self.links:
            self.links_list.add_widget(LinkIconListItem(self, text=link))
