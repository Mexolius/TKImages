import glob
import json
import logging
import os
import threading
from time import sleep

import dearpygui.dearpygui as dpg

from Logger.CustomLogFormatter import CustomLogFormatter
from RabbitMq.Query import HealthRequestMessage
from Utils.QueryUtils import QueryBuilder, QueryExecutor
from RabbitMq.RabbitMQClient import RabbitMQProducer, RabbitMQSyncConsumer, RabbitMQAsyncConsumer

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
links_inv = dict()
link_parent = dict()
results = []

# Health states:
# -1 offline
# 0 pending
# 1 online
health_dict = {
    'size_service': -1,
    'color_service': -1,
    'dog_service': -1,
    'faces_service': -1,
    'similarity_service': -1,
}
online_color = (0, 255, 0)
offline_color = (255, 0, 0)
status_circle_radius = 5
status_separation = 30
status_check_interval = 2

comparator_dict = {">": "greater than", ">=": "greater/equal than", "<": "less than", "<=": "less/equal than",
                   "==": "equal"}
comparator_dict_inv = {v: k for k, v in comparator_dict.items()}


def setup_health_consumer():
    health_consumer = RabbitMQAsyncConsumer.from_config('health_response')

    def health_callback(ch, method, properties, body):
        s_name = json.loads(body)['service_name']
        if s_name in health_dict:
            health_dict[s_name] = 1
        health_consumer.ack(method.delivery_tag)

    health_consumer.consume(health_callback)


def setup_health_sender_thread(interval: float):
    def send_health_beat():
        producer = RabbitMQProducer.from_config()

        while True:
            sleep(interval)
            for k in health_dict.keys():
                producer.publish_rmq_message(HealthRequestMessage(k))
                if health_dict[k] > -1:
                    dpg.configure_item(k, fill=online_color)
                    health_dict[k] -= 1
                else:
                    dpg.configure_item(k, fill=offline_color)

    producer_thread = threading.Thread(target=send_health_beat)
    producer_thread.start()


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
    dpg.set_global_font_scale(
        1 + (h - initial_height) / (4 * initial_height) - 0.5)


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
    id = dpg.add_node_link(app_data[0], app_data[1], parent=sender)
    links[app_data[0]] = app_data[1]
    links_inv[app_data[1]] = app_data[0]
    link_parent[id] = (app_data[0], app_data[1])


def delink_callback(sender, app_data):
    # app_data -> link_id
    links.pop(link_parent[app_data][0])
    links_inv.pop(link_parent[app_data][1])
    link_parent.pop(app_data)
    dpg.delete_item(app_data)


def choice_propagate(sender, app, u):
    component_dict = u[1][1].parameters
    children = dpg.get_item_children(dpg.get_item_children(u[0])[1][0])[1]
    for group in children:
        field = dpg.get_item_children(group)[1]
        text = dpg.get_item_label(field[0])
        v = component_dict[text]
        if v[0] == "choice_propagate" and group > sender:
            break
        if v[0] == "choice_propagate" or (len(v) > 1 and v[1] == "shared") or group < sender:
            continue
        elif (v[1] not in app):
            dpg.hide_item(group)
        else:
            dpg.show_item(group)


def file_selector_callback(s, a, u):
    dpg.set_value(u, list(a["selections"].items())[0][1])


