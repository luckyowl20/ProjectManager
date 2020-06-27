from __future__ import print_function

import threading
import pickle
import os.path
from zipfile import ZipFile

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload

from kivy.app import App
from kivy.clock import mainthread
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.utils import get_hex_from_color
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineAvatarIconListItem
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.spinner import MDSpinner

from widgets import utils

Builder.load_file("widgets/exportbutton/GoogleDriveExport.kv")
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/drive.file']


# removed ToggleButtonBehavior
class GoogleProjectEntry(OneLineAvatarIconListItem):
    """
    List item for each folder in the users google drive
    """

    def __init__(self, parent_layout, **kwargs):
        """Init folder item"""
        super(OneLineAvatarIconListItem, self).__init__(**kwargs)
        self.parent_layout = parent_layout
        self.app = App.get_running_app()

    def project_selected(self, project_entry):
        """
        Called when a project is selected, updates background color to be theme.primary_light
        :param project_entry: object
        :return: None
        """

        for project in self.parent_layout.project_entries:
            if project == project_entry:
                project.bg_color = self.app.theme_cls.primary_light
            else:
                project.bg_color = [0, 0, 0, 0]
        self.parent_layout.content.selected_folder_label.text = f"[b]Selected folder: [/b][i]{project_entry.text}[/i]"
        self.parent_layout.selected_folder = project_entry.text

    def open_selected_folder(self, project_entry):
        """
        Open the selected folder in new thread to prevent blocking UI responsiveness
        :param project_entry: object
        :return: None
        """
        threading.Thread(target=self.secondary_update, args=(project_entry,), daemon=True).start()

    def secondary_update(self, project_entry):
        """
        Makes API call to Google Drive and updates the layout using @mainthread functions to have render-related
        processes in the main thread instead of child threads

        :param project_entry: object
        :return: None
        """
        self.parent_layout.clear_projects()
        self.update_selected_project(project_entry)

        new_folder = self.find_folder_in_results(project_entry.text)

        self.parent_layout.selected_folder = new_folder
        self.parent_layout.search(f"mimeType='application/vnd.google-apps.folder' "
                                  f"and trashed=false "
                                  f"and '{new_folder[0]}' in parents", self.parent_layout.content, False)
        self.parent_layout.update_projects_widget()
        # returns to kill thread, not sure if needed
        return

    @mainthread
    def update_selected_project(self, project_entry):
        """Update selected folder label so the user knows which folder is selected"""
        self.parent_layout.content.selected_folder_label.text = f"[b]Selected folder: [/b][i]{project_entry.text}[/i]"

    def find_folder_in_results(self, folder_name):
        """
        Checks if a folder is in the search results
        :param folder_name: str
        :return: tuple
        """
        folder = ()
        for result in self.parent_layout.search_results:
            if folder_name in result:
                folder = result
        return folder


class GoogleExportPopupContent(MDBoxLayout):
    """
    Content of the popup when export is pressed and "Google Drive" is selected
    """
    projects_list = ObjectProperty()
    selected_folder_label = ObjectProperty()
    spinner_container = ObjectProperty()

    def __init__(self, parent_layout, **kwargs):
        """Init content"""
        super(MDBoxLayout, self).__init__(**kwargs)
        self.parent_layout = parent_layout

    def back_project(self):
        """Sets the selected folder to "My Drive" (root folder) and updates required values"""
        self.parent_layout.search_results = self.parent_layout.root_projects
        self.parent_layout.selected_folder = "root"
        self.selected_folder_label.text = "[b]Selected folder: [/b][i]My Drive[/i]"
        self.parent_layout.clear_projects()
        self.parent_layout.update_projects_widget()


