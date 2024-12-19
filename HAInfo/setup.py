from re import search
from requests import get
from json import loads
from HomeAssistant.readconf import get_data, get_headers, write_json
import tkinter as tk
from tkinter import ttk, StringVar, IntVar



class App:
    def __init__(self, root, ha, header):
        self.root = root

        self.ha = ha
        self.header = header

        self.notebook1 = ttk.Notebook(root)
        self.notebook1.pack(expand=True, fill='both')

        self.frame_services = tk.Frame(self.notebook1)
        self.frame_states = tk.Frame(self.notebook1)

        self.notebook1.add(self.frame_services, text='Services')
        self.notebook1.add(self.frame_states, text='Sensor')


        self.array_entity_services = []
        self.array_var_services = []

        self.sub_frame_left_frame_services = tk.Frame(self.frame_services)
        self.sub_frame_left_frame_services.pack(side='left', fill='both', expand=True)

        self.sub_frame_right_frame_services = tk.Frame(self.frame_services)
        self.sub_frame_right_frame_services.pack(side='left', fill='both', expand=True)

        self.frame_entry_services = tk.Frame(self.sub_frame_left_frame_services)
        self.frame_entry_services.pack(pady=10)

        self.label_entry_services = tk.Label(self.frame_entry_services, text='Search:')
        self.label_entry_services.pack(side='left')

        self.var_entry_services = StringVar()
        self.var_entry_services.trace('w', lambda name, index, mode, var=self.var_entry_services: create_checkbox(self.search_entity('toggle', var), self.sub_frame_left_frame_services, 'Services', self.array_entity_services, self.array_var_services, self.command_ckeckbox_service))

        self.entry_services = tk.Entry(self.frame_entry_services, textvariable=self.var_entry_services)
        self.entry_services.pack(side='left')



        self.button_list_services = []
        self.frame_list_services = []
        self.label_list_services = []

        create_label_services(get_data('config.json', 'Services'), self.sub_frame_right_frame_services, self.label_list_services, self.frame_list_services, self.button_list_services)



        self.array_entity_states = []
        self.array_var_states = []

        self.sub_frame_left_frame_states = tk.Frame(self.frame_states)
        self.sub_frame_left_frame_states.pack(side='left', expand=True, fill='both')

        self.sub_frame_right_frame_states = tk.Frame(self.frame_states)
        self.sub_frame_right_frame_states.pack(side='left', expand=True, fill='both')

        self.frame_entry_states = tk.Frame(self.sub_frame_left_frame_states)
        self.frame_entry_states.pack(pady=10)

        self.label_entry_states = tk.Label(self.frame_entry_states, text='Search:')
        self.label_entry_states.pack(side='left')

        self.var_entry_states = StringVar()
        self.var_entry_states.trace('w', lambda name, index, mode, var=self.var_entry_states: create_checkbox(self.search_entity('sensor', var), self.sub_frame_left_frame_states, 'States', self.array_entity_states, self.array_var_states, self.command_ckeckbox_state))

        self.entry_states = tk.Entry(self.frame_entry_states, textvariable=self.var_entry_states)
        self.entry_states.pack(side='left')


        self.frame_list_states = []
        self.label_list_states = []

        create_label_states(get_data('config.json', 'States'), self.sub_frame_right_frame_states,
                     self.label_list_states, self.frame_list_states)


    def search_entity(self, entity_type, var):
        result = get_api(self.ha, 'states', self.header)
        # print(result)
        if entity_type == 'toggle':
            # print('toggle')
            res = sort_state(result, 'light', var.get())
            result = res + sort_state(result, 'switch', var.get())
        elif entity_type == 'sensor':
            # print('sensor')
            result = sort_state(result, 'sensor', var.get())

        # print(result)
        return result


    def command_ckeckbox_service(self):

        services_data = get_data('config.json', 'Services')


        new_data = [services_data[x][1] for x in services_data]
        # old_data = [services_data[x][1] for x in services_data]
        # print(services_data)
        for x in range(len(self.array_var_services)):
            # print(self.array_entity_services[x]['text'], self.array_var_services[x].get())
            if self.array_entity_services[x]['text'] in new_data:
                # print('in db')
                if self.array_var_services[x].get() == 0:
                    new_data.remove(self.array_entity_services[x]['text'])
                    # print('remove'+self.array_entity_services[x]['text'])
            elif self.array_var_services[x].get() == 1:
                new_data.append(self.array_entity_services[x]['text'])

        # print(new_data)
        # print(services_data)
        for x in services_data:
            if services_data[x][1] not in new_data:
                # print('remove '+services_data[x][1])
                del services_data[x]
                # print(services_data)
                break

        for x in new_data:
            v = [item for item in services_data]
            val = [services_data[item][1] for item in v]
            if x not in val:
                services_data[x.split('.')[1]] = [f'{x.split('.')[0]}/toggle', x]
                # print(services_data)
                break

        write_json("config.json", "Services", services_data)
        create_label_services(get_data('config.json', 'Services'), self.sub_frame_right_frame_services,
                              self.label_list_services, self.frame_list_services, self.button_list_services)

    def command_ckeckbox_state(self):

        services_data = get_data('config.json', 'States')

        new_data = [x[0] for x in services_data]
        # old_data = [services_data[x][1] for x in services_data]
        # print(services_data)

        for x in range(len(self.array_var_states)):
            # print(self.array_entity_states[x]['text'], self.array_var_states[x].get())
            if self.array_entity_states[x]['text'] in new_data:
                # print('in db')
                if self.array_var_states[x].get() == 0:
                    new_data.remove(self.array_entity_states[x]['text'])
                    # print('remove'+self.array_entity_services[x]['text'])
            elif self.array_var_states[x].get() == 1:
                new_data.append(self.array_entity_states[x]['text'])

        # print(new_data)
        # print(services_data)

        for x in range(len(services_data)):
            if services_data[x][0] not in new_data:
                # print('remove '+str(services_data[x]))
                services_data.remove(services_data[x])
                # print(services_data)
                break

        for x in range(len(new_data)):
            val = [item[0] for item in services_data]
            # print(val)
            if new_data[x] not in val:
                unit_resp = get_api(self.ha, f'states/{new_data[x]}', self.header)
                unit = ''
                if 'attributes' in unit_resp:
                    unit_resp=unit_resp['attributes']
                    if 'unit_of_measurement' in unit_resp:
                        unit=unit_resp['unit_of_measurement']

                services_data.append([new_data[x], unit])

        # print(services_data)
        write_json("config.json", "States", services_data)
        create_label_states(get_data('config.json', 'States'), self.sub_frame_right_frame_states,
                            self.label_list_states, self.frame_list_states)



