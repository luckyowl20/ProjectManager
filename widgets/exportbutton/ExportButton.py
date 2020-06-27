import os
import shutil
import tkinter
from tkinter import filedialog
from zipfile import ZipFile

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.utils import get_hex_from_color
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import Snackbar

from widgets import utils
from widgets.exportbutton.GoogleDriveExport import GoogleDriveExport

Builder.load_file("widgets/exportbutton/ExportButton.kv")


class ExportPopupContent(MDBoxLayout):
    """
    Content for popup when "export" is pressed in ExportButton when "Google Drive" is selected
    """
    export_path = os.path.abspath(utils.app_settings["default_export_path"])
    export_type = utils.app_settings["default_export_type"]

    export_type_label = ObjectProperty()
    export_path_label = ObjectProperty()

    export_filename_label = ObjectProperty()
    filename_field = ObjectProperty()

    def __init__(self, parent_window, export_filename, **kwargs):
        """Init popup"""
        super(MDBoxLayout, self).__init__(**kwargs)
        self.export_path = os.path.abspath(utils.app_settings["default_export_path"])
        self.export_type = utils.app_settings["default_export_type"]
        self.parent_window = parent_window
        self.export_type_label.text = self.get_export_type()
        self.export_path_label.text = self.get_export_path()
        self.export_filename = export_filename
        self.export_filename_label.text = f"[b]Original export file name:[/b] {self.export_filename}"
        self.filename_field.text = self.export_filename

    def get_export_path(self):
        """
        Gets the default export path and appends the name of the project folder
        :return: str
        """
        return self.export_path + f"\\{self.parent_window.name}"

    def get_export_type(self):
        """
        Gets the type of export, example: "Folder", and returns string that declares the export type
        :return: str
        """
        return f"[b]Export to:[/b] {self.export_type}"

    def change_export_path(self, *args):
        """
        Change the default export path to a selected path
        :param args: button args
        :return: None
        """
        # if the user does not select anything, the project path bugs out TODO: Fix this issue
        root = tkinter.Tk()
        root.withdraw()
        selected_folder = tkinter.filedialog.askdirectory().replace("/", "\\")
        self.export_path = selected_folder
        self.export_path_label.text = selected_folder + f"\\{self.parent_window.name}"

    def export_type_selected(self, instance, value):
        """
        Update the selected export type
        :param instance: not sure?
        :param value: chip widget value
        :return: None
        """
        # value is the text from the chip
        self.export_type = value
        self.export_type_label.text = self.get_export_type()

    def filename_text_edited(self, text):
        self.export_filename = text