def add_node(sender, app, u):
    pos_x = dpg.get_item_pos("popup")[0] + scroll_add[0]
    pos_y = dpg.get_item_pos("popup")[1] + scroll_add[1]
    with dpg.node(label=u[0], pos=[pos_x, pos_y], parent="node_editor") as node_id:
        component = u[1]
        with dpg.node_attribute():

            # handle parameters generation
            capture = ""
            for k, v in component.parameters.items():
                v_filtered = v
                show_input = True
                if capture != "" and v[0] != "choice_propagate":
                    clause = v[1]
                    v_filtered = v[:1] + v[2:]
                    if clause not in capture and clause != "shared":
                        show_input = False
                if v_filtered[0] == "choice_propagate":
                    with dpg.group(xoffset=120, horizontal=True):
                        dpg.add_text(k, label=k)
                        if k == "comparator":
                            vi = []
                            for id, i in enumerate(v_filtered[1:]):
                                vi.append(comparator_dict[i])
                            dpg.add_combo(vi, width=150, default_value=vi[0], user_data=[node_id, u],
                                          callback=choice_propagate)
                        else:
                            dpg.add_combo(v_filtered[1:], width=150, default_value=v_filtered[2],
                                          user_data=[node_id, u],
                                          callback=choice_propagate)
                        capture = v_filtered[2]
                elif v_filtered[0] == "optional_float":
                    with dpg.group(xoffset=120, horizontal=True, show=show_input):
                        dpg.add_text(k, label=k)
                        dpg.add_input_text(width=150, default_value="")
                elif v_filtered[0] == "float":
                    with dpg.group(xoffset=120, horizontal=True, show=show_input):
                        dpg.add_text(k, label=k)
                        dpg.add_input_text(
                            width=150, default_value="0", no_spaces=True, decimal=True)

                elif v_filtered[0] == "int":
                    with dpg.group(xoffset=120, horizontal=True, show=show_input):
                        dpg.add_text(k, label=k)
                        dpg.add_input_text(
                            width=150, default_value="", no_spaces=True, decimal=True)

                elif v_filtered[0] == "string":
                    with dpg.group(xoffset=120, horizontal=True, show=show_input):
                        dpg.add_text(k, label=k)
                        dpg.add_input_text(width=150, default_value="")

                elif v_filtered[0] == "vec2f":
                    with dpg.group(xoffset=120, horizontal=True, show=show_input):
                        dpg.add_text(k, label=k)
                        dpg.add_input_floatx(
                            size=2, width=150, default_value=(0, 0))

                elif v_filtered[0] == "choice":
                    with dpg.group(xoffset=120, horizontal=True, show=show_input):
                        dpg.add_text(k, label=k)
                        if k == "comparator":
                            vi = []
                            for id, i in enumerate(v_filtered[1:]):
                                vi.append(comparator_dict[i])
                            dpg.add_combo(vi, width=150, default_value=vi[0])
                        else:
                            dpg.add_combo(
                                v_filtered[1:], width=150, default_value=v_filtered[1])

                elif v_filtered[0] == "color":
                    with dpg.group(show=show_input):
                        dpg.add_text(k, label=k)
                        dpg.add_color_picker(width=200, height=200)

                elif v_filtered[0] == "file_selector":
                    with dpg.group(xoffset=120, horizontal=True, show=show_input):
                        dpg.add_text(k, label=k)
                        id_path = dpg.add_input_text(width=150)

                        with dpg.file_dialog(label="File Dialog", width=400, height=500, show=False, user_data=id_path,
                                             callback=file_selector_callback):
                            dpg.add_file_extension(
                                ".*", color=(255, 255, 255, 255))
                        dpg.add_button(label="File Selector", user_data=dpg.last_container(),
                                       callback=lambda s, a, u: dpg.configure_item(u, show=True), indent=280)

        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output):
            pass
    return node_id


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
    files = [log for log in glob.glob(
        input + "/**", recursive=True) if not os.path.isdir(log)]
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
            id = dpg.get_item_children(id)
            id0 = id[1][0]
            id = id[1][1]

            if dpg.get_item_label(id0) == "comparator":
                data[dpg.get_item_label(
                    id0)] = comparator_dict_inv[dpg.get_value(id)]
            else:
                data[dpg.get_item_label(id0)] = dpg.get_value(id)

        value = (QueryBuilder()
                 .query_type(dpg.get_item_label(dpg.get_item_parent(next)))
                 .data(data)
                 .paths(files)
                 .build())
        parsed.append(value)
        try:
            next = links[dpg.get_item_children(
                dpg.get_item_parent(next))[1][1]]
        except KeyError:
            break

    seq_len = len(parsed)

    def callback(body, query_no):
        logger.info(" [x] Received %r" % body)
        dpg.set_value("progress_bar", query_no / seq_len)

        dpg.delete_item("results", children_only=True)
        dpg.delete_item("texture_container", children_only=True)
        body_py = json.loads(body)
        for item in body_py["paths"]:
            try:
                width, height, channels, data = dpg.load_image(item)
                id = dpg.add_static_texture(
                    width, height, data, parent="texture_container")
                dpg.add_image(width=100 * (width / height),
                              height=100, texture_tag=id, parent="results")
            except TypeError:
                continue

    dpg.set_value("progress_bar", 0)
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


