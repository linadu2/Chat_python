from pystray import Icon
from PIL import Image
from pystray import MenuItem , Menu
from requests import get, post, Timeout, head, ConnectionError
from json import loads
from HomeAssistant.readconf import get_data, get_headers, write_json
import tkinter as tk
import setup
import threading
from time import sleep
import first_setup



class SysTray:
    def __init__(self, conf_file, credentials_file, ico):
        self.stop = None
        self.states, self.services, self.url, self.settings = get_data(conf_file, 'States', 'Services', 'InstanceUrl', 'Settings')
        self.conf_file = conf_file
        self.credentials_file = credentials_file
        self.header = get_headers(get_data(credentials_file, 'Token'))
        first_setup_flag = False
        if not get_data(credentials_file, 'Token'):
            first_setup_flag = True
            self.first_setup()







        self.icon_image = Image.open(ico)
        self.icon = Icon("HA_icon", self.icon_image, menu=self.setup_menu())

        self.states_dict = dict([[state[0], self.get_ha(state[0])] for state in self.states])

        self.check_setting()

        if first_setup_flag:
            self.start_setup()


    def first_setup(self):

        root = tk.Tk()
        root.geometry('300x75')
        root.title('first setup')
        app = first_setup.App(root, self.conf_file, self.credentials_file)
        root.mainloop()
        self.states, self.services, self.url, self.settings = get_data(self.conf_file, 'States', 'Services', 'InstanceUrl','Settings')
        self.header = get_headers(get_data(self.credentials_file, 'Token'))





    def check_setting(self):
        if self.settings['autoRefresh']:
            # print('start auto refresh')
            self.start_auto_refresh()
        if self.stop is not None and not self.settings['autoRefresh']:
            # print('stop auto refresh')
            self.stop.set()
            self.stop = None


    def toggle_settings(self, setting):
        self.settings[setting] = not self.settings[setting]

        data = get_data(self.conf_file, 'Settings')
        data[setting] = self.settings[setting]

        write_json(self.conf_file, 'Settings', data)

        self.check_setting()


    # def get_states(self, entity):
    #     # print(entity, self.states_dict[entity])
    #     return self.states_dict[entity]

    def refresh_state(self):
        # print('refresh')

        for entity in self.states_dict:
            self.states_dict[entity] = self.get_ha(entity)
        self.icon.menu = self.setup_menu()

        # print(self.states_dict)


    def run_icon(self):
        self.icon.run()

    def on_quit(self):
        self.icon.stop()

    def post_ha(self, item):
        url = self.services[str(item)][0]
        entity_id = self.services[str(item)][1]
        # print(url, entity_id)
        data = {
            "entity_id": entity_id
        }
        try:
            post(f"http://{self.url}:8123/api/services/{url}", headers=self.header, json=data)
        except Timeout:
            pass
        except ConnectionError:
            pass

    def get_ha(self, entity_id):
        if self.home_assistant_reachable():
            response = get(f"http://{self.url}:8123/api/states/{entity_id}", headers=self.header, timeout=1)
            return loads(response.text)['state']
        else:
            return '--'

    def home_assistant_reachable(self, timeout=2):
        try:
            response = head(f'http://{self.url}:8123/api/states', timeout=timeout)
            if response.status_code == 405:
                return True
            else:
                return False
        except ConnectionError:
            return False
        except Timeout:
            return False

    def setup_menu(self):

        menu_items = []
        for item_state in self.states:
            menu_items.append(MenuItem(lambda text, entity=item_state[0], symbol=item_state[1]: f"{self.states_dict[entity]} {symbol}", lambda: None,
                                       enabled=False))

        menu_items.append(Menu.SEPARATOR)

        for item_state in self.services:
            menu_items.append(MenuItem(lambda text, name=item_state: name,
                                       lambda icon, item: self.post_ha(item)))

        menu_items.append(Menu.SEPARATOR)

        sub_menu = Menu(
            MenuItem('Auto Refresh', lambda : self.toggle_settings('autoRefresh'), checked=lambda item : self.settings['autoRefresh']),
            MenuItem('Setup', lambda: self.start_setup()),
            MenuItem('HA IP and Token', self.first_setup)
        )

        menu_items.append(MenuItem('Configuration', sub_menu))
        menu_items.append(MenuItem('Refresh', lambda: self.refresh_state()))
        menu_items.append(MenuItem('Quit', self.on_quit))
        return Menu(*menu_items)

    def start_setup(self):
        if not self.home_assistant_reachable():
            return ''
        thread = threading.Thread(target=invoke_app, args=(self.url, self.header))
        thread.start()
        thread.join()

        self.states, self.services = get_data(self.conf_file, 'States', 'Services')
        self.states_dict = dict([[state[0], self.get_ha(state[0])] for state in self.states])

        self.icon.menu = self.setup_menu()

    def start_auto_refresh(self):
        self.stop = threading.Event()
        thread = threading.Thread(target=invoke_refreseher, args=(self, self.stop), daemon=True)
        thread.start()




def invoke_app(ha, header):
    root = tk.Tk()
    root.geometry('600x500')
    root.resizable(width=False, height=False)
    app = setup.App(root, ha, header)
    root.mainloop()

def invoke_refreseher(obj, stop):
    while not stop.is_set():
        obj.refresh_state()
        sleep(60)




if __name__ == '__main__':

    obj = SysTray('config.json','credentials.json', 'Home_Assistant_Logo.ico')
    obj.run_icon()