class ExportPopup(MDBoxLayout):
    """
    Majority of logic that handles exporting the project, the actual popup for the export button
    """

    def __init__(self, parent_window, **kwargs):
        """Init the popup"""
        super(MDBoxLayout, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.export_path = 'Exports'

        # parent Window object (the screen which this export button lives in)
        self.parent_window = parent_window

        self.popup_content = ExportPopupContent(parent_window, self.parent_window.name)
        self.error_dialog = None
        self.error_noticed = False

        # Initialize the export dialog/popup window
        self.export_dialog = MDDialog(
            title=f"[color=%s]Export {utils.data[self.parent_window.name]['title']}?\n"
                  f"[size=12]Exporting as {self.parent_window.name}[/size][/color]" %
                  get_hex_from_color(self.app.theme_cls.text_color),
            type="custom",
            content_cls=self.popup_content,
            buttons=[
                MDFlatButton(
                    text="CANCEL", text_color=self.app.theme_cls.text_color,
                    on_release=self.cancel_export
                ),
                MDRaisedButton(
                    text="EXPORT", text_color=self.app.theme_cls.primary_color,
                    on_release=self.export_project
                )],
            size_hint = (None, None), size=(self.popup_content.width + 50, self.popup_content.height + 50)
        )

    def open_export_menu(self, *args):
        """Opens the export popup"""
        self.export_dialog.set_normal_height()
        self.export_dialog.open()

    def cancel_export(self, *args):
        """Dismisses the export popup"""
        self.export_dialog.dismiss()

    def export_project(self, *args):
        """
        Exports the project on the current window, 3 options for export:
        Folder - a folder which the project is exported to
        .zip file - a zip file the project is exported to
        Google Drive - uploads to the users google drive account, if the user has not selected an account, prompts them
                       to select one
        :param args: button args
        :return: None
        """
        # Path to the selected export folder in the popup dialog
        abs_export_path = os.path.abspath(self.popup_content.export_path)
        success = False

        if self.popup_content.export_type == "Folder":
            try:
                source_dir = os.path.abspath(utils.data[self.parent_window.name]['proj_path'])
                dest_dir = abs_export_path + "\\" + self.popup_content.export_filename

                shutil.copytree(source_dir, dest_dir)
            except FileExistsError:
                self.create_error_dialog("This project already exists",
                                         f"\nThe directory [u]{abs_export_path}[/u] already has a folder named "
                                         f"[u]{self.parent_window.name}[/u]"
                                         f"\n\nPlease delete or move this folder to export this project to a folder")

            if not self.error_dialog:
                success = True
            else:
                success = False

        elif self.popup_content.export_type == ".zip File":
            files = []
            project_path = os.path.abspath(utils.data[self.parent_window.name]['proj_path'])

            if os.path.isfile(f"{abs_export_path}\\{self.popup_content.export_filename}.zip") and not self.error_noticed:
                self.create_error_dialog("This project zip file already exists",
                                         f"\nThe zip file will be overridden if you choose to export without moving the"
                                         f" current zip file in [u]{self.popup_content.export_path}[/u]"
                                         f"\n\nMove this file: [u]{self.popup_content.export_filename}.zip[/u]")

                # So the user has the option to override the zip file in the export directory
                if self.error_noticed:
                    self.write_to_zip(files, project_path, abs_export_path, self.popup_content.export_filename)
                    success = True
            else:
                self.write_to_zip(files, project_path, abs_export_path, self.popup_content.export_filename)
                success = True

        elif self.popup_content.export_type == "Google Drive":
            google_popup = GoogleDriveExport(self.parent_window, self.popup_content.export_filename)
            google_popup.open_export_popup()

            # Close the export popup because google_popup.open_export_popup() opens its own popup
            self.cancel_export()

        if success:
            self.export_dialog.dismiss()
            Snackbar(text=f"{utils.data[self.parent_window.name]['title']} exported"
                          f" to {self.popup_content.export_path}\\{self.popup_content.export_filename} as "
                          f"{self.popup_content.export_type} successfully").show()
            self.error_noticed = False

    def dismiss_error(self, *args):
        """Dismiss the error message and set noticed flag to True"""
        self.error_dialog.dismiss()
        self.error_dialog = None
        self.error_noticed = True

    def create_error_dialog(self, title, text):
        """
        Creates an error dialog with title for the dialog title and text for the content of the message
        :param title: str
        :param text: str
        :return: None
        """
        self.error_dialog = MDDialog(buttons=[MDRaisedButton(text="CLOSE", text_color=self.app.theme_cls.text_color,
                                                             on_release=self.dismiss_error)])
        self.error_dialog.title = f"[color=%s]{title}[/color]" % \
                                  get_hex_from_color(self.app.theme_cls.text_color)
        self.error_dialog.text = text
        self.error_dialog.set_normal_height()
        self.error_dialog.open()

    @staticmethod
    def write_to_zip(files, project_path, abs_path, filename):
        """
        Writes file to zip
        :param filename: what to name the file
        :param files: list
        :param project_path: str - path of the project to save
        :param abs_path: str - absolute path of export path
        :return:
        """
        for file in os.listdir(project_path):
            files.append(f"{file}")

        cwd = os.getcwd()

        with ZipFile(f"{abs_path}\\{filename}.zip", 'w') as zip_file:
            os.chdir(project_path)
            for file in files:
                zip_file.write(file)

        os.chdir(cwd)