def get_json(entity_type):

    json_data = get_data('config.json', entity_type)

    if entity_type == 'States':
        return  [x[0] for x in json_data]
    elif entity_type == 'Services':
        return [json_data[x][1] for x in json_data]


def create_checkbox(data, frame, json, entity_list, var_list, callback_func):
    for item in entity_list:
        item.destroy()
    entity_list.clear()
    var_list.clear()
    count = 0
    json_data = get_json(json)
    for item in data:
        if item in json_data:
            var = IntVar(value=1)
        else:
            var = IntVar(value=0)
        var_list.append(var)
        checkbox = ttk.Checkbutton(frame, variable=var, text=item, command=callback_func, width=40)
        checkbox.pack()
        entity_list.append(checkbox)
        count += 1
        if count > 18:
            break


def create_label_services(data, frame, label_list, frame_list, button_list):
    for item in label_list:
        item.destroy()
    for item in frame_list:
        item.destroy()
    for item in button_list:
        item.destroy()

    label_list.clear()
    frame_list.clear()
    button_list.clear()

    count = 0
    for item in data:
        f = tk.Frame(frame)
        frame_list.append(f)

        l = tk.Label(f, text=item)
        l.pack(side='left', padx=20)
        label_list.append(l)

        b = tk.Button(f, text='rename', command=lambda i=item, c=count, fl=frame_list, ll=label_list, bb=button_list: update_label(i, c, fl, ll, bb))
        b.pack(side='left', padx=5)
        button_list.append(b)

        f.pack(pady=10)

        count += 1


def update_label(text, count, frame, label, button):


    label[count].pack_forget()
    button[count].pack_forget()

    sv = StringVar(value=text)

    e = tk.Entry(frame[count], textvariable=sv)
    e.pack(side='left')

    b = tk.Button(frame[count], command=lambda: update_name(e, b, sv, label[count], button[count], text, count), text='done')
    b.pack(side='left')


def update_name(entry, button, sv, or_label, or_button, text, count):
    val = sv.get()
    entry.destroy()
    button.destroy()

    # print(val)
    # print(text)

    data = get_data('config.json', 'Services')
    update_json_key(data, count, val)

    or_label['text'] = val
    or_label.pack(side='left')

    or_button.pack(side='left')



def create_label_states(data, frame, label_list, frame_list):
    for item in label_list:
        item.destroy()
    for item in frame_list:
        item.destroy()


    label_list.clear()
    frame_list.clear()


    for item in data:
        f = tk.Frame(frame)
        frame_list.append(f)

        l = tk.Label(f, text=item[0])
        l.pack(side='left', padx=20)
        label_list.append(l)

        f.pack(pady=10)


def update_json_key(dico, key_num, value):
    a = [[key, value] for key, value in dico.items()]
    a[key_num][0] = value

    b = dict(a)
    # print(b)
    write_json('config.json', 'Services', b)


def get_api(url, endpoint, header):
    return loads(get(f'http://{url}:8123/api/{endpoint}', headers=header).text)


def sort_state(json, entity_type, search_word):
    return [entity['entity_id'] for entity in json if search(f'^{entity_type}.+{search_word}', entity['entity_id'])]


if __name__ == '__main__':
    States, Services, HA = get_data('config.json', 'States', 'Services', "InstanceUrl")
    Token = get_data('credentials.json', 'Token')
    Header = get_headers(Token)

    root = tk.Tk()
    root.title('Setup')
    root.geometry('600x500')
    app = App(root, HA, Header)
    root.mainloop()