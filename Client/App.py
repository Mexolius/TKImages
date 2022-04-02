import glob
import json
import logging
import os

import dearpygui.dearpygui as dpg

from Logger.CustomLogFormatter import CustomLogFormatter
from RabbitMq.Query import QueryExecutor, QueryBuilder
from RabbitMq.RabbitMQClient import RabbitMQProducer, RabbitMQSyncConsumer

logger = logging.getLogger("App")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomLogFormatter())
logger.addHandler(ch)

# global parameters
initial_width = 1280
initial_height = 720
font_size = 40
scroll_start = []
scroll_add = [0, 0]
component_map = dict()
links = dict()


class Component:
    def __init__(self, label):
        self.label = label
        self.parameters = dict()

    def add_parameters(self, params):
        for label, type in params.items():
            self.parameters[label] = type


def resize_ui(sender, app_data):
    h = dpg.get_viewport_height()

    # render font at higher res and downsample, better then upsampling
    dpg.set_global_font_scale(1 + (h - initial_height) / (4 * initial_height) - 0.5)


def show_popup(sender, app_data):
    if app_data[0] == 1:
        dpg.show_item("popup")
        dpg.set_item_pos("popup", dpg.get_mouse_pos(local=False))


def scroll_click(sender, app_data):
    global scroll_start
    if dpg.is_item_hovered("node_editor"):
        scroll_start = dpg.get_mouse_pos(local=False)


def scroll_end(sender, app_data):
    global scroll_add
    scroll_add[0] += scroll_start[0] - dpg.get_mouse_pos(local=False)[0]
    scroll_add[1] += scroll_start[1] - dpg.get_mouse_pos(local=False)[1]


def delete_nodes(sender, app_data):
    nodes = dpg.get_selected_nodes("node_editor")
    for n in nodes:
        if dpg.get_item_label(n) != "Input":
            dpg.delete_item(n)


def link_callback(sender, app_data):
    # app_data -> (link_id1, link_id2)
    dpg.add_node_link(app_data[0], app_data[1], parent=sender)
    links[app_data[0]] = app_data[1]


def delink_callback(sender, app_data):
    # app_data -> link_id
    dpg.delete_item(app_data)
    links.pop(app_data)


def add_node(sender, app, u):
    pos_x = dpg.get_item_pos("popup")[0] + scroll_add[0]
    pos_y = dpg.get_item_pos("popup")[1] + scroll_add[1]
    with dpg.node(label=u[0], pos=[pos_x, pos_y], parent="node_editor"):
        component = u[1]
        with dpg.node_attribute():

            # handle parameters generation
            for k, v in component.parameters.items():
                if v[0] == "float":
                    dpg.add_input_text(label=k, width=150)
                elif v[0] == "vec2f":
                    dpg.add_input_floatx(label=k, size=2, width=150)
                elif v[0] == "choice":
                    dpg.add_combo(v[1:], label=k, width=150)
                elif v[0] == "color":
                    dpg.add_color_picker(label=k, width=200, height=200)

        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output):
            pass


def parse_components(path):
    with open(path) as jsonfile:
        parsed = json.load(jsonfile)
        for name, params in parsed.items():
            comp = Component(name)
            comp.add_parameters(params)
            component_map[name] = comp


def execute_sequence(query_executor):
    clear_error()
    input = dpg.get_value("root_path")
    if len(input) == 0:
        raise_error("Error: Empty root path")
        return
    files = [log for log in glob.glob(input + "/**", recursive=True) if not os.path.isdir(log)]
    if len(files) == 0:
        raise_error("Error: Cannot find any files in the root path")
        return

    parsed = []
    try:
        next = links["input_param"]
    except KeyError:
        raise_error("Error: No active links to follow")
        return

    while (True):
        data = {}
        children = dpg.get_item_children(next)[1]
        for id in children:
            data[dpg.get_item_label(id)] = dpg.get_value(id)

        value = (QueryBuilder()
                 .query_type(dpg.get_item_label(dpg.get_item_parent(next)))
                 .data(data)
                 .paths(files)
                 .build())
        parsed.append(value)
        try:
            next = links[dpg.get_item_children(dpg.get_item_parent(next))[1][1]]
        except KeyError:
            break

    seq_len = len(parsed)

    def callback(body, query_no):
        logger.info(" [x] Received %r" % body)
        dpg.set_value("progress_bar", query_no / seq_len)

    query_executor.execute(parsed, callback)

    # for p in parsed:
    #     print(p)
    #     p["files"] = files
    #     json_parsed = json.dumps(p)
    #
    #     # here send the json_parsed
    #
    #     # here retreive the json with files
    #     # pthon_json=json.loads(json)
    #     # files=python_json["files"]
    #
    #     # faking execution
    #     time.sleep(1)
    #     success_num += 1

    # debug
    # print(parsed)


# todo
def cancel_execution():
    pass


def raise_error(error):
    dpg.set_value("console", error)
    dpg.configure_item("console", color=(255, 0, 0))


def clear_error():
    dpg.set_value("console", "Error message: 0")
    dpg.configure_item("console", color=(0, 255, 0))


if __name__ == '__main__':
    logger.info("Starting App...")
    dpg.create_context()

    with dpg.font_registry():
        default_font = dpg.add_font("Fonts/Montserrat-Light.otf", font_size, tag="font")

    with dpg.handler_registry():
        dpg.add_mouse_down_handler(callback=show_popup)
        dpg.add_mouse_click_handler(button=2, callback=scroll_click)
        dpg.add_mouse_release_handler(callback=scroll_end, button=2)
        dpg.add_key_press_handler(key=46, callback=delete_nodes)

    rmq_consumer = RabbitMQSyncConsumer('localhost', 5672, 'ImageFinder', 'image_finder.results', 'myuser',
                                        'mypassword')
    rmq_producer = RabbitMQProducer('localhost', 5672, 'myuser', 'mypassword')
    query_executor = QueryExecutor(rmq_producer, rmq_consumer)


    def execution_callback():
        execute_sequence(query_executor)


    parse_components("components.json")
    with dpg.window(tag="main_window"):
        with dpg.group(tag="menu", horizontal=True):
            dpg.add_button(label="Execute", callback=execution_callback)
            dpg.add_button(label="Cancel", callback=cancel_execution)
            dpg.add_progress_bar(tag="progress_bar")
        dpg.add_text(tag="console", default_value="Error message: 0", color=(0, 255, 0))
        dpg.add_text("Ctrl: remove link\nRMB: node list\nDEL: delete selected")
        with dpg.window(tag="popup", popup=True, show=False):
            dpg.add_text("Node list")
            dpg.add_separator()
            for name, params in component_map.items():
                dpg.add_selectable(label=name, user_data=[name, component_map[name]], callback=add_node)

        with dpg.node_editor(callback=link_callback, delink_callback=delink_callback, tag="node_editor",
                             tracked=True) as node_editor:
            with dpg.node(label="Input", tag="input"):
                with dpg.node_attribute(tag="input_param", attribute_type=dpg.mvNode_Attr_Output):
                    dpg.add_input_text(label="root path", width=150, tag="root_path")

    dpg.bind_font(default_font)
    dpg.set_viewport_resize_callback(resize_ui)

    dpg.create_viewport(title='Image Finder', width=initial_width, height=initial_height)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("main_window", True)

    # debug
    # dpg.show_item_registry()

    dpg.start_dearpygui()
    dpg.destroy_context()
