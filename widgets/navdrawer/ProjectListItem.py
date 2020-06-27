from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivymd.uix.list import OneLineIconListItem

Builder.load_file("widgets/navdrawer/ProjectListItem.kv")


class ProjectListItem(OneLineIconListItem):
    window_manager = ObjectProperty()
    next_win = StringProperty()
    drawer = ObjectProperty()

    def __init__(self, window_item, next_window, drawer, **kwargs):
        super(OneLineIconListItem, self).__init__(**kwargs)
        self.window_manager = window_item.manager
        self.next_win = next_window
        self.drawer = drawer
