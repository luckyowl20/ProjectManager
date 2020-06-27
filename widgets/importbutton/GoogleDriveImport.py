import io
import os
import pickle
import threading
from zipfile import ZipFile

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

from kivy.app import App
from kivy.clock import mainthread
from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import ObjectProperty
from kivy.utils import get_hex_from_color
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineAvatarIconListItem
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.spinner import MDSpinner

from widgets import utils

Builder.load_file("widgets/importbutton/GoogleDriveImport.kv")
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/drive.file']


class GoogleFileEntry(OneLineAvatarIconListItem):

    def __init__(self, parent_list, **kwargs):
        """Init folder item"""
        super(OneLineAvatarIconListItem, self).__init__(**kwargs)
        self.parent_list = parent_list
        self.app = App.get_running_app()

    def file_selected(self, file):
        for parent_file in self.parent_list.file_entries:
            if parent_file == file:
                parent_file.bg_color = self.app.theme_cls.primary_light
            else:
                parent_file.bg_color = [0, 0, 0, 0]

        self.parent_list.content.selected_file_label.text = f"[b]Selected file: [/b][i]{file.text}[/i]"
        self.parent_list.selected_file = file.text
        self.parent_list.content.original_filename_label.text = f"[b]Original filename: [/b]{file.text}"
        self.parent_list.content.filename_field.text = file.text.split('.')[0] + "_gimport"


class GoogleImportPopupContent(MDBoxLayout):
    file_list = ObjectProperty()
    selected_file_label = ObjectProperty()
    spinner_container = ObjectProperty()

    # filename edit objects
    filename_layout = ObjectProperty()
    original_filename_label = ObjectProperty()
    filename_field = ObjectProperty()

    def __init__(self, parent_layout, original_filename, **kwargs):
        super(MDBoxLayout, self).__init__(**kwargs)
        self.parent_layout = parent_layout
        self.original_filename_label.text = f"[b]Original filename: [/b] {original_filename}"

    def filename_text_edited(self, text):
        self.parent_layout.filename = text


class GoogleDriveImport:
    def __init__(self):
        self.import_popup = None
        self.app = App.get_running_app()
        self.search_results = []
        self.file_entries = []
        self.selected_file = ""
        self.content = GoogleImportPopupContent(self, "Nothing selected")
        self.filename = "None"

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

    def search(self, query):
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
        self.search_results = []
        self.file_entries = []
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

            page_token = response.get('nextPageToken', None)
            if not page_token:
                # no more files
                break
        self.search_results = result
        self.update_files_list()
        return

    def download_file(self, file_id, filename):

        request = self.get_gdrive_service().files().get_media(fileId=file_id)
        cwd = os.getcwd()
        os.chdir('temp')
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        with io.open(filename, 'wb') as file:
            fh.seek(0)
            file.write(fh.read())
        os.chdir(cwd)

        import_path = utils.app_settings["project_path"]
        # folder_name = filename.split(".")[0] + "_gimport"
        folder_name = self.filename
        try:
            with ZipFile(f"temp/{filename}", "r") as zip_file:
                if "project_data.json" in zip_file.namelist():
                    zip_file.extractall(f"{import_path}/{folder_name}")
                    self.prompt_success(folder_name, import_path)
                else:
                    self.report_message(f"File is not a Project Manager Project, missing project data file")

        except FileNotFoundError:
            self.report_message(f"** There was an error importing {filename} **")

    @mainthread
    def update_files_list(self):
        self.content.spinner_container.clear_widgets()
        self.file_entries = []
        for result in self.search_results:
            file_entry = GoogleFileEntry(self)
            file_entry.text = result[1]
            self.file_entries.append(file_entry)
            self.content.file_list.add_widget(file_entry)

    def fetch_search(self):
        threading.Thread(target=self.search, args=(f"mimeType='application/x-zip-compressed' and trashed=false",),
                         daemon=True).start()

    def open_import_popup(self):
        self.fetch_search()
        if not self.import_popup:
            self.import_popup = MDDialog(
                title=f"[color=%s]Import project from Google Drive[/color]" %
                      get_hex_from_color(self.app.theme_cls.text_color),
                type="custom",
                content_cls=self.content,
                buttons=[
                    MDFlatButton(
                        text="CANCEL", text_color=self.app.theme_cls.text_color, on_release=self.close_import_dialog
                    ),
                    MDRaisedButton(
                        text="DOWNLOAD", text_color=self.app.theme_cls.primary_color,
                        on_release=self.start_download_thread
                    )],
                size_hint=(None, None), size=(self.content.width + 50, self.content.height + 50)
            )
        self.import_popup.set_normal_height()
        self.import_popup.open()

    def start_download_thread(self, *args):
        file_object = ()
        for result in self.search_results:
            if self.selected_file in result:
                file_object = result
        if not len(file_object) == 0:
            self.report_message(f"Starting download on {file_object[1]}")
            threading.Thread(target=self.download_file, args=(file_object[0], file_object[1]), daemon=True).start()
        else:
            self.report_message("Please select a project before downloading it.")

    def close_import_dialog(self, *args):
        self.import_popup.dismiss()

    @mainthread
    def prompt_success(self, folder_name, import_path):

        utils.update_projects()
        self.report_message(f"Project has imported as {folder_name} to {import_path} successfully!")

    @staticmethod
    @mainthread
    def report_message(message):
        Snackbar(text=message).show()