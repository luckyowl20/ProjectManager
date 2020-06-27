import webbrowser

import validators
from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from kivy.utils import get_color_from_hex
from kivymd.color_definitions import colors
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import OneLineAvatarIconListItem

from widgets import utils
from widgets.MenuIconTextButton import MenuIconTextButton

Builder.load_file("widgets/navdrawer/helpmenu/HelpPage.kv")


class HelpLinkIconListItem(OneLineAvatarIconListItem):
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
        # utils.update_data()
        # utils.data[self.link_layout.parent_screen.name]['links'] = self.link_layout.links
        # utils.save_project_data(utils.data[self.link_layout.parent_screen.name],
        #                         f"{utils.data[self.link_layout.parent_screen.name]['proj_path']}/project_data.json")


class HelpPageContent(MDBoxLayout):
    link_field = ObjectProperty()
    add_link_button = ObjectProperty()
    links_list = ObjectProperty()

    def __init__(self, **kwargs):
        super(MDBoxLayout, self).__init__(**kwargs)
        self.links = []
        # add a test link
        self.link_field.text = "https://google.com"
        self.add_pressed()

    @staticmethod
    def get_lighter(color, percentage):
        """returns a lighter alpha value for a given color"""
        color[3] = percentage
        return color

    # same methods from widgets.linkslayout.LinksLayout LinksLayout class

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

    def add_pressed(self):
        new_link = self.link_field.text
        self.links_list.add_widget(HelpLinkIconListItem(self, text=new_link))
        self.link_field.text = ""
        self.add_link_button.disabled = True
        self.link_field.focus = False
        self.link_field.helper_text = "Please enter a valid url"
        self.links.append(new_link)


class HelpPage(Screen):
    def __init__(self, name, **kwargs):
        super(HelpPage, self).__init__(**kwargs)
        self.name = name
        self.app = App.get_running_app()

        main_layout = MDBoxLayout(orientation='vertical')
        second_layout = MDBoxLayout(size_hint_y=None, padding=dp(10))

        main_layout.add_widget(HelpPageContent())

        menu_button = MenuIconTextButton('menu', 'Menu')
        menu_button.bind(on_release=self.app.menu_btn_bind)
        menu_button.icon_button.bind(on_release=self.app.menu_btn_bind)
        second_layout.add_widget(menu_button)

        separator = MDBoxLayout(size_hint_x=None, width=dp(1), md_bg_color=self.app.theme_cls.primary_light)
        utils.separators.append(separator)
        second_layout.add_widget(separator)

        home_button = MenuIconTextButton('home', 'Home')
        home_button.bind(on_release=self.app.home_btn_bind)
        home_button.icon_button.bind(on_release=self.app.home_btn_bind)
        second_layout.add_widget(home_button)

        second_layout.height = dp(61)
        second_layout.md_bg_color = get_color_from_hex(colors[self.app.theme_cls.theme_style]["CardsDialogs"])
        main_layout.add_widget(second_layout)

        utils.bottom_banners.append(second_layout)

        self.add_widget(main_layout)
