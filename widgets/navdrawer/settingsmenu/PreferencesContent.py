import os
import tkinter
from tkinter import filedialog

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout

from widgets import utils

Builder.load_file("widgets/navdrawer/settingsmenu/PreferencesContent.kv")


class PreferencesContent(MDBoxLayout):

    default_proj_path_label = ObjectProperty()
    default_export_path_label = ObjectProperty()
    default_export_type_label = ObjectProperty()

    def __init__(self, **kwargs):
        super(MDBoxLayout, self).__init__(**kwargs)
        utils.update_settings()

        self.project_path = os.path.abspath(utils.app_settings["project_path"])
        self.default_export_path = utils.app_settings["default_export_path"]
        self.default_export_type = utils.app_settings["default_export_type"]

        self.default_proj_path_label.text = self.project_path
        self.default_export_path_label.text = self.default_export_path
        self.default_export_type_label.text = f"[b]Default export format: [/b]{self.default_export_type}"

    def change_project_path(self):
        root = tkinter.Tk()
        root.withdraw()
        selected_folder = tkinter.filedialog.askdirectory(initialdir="C:/",
                                                          title="Select a new projects folder").replace('/', '\\')
        if selected_folder != "":
            self.project_path = selected_folder
            self.default_proj_path_label.text = self.project_path

    def change_export_path(self):
        root = tkinter.Tk()
        root.withdraw()
        selected_folder = tkinter.filedialog.askdirectory(initialdir="C:/",
                                                          title="Select a new default export folder").replace('/', '\\')
        if selected_folder != "":
            self.default_export_path = selected_folder
            self.default_export_path_label.text = self.default_export_path

    def export_type_selected(self, instance, value):
        self.default_export_type = value
        self.default_export_type_label.text = f"[b]Default export format: [/b]{value}"