def draw_status(pos, tag):
    dpg.draw_circle((10, pos), status_circle_radius,
                    thickness=1, fill=offline_color, tag=tag)


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
    setup_health_consumer()
    setup_health_sender_thread(status_check_interval)
    dpg.create_context()

    dpg.add_texture_registry(label="texture_container",
                             tag="texture_container")
    with dpg.font_registry():
        default_font = dpg.add_font(
            "Fonts/Montserrat-Light.otf", font_size, tag="font")

    with dpg.handler_registry():
        dpg.add_mouse_down_handler(callback=show_popup)
        dpg.add_mouse_click_handler(button=2, callback=scroll_click)
        dpg.add_mouse_release_handler(callback=scroll_end, button=2)
        dpg.add_key_press_handler(key=46, callback=delete_nodes)

    rmq_consumer = RabbitMQSyncConsumer.from_config('results')
    rmq_producer = RabbitMQProducer.from_config()
    query_executor = QueryExecutor(rmq_producer, rmq_consumer)

    def execution_callback():
        execute_sequence(query_executor)

    parse_components("components.json")
    with dpg.window(tag="main_window"):
        with dpg.group(tag="menu", horizontal=True):
            dpg.add_button(label="Execute", callback=execution_callback)
            dpg.add_button(label="Cancel", callback=cancel_execution)
            dpg.add_progress_bar(tag="progress_bar")
        dpg.add_text(
            tag="console", default_value="Error message: 0", color=(0, 255, 0))
        dpg.add_text("Ctrl: remove link\nRMB: node list\nDEL: delete selected")
        with dpg.collapsing_header(label="Results"):
            with dpg.child_window(height=150, horizontal_scrollbar=True):
                with dpg.group(tag="results", horizontal=True):
                    pass

        with dpg.collapsing_header(label="Status"):
            with dpg.group(horizontal=True):
                with dpg.group():
                    for k in health_dict.keys():
                        dpg.add_text(k)
                with dpg.drawlist(width=200, height=160):
                    for i, k in enumerate(health_dict.keys()):
                        draw_status(status_separation/2 +
                                    i * status_separation, k)

        with dpg.window(tag="popup", popup=True, show=False):
            dpg.add_text("Node list")
            dpg.add_separator()
            for name, params in component_map.items():
                dpg.add_selectable(label=name, user_data=[
                                   name, component_map[name]], callback=add_node)

        with dpg.node_editor(callback=link_callback, delink_callback=delink_callback, tag="node_editor",
                             tracked=True) as node_editor:
            with dpg.node(label="Input", tag="input"):
                with dpg.node_attribute(tag="input_param", attribute_type=dpg.mvNode_Attr_Output):
                    dpg.add_input_text(label="root path",
                                       width=150, tag="root_path")

    dpg.bind_font(default_font)
    dpg.set_viewport_resize_callback(resize_ui)

    dpg.create_viewport(title='Image Finder',
                        width=initial_width, height=initial_height)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("main_window", True)

    # debug
    # dpg.show_item_registry()

    dpg.start_dearpygui()
    dpg.destroy_context()