class GoogleDriveExport:
    """
    Main class for handling the export to google drive
    """

    def __init__(self, parent_screen, export_filename, **kwargs):
        self.parent_screen = parent_screen
        self.export_filename = export_filename
        self.export_popup = None
        self.app = App.get_running_app()
        self.search_results = []
        self.project_entries = []
        self.root_projects = []
        self.visited_projects = []
        self.content = GoogleExportPopupContent(self)
        self.selected_folder = "root"

    @staticmethod
    def get_gdrive_service():
        """
        Gets the google drive service so we can upload to the users account
        Not completely sure how this works, treated as black box
        :return: object
        """
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        # return Google Drive API service
        return build('drive', 'v3', credentials=creds)

    def search(self, query, content, first=True):
        """
        Search for a given file/folder in the users drive based on query
        :param query: str
        :param content: object - popup content
        :param first: bool
        :return: None
        """
        # search for the file
        service = self.get_gdrive_service()
        result = []
        page_token = None
        while True:
            response = service.files().list(q=query,
                                            spaces="drive",
                                            fields="nextPageToken, files(id, name, mimeType, parents)",
                                            pageToken=page_token).execute()
            # iterate over filtered files
            for file in response.get("files", []):
                try:
                    parent_id = file['parents']
                except KeyError:
                    parent_id = "N/A"
                result.append((file["id"], file["name"], file["mimeType"], parent_id))

                # print(type(list(file.keys())[-1]))
            page_token = response.get('nextPageToken', None)
            if not page_token:
                # no more files
                break
        self.search_results = result
        if first:
            self.update_projects_widget(content)
            self.root_projects = result
        return

    @mainthread
    def clear_projects(self):
        """Remove all project list items and add a spinner to signify loading"""
        self.content.projects_list.clear_widgets()
        self.content.spinner_container.add_widget(MDSpinner(
            size_hint=(None, None), pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size=(dp(48), dp(48))
        ))

    @mainthread
    def update_projects_widget(self, *args):
        """Updates the layout for new projects after api call has finished"""
        self.content.spinner_container.clear_widgets()
        self.project_entries = []
        for result in self.search_results:
            project_entry = GoogleProjectEntry(self)
            project_entry.text = result[1]
            self.project_entries.append(project_entry)
            self.content.projects_list.add_widget(project_entry)

    def fetch_search(self, content):
        """Start a new thread to search the users Google Drive and prevent blocking UI thread"""
        threading.Thread(target=self.search, args=(f"mimeType='application/vnd.google-apps.folder' "
                                                   f"and trashed=false "
                                                   f"and 'root' in parents", content,), daemon=True).start()

    def open_export_popup(self):
        """
        Opens the export popup and initiates a search for their projects, if no user signed in, search prompts a sign in
        :return: None
        """
        self.fetch_search(self.content)
        if not self.export_popup:
            self.export_popup = MDDialog(
                title=f"[color=%s]Upload project to Google Drive[/color]" %
                      get_hex_from_color(self.app.theme_cls.text_color),
                type="custom",
                content_cls=self.content,
                buttons=[
                    MDFlatButton(
                        text="CANCEL", text_color=self.app.theme_cls.text_color, on_release=self.close_export_dialog
                    ),
                    MDRaisedButton(
                        text="UPLOAD", text_color=self.app.theme_cls.primary_color,
                        on_release=self.start_upload_thread
                    )],
                size_hint=(None, None), size=(self.content.width + 50, self.content.height + 50)
            )
        self.export_popup.title = f"[color=%s]Upload project to Google Drive[/color]" % \
                                  get_hex_from_color(self.app.theme_cls.text_color)
        self.export_popup.set_normal_height()
        self.export_popup.open()

    def start_upload_thread(self, *args):
        """Start the thread to upload project and prevent UI blocking"""
        threading.Thread(target=self.upload_project, daemon=True).start()

    def upload_project(self, *args):
        """Upload the users project to their google drive"""
        self.start_upload_ui()
        cwd = os.getcwd()

        # abs path of project
        project = os.path.abspath(utils.data[self.parent_screen.name]['proj_path'])
        files = []
        for file in os.listdir(project):
            files.append(file)

        # send to zip file and save in temp so we can export to drive
        with ZipFile(f"temp/{self.export_filename}.zip", "w") as project_upload:
            os.chdir(project)
            for file in files:
                project_upload.write(file)

        os.chdir(cwd)

        folder_id = "root" if type(self.selected_folder) == str else self.selected_folder[0]

        file_metadata = {
            "name": f"{self.export_filename}.zip",
            "parents": [folder_id]
        }

        # upload project
        try:
            service = self.get_gdrive_service()
            media = MediaFileUpload(f"temp/{self.export_filename}.zip", resumable=True)
            service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            self.prompt_success()
        # not sure what exceptions could be raised here
        except Exception:
            self.prompt_failure()
        return

    @mainthread
    def start_upload_ui(self):
        """Provides info to user that upload has started"""
        if type(self.selected_folder) == str:
            folder = "My Drive"
        else:
            folder = self.selected_folder[1]

        self.export_popup.dismiss()
        Snackbar(text=f"Starting upload of {self.export_filename}.zip to "
                      f"{folder} in Google Drive").show()

    @mainthread
    def prompt_success(self):
        """Prompts the suer that their upload has succeeded"""
        if type(self.selected_folder) == str:
            folder = "My Drive"
        else:
            folder = self.selected_folder[1]

        Snackbar(text=f"{utils.data[self.parent_screen.name]['title']} exported"
                      f" to {folder} in Google Drive as "
                      f"{self.export_filename}.zip successfully").show()

    @mainthread
    def prompt_failure(self):
        """Prompts the suer that their upload has failed"""
        if type(self.selected_folder) == str:
            folder = "My Drive"
        else:
            folder = self.selected_folder[1]

        Snackbar(text=f"** Failed to export {utils.data[self.parent_screen.name]['title']} "
                      f"to {folder} in Google Drive as "
                      f"{self.export_filename}.zip **").show()

    def close_export_dialog(self, *args):
        """Close the export dialog"""
        self.export_popup.dismiss()
