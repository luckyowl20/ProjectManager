import os
import subprocess
import tkinter
from tkinter import filedialog
from datetime import date

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.core.window import Window as Wd
from kivymd.uix.snackbar import Snackbar

from widgets import utils
from widgets.linkslayout.LinksLayout import LinksLayout

Builder.load_file("widgets/mainlayout/MainLayout.kv")


class MainLayout(MDBoxLayout):
    # the main layout for each project page, consists of the header, progress layout,
    # and information layout (description and filechooser)
    # info layout is what contains the description field and project fields, pretty much all of these properties are for
    # the info layouts for each page
    info_layout = ObjectProperty()
    desc_field = ObjectProperty()
    save_field = ObjectProperty()
    complete_field = ObjectProperty()
    progress_bar = ObjectProperty()
    progress_label = ObjectProperty()
    recent_label = ObjectProperty()
    project_edit_button = ObjectProperty()
    project_open_button = ObjectProperty()
    project_label = ObjectProperty()
    continue_btn = ObjectProperty()
    project_path_label = ObjectProperty()
    selection_button = ObjectProperty()
    select_label = ObjectProperty()
    viewer = ObjectProperty()
    links_layout = ObjectProperty()
    todo_layout = ObjectProperty()

    snackbar = None
    project_path = os.path.abspath(utils.get_project_path().replace("/", "\\"))

    # initializes all the components with their values determined from the json key for the project
    # loads the description from the (projectname)_DESCRIPTION.txt file in the project directory
    def __init__(self, parent_screen, **kwargs):
        super(MDBoxLayout, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.parent_screen = parent_screen
        self.data = self.parent_screen.page_data
        self.desc_field.line_color_normal = self.app.theme_cls.text_color
        self.save_field.text = self.data["start_date"]
        self.complete_field.text = self.data["completion"]
        self.progress_bar.value = self.data["progress"]
        self.progress_label.text = f"[b]Progress: {self.progress_bar.value}%[/b]"
        self.recent_label.text = f"[b]Recent Progress: {self.data['recent_progress']}, Progress made: " \
                                 f"{self.progress_bar.value - self.data['recent_amount']}%[/b]"
        self.selection = ""
        self.path = ""
        self.project_path = self.data['proj_path']
        self.viewer.path = os.path.abspath(self.project_path.replace("/", "\\"))
        self.project_path_label.text = self.get_project_path()
        self.shortened_path = True

        self.read_descriptions()

        temp_selection = [os.getcwd() + "\\" + utils.projects_directory.replace("/", "\\")]
        self.selection_made(temp_selection)

        self.links_layout.update_screen(self.parent_screen)

        self.todo_layout.update_screen(self.parent_screen)

    def update_data(self):
        utils.update_data()
        self.data = utils.data[self.parent_screen.name]

    # reads the descriptions from (projectname)_DESCRIPTION.txt for the project and sets the description
    # field to that text
    def read_descriptions(self):
        # description_path = self.project_path + f"/{self.parent_screen.name}_DESCRIPTION.txt"
        description_path = self.project_path + f"/DESCRIPTION.txt"
        try:
            with open(f"{description_path}", "r") as file:
                self.desc_field.text = file.read()
        except FileNotFoundError:
            with open(f"{description_path}", "w") as file:
                file.write("Type a description here!")
            self.desc_field.text = "Type a description here!"

    # when completion field is edited, save that text
    def save_completion(self):
        self.data["completion"] = self.complete_field.text
        utils.save_project_data(self.data, f"{self.project_path}/project_data.json")

        self.update_data()

    # when start field is edited, save that text
    def save_start(self):
        self.data["start_date"] = self.save_field.text
        utils.save_project_data(self.data, f"{self.project_path}/project_data.json")

        self.update_data()

    # saves the text in the description field to the corresponding page description file
    def save_text(self):
        description_path = self.project_path + f"/DESCRIPTION.txt"
        with open(f"{description_path}", "w") as file:
            file.write(self.desc_field.text)
        for project_card in utils.project_cards:
            if project_card.project == self.parent_screen.name:
                project_card.home_project_desc.text = project_card.home_page.get_project_desc(project_card.project)

    # called when the increment/decrement progress button is pressed, increases progressbar value,
    # updates recent progress, changes the label containing the progress as a number
    def update(self, amount):
        self.update_data()

        self.data = utils.data[self.parent_screen.name]
        self.progress_bar.value += amount
        self.progress_label.text = f"[b]Progress: {self.progress_bar.value}%[/b]"

        # most recent date where progress was made
        recent_date = self.data["recent_progress"]

        today = date.today().strftime("%m/%d/%y%y")

        # only update the recent work date if it is different than today's date
        if not today == recent_date:
            self.data["recent_progress"] = today
            self.recent_label.text = f"[b]Recent Progress: {self.data['recent_progress']}, Progress made: " \
                                     f"{self.progress_bar.value - self.data['recent_amount']}%[/b]"

            # value - amount because we want the difference in the progressbar.value and our
            # recent progress to make it not 0
            self.data["recent_amount"] = self.progress_bar.value - amount

        self.recent_label.text = f"[b]Recent Progress: {self.data['recent_progress']}, Progress made: " \
                                 f"{self.progress_bar.value - self.data['recent_amount']}%[/b]"
        self.data["progress"] = self.progress_bar.value

        # if progress = 100%, update the completion field to todays date because the project is completed,
        # only works with default 'In progress' tag
        if self.progress_bar.value == 100.0 and self.data["completion"] == "In progress":
            self.complete_field.text = today
            self.data["completion"] = today
        else:
            self.complete_field.text = "In progress"
            self.data["completion"] = "In progress"

        # write changes to the json file
        utils.save_project_data(self.data, f"{self.project_path}/project_data.json")

        self.update_data()

        # update the progress information in the ProjectCard for this project
        for project_card in utils.project_cards:
            if project_card.project == self.parent_screen.name:
                project_card.home_progress_bar.value = self.progress_bar.value
                project_card.home_progress_label.text = f"{self.progress_bar.value}%"

    # gets the height for the description layout so scrollview knows when to start scrolling
    def get_height(self):

        if self.info_layout not in utils.info_layouts:
            utils.info_layouts.append(self.info_layout)
        self.info_layout.height = Wd.height - 300
        utils.info_layouts[utils.info_layouts.index(self.info_layout)] = self.info_layout
        return Wd.height - 300

    # prompts the user to select a new project path, saves that path and updates the label to match new path
    def change_project_path(self):
        root = tkinter.Tk()
        root.withdraw()
        selected_folder = tkinter.filedialog.askdirectory()
        self.update_data()

        self.project_path_label.text = selected_folder
        self.project_path = selected_folder
        self.data["proj_path"] = selected_folder
        utils.save_project_data(self.data, f"{self.project_path}/project_data.json")
        self.update_data()

        self.data = utils.data

    # opens the projects project path
    def open_project(self):
        go_to_path = self.project_path.replace('/', '\\')
        subprocess.Popen(f"explorer {go_to_path}")

    # gets the project path label, if it is longer than 40 chars turn on the expand button
    def get_project_path(self):

        project_path = self.project_path
        if len(project_path) > 40:
            split_path = project_path.replace("/", "\\").split("\\")
            project_path = f"\\{split_path[-2]}\\{split_path[-1]}"
            self.continue_btn.disabled = False
            self.continue_btn.text = "..."
            self.project_path_label.text = project_path

        else:
            self.continue_btn.disabled = True
            self.continue_btn.size = 0, self.continue_btn.height

        return project_path.replace("/", "\\")

    # display the project directory when the expand button is pressed
    def expand_directory(self):
        if self.shortened_path:
            self.continue_btn.background_color = 0, 0, 0, 1
            self.project_path_label.text = self.project_path
            self.continue_btn.background_color = 0, 0, 0, 0
            self.shortened_path = False
        else:
            self.shortened_path = True
            self.continue_btn.background_color = 0, 0, 0, 1
            self.get_project_path()
            self.continue_btn.background_color = 0, 0, 0, 0

    # opens the selected file, if nothing is selected, show an error
    def open_selection(self):
        try:
            # str or list, if string from making project directory into selection, list if from filechooser
            if type(self.selection) is str:
                subprocess.Popen(f'explorer {self.selection}')
            else:
                subprocess.Popen(f'explorer {self.selection[-1]}')
        except IndexError:
            Snackbar(test="Please select a file or directory before opening it").show()

    # makes the project directory into the selection
    def select_project_dir(self):
        self.selection = self.project_path.replace("/", "\\")
        self.viewer.project_path = self.selection
        self.select_label.text = f"[b]Selection [/b][i](DIR)[/i][b]: [/b]{self.selection}"
        self.selection_button.tooltip_text = "Open selected directory"
        self.selection_button.icon = "folder-open-outline"

    # called when a file from filechooser is selected
    def selection_made(self, selection):
        self.selection = selection

        if len(self.selection) == 0:
            self.selection_button.icon = 'window-close'
            self.select_label.text = "[b]Selection: [/b]None"
        try:
            selection_text = self.selection[-1].replace('/', '\\')
            if os.path.isdir(self.selection[-1]):
                self.select_label.text = f"[b]Selection [/b][i](DIR)[/i][b]: [/b]{selection_text}"
                self.selection_button.icon = "folder-open-outline"
                self.selection_button.tooltip_text = "Open selected directory"
            else:
                self.select_label.text = f"[b]Selection [/b][i](FILE)[/i][b]: [/b]{selection_text}"
                self.selection_button.icon = "open-in-new"
                self.selection_button.tooltip_text = "Open selected file"

        except IndexError:
            pass
