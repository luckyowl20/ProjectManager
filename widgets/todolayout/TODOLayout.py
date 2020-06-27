from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard

from widgets import utils

Builder.load_file("widgets/todolayout/TODOLayout.kv")


class TODOCheckItem(MDBoxLayout):
    item_checkbox = ObjectProperty()
    item_text_field = ObjectProperty()
    item_close_btn = ObjectProperty()

    def __init__(self, parent_list, item_text=None, check_active=False, **kwargs):
        super(MDBoxLayout, self).__init__(**kwargs)
        self.parent_list = parent_list
        self.parent_list.height += self.height
        self.parent_list.total_items.append(self)
        self.screen_name = self.parent_list.parent_layout.parent_screen.name
        self.correct_index = self.parent_list.parent_layout.todo_list_ids.index(self.parent_list.list_id)
        self.self_index = self.parent_list.total_items.index(self)
        utils.todo_checkboxes.append(self)
        if not item_text:
            self.item_text_field.text = "New item"
        else:
            self.item_text_field.text = item_text
        if check_active:
            self.item_checkbox.state = 'down'

    def update_check_item(self):
        utils.update_data()
        if self.item_checkbox.state == 'down':
            self.parent_list.active_items += 1
            save_state = True

        else:
            self.parent_list.active_items -= 1
            save_state = False

        self.parent_list.todo_completion.text = f"{self.parent_list.active_items}/" \
                                                f"{len(self.parent_list.total_items)} Completed"

        # try except added bc of a bug with editing started and completed field, i think this is caused by
        # self.correct_index changing when that is changed, i don't think that this bug is super critical but it can be
        # TODO: investigate this bug ^
        try:
            utils.data[self.screen_name]['todo_lists'][self.correct_index]['items'][self.self_index][-1] = save_state
        except IndexError:
            pass

        utils.save_project_data(utils.data[self.screen_name],
                                f"{utils.data[self.screen_name]['proj_path']}/project_data.json")

    def remove_todo_item(self):
        self.parent_list.height -= self.height

        try:
            utils.data[self.screen_name]['todo_lists'][self.correct_index]['items'].pop(self.self_index)
        except IndexError:
            pass

        utils.save_project_data(utils.data[self.screen_name],
                                f"{utils.data[self.screen_name]['proj_path']}/project_data.json")

        self.parent_list.total_items.remove(self)
        self.parent_list.todo_check_items.remove_widget(self)
        if self.item_checkbox.state == 'down':
            self.parent_list.active_items -= 1
        if len(self.parent_list.total_items) == 0:
            self.parent_list.todo_completion.text = ""
        else:
            self.parent_list.todo_completion.text = f"{self.parent_list.active_items}/" \
                                                    f"{len(self.parent_list.total_items)} Completed"

    def save_item_text(self):
        new_title = self.item_text_field.text
        utils.update_data()
        utils.data[self.screen_name]['todo_lists'][self.correct_index]['items'][self.self_index][0] = new_title
        utils.save_project_data(utils.data[self.screen_name],
                                f"{utils.data[self.screen_name]['proj_path']}/project_data.json")
        utils.update_data()


class TODOListCard(MDBoxLayout):
    todo_title_field = ObjectProperty()
    todo_check_items = ObjectProperty()
    todo_completion = ObjectProperty()

    def __init__(self, parent_layout, list_id, title_text=None, check_info=None, **kwargs):
        super(MDBoxLayout, self).__init__(**kwargs)
        self.parent_layout = parent_layout
        self.size_hint = None, None
        self.total_items = []
        self.active_items = 0
        self.list_id = list_id
        if title_text is not None:
            self.todo_title_field.text = title_text
        if check_info is not None:
            for check in check_info:
                self.add_check_item(check[0], check[1], True)

    def add_check_item(self, title=None, active=None, from_load=False):
        new_item = TODOCheckItem(self, title, active)
        self.todo_check_items.add_widget(new_item)
        self.todo_completion.text = f"{self.active_items}/{len(self.total_items)} Completed"
        utils.update_data()
        new_check = ["New item", False]

        if not from_load:
            utils.data[self.parent_layout.parent_screen.name]['todo_lists'][self.parent_layout.todo_list_ids.index(
                self.list_id)]['items'].append(new_check)
            utils.save_project_data(utils.data[self.parent_layout.parent_screen.name],
                                    f"{utils.data[self.parent_layout.parent_screen.name]['proj_path']}/"
                                    f"project_data.json")
        utils.update_data()

    def delete_todo_list(self):
        self.parent_layout.todo_stack_layout.remove_widget(self)
        utils.data[self.parent_layout.parent_screen.name]['todo_lists'].pop(self.parent_layout.todo_list_ids.index(
            self.list_id))
        utils.save_project_data(utils.data[self.parent_layout.parent_screen.name],
                                f"{utils.data[self.parent_layout.parent_screen.name]['proj_path']}/project_data.json")
        self.parent_layout.todo_list_ids.remove(self.list_id)
        utils.update_data()

    def save_todo_title(self):
        utils.data[self.parent_layout.parent_screen.name]['todo_lists'][self.parent_layout.todo_list_ids.index(
            self.list_id)]['title'] = self.todo_title_field.text
        utils.save_project_data(utils.data[self.parent_layout.parent_screen.name],
                                f"{utils.data[self.parent_layout.parent_screen.name]['proj_path']}/project_data.json")
        utils.update_data()


class TODOLayout(MDBoxLayout):
    add_todo_list_button = ObjectProperty()
    todo_stack_layout = ObjectProperty()

    def __init__(self, **kwargs):
        super(MDBoxLayout, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.parent_screen = None
        self.todo_lists = []
        self.todo_list_ids = []

    def add_todo_list(self):
        new_id = utils.generate_hash_id()
        new_list = TODOListCard(self, new_id)
        self.todo_list_ids.append(new_id)
        self.todo_stack_layout.add_widget(new_list)
        utils.data[self.parent_screen.name]['todo_lists'].append({
            "id": new_id,
            "title": "Card title",
            "items": []
        })
        utils.save_project_data(utils.data[self.parent_screen.name],
                                f"{utils.data[self.parent_screen.name]['proj_path']}/project_data.json")
        utils.update_data()

    def update_screen(self, screen):
        self.parent_screen = screen
        self.todo_lists = utils.data[self.parent_screen.name]['todo_lists']
        for todo_list in self.todo_lists:
            self.todo_list_ids.append(todo_list['id'])
            self.todo_stack_layout.add_widget(TODOListCard(self, todo_list['id'],
                                                           todo_list['title'], todo_list['items']))
