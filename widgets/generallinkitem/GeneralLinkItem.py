import webbrowser

from kivy.lang import Builder
from kivy.properties import StringProperty
from kivymd.uix.list import OneLineAvatarIconListItem

Builder.load_file("widgets/generallinkitem/GeneralLinkItem.kv")


class GeneralLinkItem(OneLineAvatarIconListItem):
    """
    General use case item to provide links to external sites
    """
    link = StringProperty()

    def __init__(self, **kwargs):
        super(OneLineAvatarIconListItem, self).__init__(**kwargs)
        self.link = self.link

    def open_link(self):
        webbrowser.get().open(self.link)
