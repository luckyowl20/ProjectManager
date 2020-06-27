from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ListProperty, StringProperty
from kivymd.uix.boxlayout import MDBoxLayout

from widgets import utils

Builder.load_file("widgets/myviewer/MyViewer.kv")


# file viewer widget, needed custom one to update file text color
class MyViewer(MDBoxLayout):
    selection = ListProperty(allownone=True)
    path = StringProperty(allownone=True)
    project_path = StringProperty(allownone=True)

    def __init__(self, **kwargs):
        Clock.schedule_once(self.init_widget, 0)
        super(MyViewer, self).__init__(**kwargs)
        self.app = App.get_running_app()

    # binds addition of file to update_file_list entry for color change
    def init_widget(self, *args):
        fc = self.ids['filechooser']
        self.path = fc.rootpath
        fc.bind(on_entry_added=self.update_file_list_entry)
        fc.bind(on_subentry_to_entry=self.update_file_list_entry)

    # changes the text color of the file
    def update_file_list_entry(self, file_chooser, file_list_entry, args):
        file_list_entry.ids['filename'].color = self.app.theme_cls.text_color
        utils.files.append(file_list_entry.ids['filename'])

    # adds selection to the path for use outside of this widget
    def selection_made(self, selection, path):
        self.selection = selection
        # if path is none
        if not path:
            self.path = "/"
        else:
            self.path = path
