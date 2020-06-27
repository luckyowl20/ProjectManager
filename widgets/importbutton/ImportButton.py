import shutil
import tkinter
from functools import partial
from tkinter import filedialog
from zipfile import ZipFile

from kivy.app import App
from kivy.utils import get_hex_from_color
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import Snackbar

from widgets import utils
from widgets.importbutton.GoogleDriveImport import GoogleDriveImport

Builder.load_file("widgets/importbutton/ImportButton.kv")


class ImportFilenameContent(MDBoxLayout):
    filename_label = ObjectProperty()
    filename_field = ObjectProperty()
    import_type_label = ObjectProperty()

    def __init__(self, import_name, import_type, **kwargs):
        super(MDBoxLayout, self).__init__(**kwargs)
        self.import_name = import_name
        self.import_type = import_type
        self.import_type_label.text = f"[b]Import from: [/b]{self.import_type}"
        self.filename_label.text = self.get_filename_label()
        self.filename_field.text = self.import_name

    def get_filename_label(self):
        return f"[b]Original filename: [/b]{self.import_name}"

    def text_edited(self, text):
        self.import_name = text


class ImportPopupContent(MDBoxLayout):
    import_type_label = ObjectProperty()
    # import_path_label = ObjectProperty() not used because it goes to Projects folder

    def __init__(self, **kwargs):
        """Init popup"""
        super(MDBoxLayout, self).__init__(**kwargs)
        self.import_type = ".zip File"
        # self.parent_window = parent_window
        self.import_type_label.text = self.get_import_type()

    def get_import_type(self):
        """
        Gets the type of export, example: "Folder", and returns string that declares the export type
        :return: str
        """
        return f"[b]Import from:[/b] {self.import_type}"

    def import_type_selected(self, instance, value):
        """
        Update the selected export type
        :param instance: not sure?
        :param value: chip widget value
        :return: None
        """
        # value is the text from the chip
        self.import_type = value
        self.import_type_label.text = self.get_import_type()


class ImportPopup(MDBoxLayout):
    def __init__(self, **kwargs):
        super(MDBoxLayout, self).__init__(**kwargs)
        self.app = App.get_running_app()

        self.save_dialog = None

        self.popup_content = ImportPopupContent()
        self.import_dialog = MDDialog(
            title=f"[color=%s]Import project[/color]" %
                  get_hex_from_color(self.app.theme_cls.text_color),
            type="custom",
            content_cls=self.popup_content,
            buttons=[
                MDFlatButton(
                    text="CANCEL", text_color=self.app.theme_cls.text_color,
                    on_release=self.cancel_import
                ),
                MDRaisedButton(
                    text="IMPORT", text_color=self.app.theme_cls.primary_color,
                    on_release=self.import_project
                )]
        )

    def open_import_popup(self, *args):
        """Open the import popup/dialog"""
        self.import_dialog.set_normal_height()
        self.import_dialog.open()

    def cancel_import(self, *args):
        """Cancel the import, dismiss popup"""
        self.import_dialog.dismiss()

    def import_project(self, *args):
        utils.update_settings()
        import_path = utils.app_settings["project_path"]

        import_type = self.popup_content.import_type
        if import_type == "Folder":
            root = tkinter.Tk()
            root.withdraw()
            selected_project = tkinter.filedialog.askdirectory(initialdir="C:/",
                                                               title="Select a folder").replace("\\", "/")
            try:
                file = open(f"{selected_project}/project_data.json", "r")
                file.close()

                folder_name = selected_project.split('/')[-1] + "_(import)"

                self.ask_save_name(import_type, selected_project, import_path, folder_name)

            except FileNotFoundError:
                self.report_message(f"The selected folder is not a Project Manager project, "
                                    f"it is missing required data")

        elif import_type == ".zip File":
            root = tkinter.Tk()
            root.withdraw()
            selected_project = tkinter.filedialog.askopenfilename(initialdir="C:/", title="Select a .zip file",
                                                                  filetypes=(("Zip Files", ".zip"),)).replace("\\", "/")

            folder_name = selected_project.split("/")[-1].split(".zip")[0] + "_(import)"
            try:
                with ZipFile(selected_project, "r") as zip_file:
                    if "project_data.json" in zip_file.namelist():
                        self.ask_save_name(import_type, selected_project, import_path, folder_name)

                    else:
                        self.report_message(f"{folder_name} is not a Project Manager project, it does not have a "
                                            f"project data file")
            except FileNotFoundError:
                self.report_message(f"** There was an error importing {folder_name.split(' ')[0]} **")

        elif import_type == "Google Drive":
            google_popup = GoogleDriveImport()
            google_popup.open_import_popup()
            self.import_dialog.dismiss()

        # update the projects
        self.import_dialog.dismiss()
        # utils.update_projects()

    def ask_save_name(self, import_type, selected_project, import_path, folder_name, zip_file=None, *args):
        content = ImportFilenameContent(folder_name, import_type)
        self.save_dialog = MDDialog(
            title=f"[color=%s]Edit filename[/color]" %
                  get_hex_from_color(self.app.theme_cls.text_color),
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCEL", text_color=self.app.theme_cls.text_color,
                    on_release=self.cancel_import2
                ),
                MDRaisedButton(
                    text="IMPORT", text_color=self.app.theme_cls.primary_color,
                    on_release=partial(self.save_import_project, content, import_type, selected_project, import_path,
                                       folder_name, zip_file)
                )]
        )
        self.save_dialog.set_normal_height()
        self.save_dialog.open()

    def save_import_project(self, content, import_type, selected_project, import_path,
                            folder_name, zip_file=None, *args):

        if import_type == "Folder":
            try:
                shutil.copytree(selected_project, f"{import_path}/{content.import_name}")
            except FileExistsError:
                pass

            self.report_message(f"{selected_project} successfully imported and renamed to {folder_name}")

        elif import_type == ".zip File":
            with ZipFile(selected_project, "r") as zip_file:
                zip_file.extractall(f"{import_path}/{content.import_name}")
                self.report_message(f"Project has imported as {content.import_name} to {import_path} successfully!")

        self.save_dialog.dismiss()
        utils.update_projects()

    def cancel_import2(self):
        self.save_dialog.dismiss()

    @staticmethod
    def report_message(message):
        Snackbar(text=message).show()
