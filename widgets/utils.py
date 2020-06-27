import gc
import hashlib
import json
import os
import random

from kivy.app import App

# the data about each project
data = {}

# the window, 1 per project
windows = []

# window manager pointer, used to add windows when projects are imported
window_manager = None

# the layouts containing
info_layouts = []

# the bottom banner in layout2 that needed to be updated manually when the theme style was edited
bottom_banners = []

# file entries for the viewer widget that need color updated, never cleared can be an issue
files = []

# each project entry in the navigation menu, needed to change text when title is edited
menu_projects = []

# the one line list items for each theme in settings -> appearance used to update checkbox status
theme_checkboxes = []
checkbox_text = []

# checkboxes for each todolist
todo_checkboxes = []

# list to track the cards to make it easier to update on progress change, on description save, on title change
project_cards = []

# the path where the program should look for new projects and the folder/directory for each project in that path
projects_directory = ""
project_folders = []
project_data_paths = []
failed_projects = []

# project keys and number of projects
keys = []
num_projects = []

# the ProjectManager class from main.py
project_manager = None

# app settings, default things and theme type: dict
app_settings = {}

# separator lines on each window
separators = []


def generate_hash_id():
    numbers = ""
    for i in range(20):
        numbers += str(random.randint(0, 9))
    return hashlib.sha1(numbers.encode()).hexdigest()


def save_project_data(some_data, path):
    save_data = {"data": some_data}
    with open(path, "w") as file:
        json.dump(save_data, file)


def update_settings():
    global app_settings
    with open("settings.json", "r") as file:
        app_settings = json.load(file)


def get_project_path():
    global projects_directory, app_settings
    with open("settings.json", "r") as file:
        app_settings = json.load(file)
    projects_directory = app_settings["project_path"]
    return projects_directory


# gets a list of projects found in the project path
def get_projects():
    global projects_directory, project_folders, failed_projects, data, project_data_paths
    projects_directory = ""
    project_folders = failed_projects = project_data_paths = []
    data = {}
    with open("settings.json", "r") as file:
        projects_directory = json.load(file)["project_path"]

    project_folders = os.listdir(projects_directory)

    working_projects = []
    for index, project in enumerate(project_folders):
        path_to_project = f"{projects_directory}/{project}"
        try:
            with open(f"{path_to_project}/project_data.json", "r") as file:
                data[project] = json.load(file)['data']

            project_data_paths.append(f"{path_to_project}/project_data.json")
            working_projects.append(project)
        except FileNotFoundError:
            failed_projects.append(project)

    # this loop renames the proj_path if it is valid in the project_data
    for index, project in enumerate(working_projects):
        path_to_project = f"{projects_directory}/{project}"
        with open(project_data_paths[index], "r") as file:
            temp_data = json.load(file)['data']
        temp_proj_path = temp_data['proj_path']

        if not os.path.isdir(os.path.abspath(temp_proj_path.replace('/', '\\'))):
            temp_data['proj_path'] = path_to_project
            data[project] = temp_data
            new_data = {'data': temp_data}
            with open(project_data_paths[index], "w") as file:
                json.dump(new_data, file)

    for index, project in enumerate(working_projects):
        path_to_project = f"{projects_directory}/{project}"
        try:
            open(f"{path_to_project}/DESCRIPTION.txt", "r")
        except FileNotFoundError:
            try:
                with open(f"{path_to_project}/DESCRIPTION.txt", "w") as file:
                    file.write("Type a description here!")

                # updates the project path if it does not work? not sure what the function of this block is but
                # it is needed for initialization to work right
                data[project]["proj_path"] = path_to_project
                new_data = {"data": data[project]}
                with open(f"{path_to_project}/project_data.json", "w") as file:
                    json.dump(new_data, file)

            except FileNotFoundError:
                print(f"Failed to create desc for {project}")


def update_projects():
    global keys, window_manager, data
    old_keys = keys

    get_projects()
    update_keys()
    for key in keys:
        if key not in old_keys:
            # adds a new window from window manager
            project_path = app_settings["project_path"]
            new_data = data[key]
            new_data['proj_path'] = project_path + f"\\{key}"
            save_project_data(new_data, f"{project_path}\\{key}\\project_data.json")
            window_manager.add_null_window(key)
            break


def clean_data():
    global data, windows
    temp_keys = data.keys()
    names = [window.name for window in windows]
    remove_keys = []
    for key in temp_keys:
        if key not in names:
            remove_keys.append(key)
    for key in remove_keys:
        del data[key]
    gc.collect()


# refresh the data in the json file
def update_data():
    global data, project_data_paths
    for project in project_data_paths:
        try:
            with open(project, "r") as file:
                data[keys[project_data_paths.index(project)]] = json.load(file)['data']
        except FileNotFoundError:
            failed_projects.append(project)


# to update the next_page and back page after the new page has been added
def update_changes(call_root=True, add_project_widget=True):
    global windows
    update_data()
    update_keys()
    if len(windows) == 1:
        project_manager.update_nav(windows[-1], add_project_widget)
        windows[-1].back = windows[-1].name
        windows[-1].next_page = windows[-1].name
    elif len(windows) > 1:
        for count, window in enumerate(windows):
            if window == windows[0] and windows[count + 1] is not None:
                window.back = window.name
                window.next_page = windows[windows.index(window) + 1].name

            elif window == windows[-1] and windows[count - 1] is not None:
                window.back = windows[windows.index(window) - 1].name
                window.next_page = window.name

            else:
                window.back = windows[windows.index(window) - 1].name
                window.next_page = windows[windows.index(window) + 1].name
        if call_root:
            project_manager.update_nav(windows[-1], add_project_widget)
    update_data()


def save_settings(new_settings):
    with open("settings.json", "r") as file:
        settings = json.load(file)
    for setting in new_settings:
        settings[setting] = new_settings[setting]

    with open("settings.json", "w") as file:
        json.dump(settings, file)


def get_num_projects():
    global num_projects
    with open("settings.json", "r") as file:
        num_projects = json.load(file)["num_projects"]
    return num_projects


def update_keys():
    global keys, num_projects
    keys = list(data.keys())
    num_projects = len(keys)


get_projects()
get_project_path()
update_keys()
gc.set_threshold(250, 15, 15)
gc.enable()
