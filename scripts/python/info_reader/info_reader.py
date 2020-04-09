#-*- coding:utf-8 -*-

import hou
import os
import json
import time
reload(time)
from collections import OrderedDict




# Slate에 작성될 GLOBAL 변수
hip_dir = hou.hscriptExpression("$HIP")
hip_name = hou.hscriptExpression("$HIPNAME")
# username = hou.hscriptExpression("$FXUSER")
username = 'nosung'

# Simulation Log에 대한 json 데이터를 저장할 경로
log_dir = hip_dir + "/simulation_log"


hip_dict = {'hip_dir':hip_dir, 'hip_name':hip_name, 'username':username, 'log_dir':log_dir}

houdini_os = hou.hscriptExpression("$HOUDINI_OS")



def convert_path(path):
    if 'window' in houdini_os.lower():
        repath = path.replace('/', '\\\\')
        # override_path = repath.replace('\\\\', '\\')
    else:
        repath = path

    return repath


def read_info():
    node = hou.pwd()

    today = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    nowtime = time.strftime('%H-%M-%S', time.localtime(time.time()))

    path_list = []
    parm_path_list = hou.pwd().parms()
    for i in list(parm_path_list):
        if 'parm_path' in i.name():
            path = i.rawValue().split('"')[1]
            path = path
            path_list.append(path)

    lv_list = []

    for j in path_list:
        parm = hou.parm(j)
        parm_label = parm.description() + ' (' + parm.name() + ')'
        parm_value = parm.eval()

        lv_list.append([parm_label, str(parm_value)])

    parm_dict = dict(zip(range(len(lv_list)), lv_list))

    for i, v in enumerate(parm_dict.items()):
        parm_dict[i] = dict([parm_dict[i]])

    write_dict = dict(Hip_information=hip_dict, Parameter=parm_dict)


    write_json(write_dict, today, nowtime)
    load_list = load_json(today, nowtime)

    node.parm('title').set(hip_name)
    node.parm('user').set(username)
    node.parm('time').set(today + ' ' + nowtime)

    text = ''

    for l in load_list:
        text = text + str(l)
        node.parm('text').set(text + '\n')


def write_json(dict_data, today, nowtime):
    json_data = OrderedDict()
    json_data = dict_data

    json_save_dir = log_dir + "/json"

    if os.path.isdir(log_dir) == False:
        os.mkdir(log_dir)
    if os.path.isdir(json_save_dir) == False:
        os.mkdir(json_save_dir)

    json_file = json_save_dir + '/' + hip_name + '_' + today + '_' + nowtime + ".json"


    with open(convert_path(json_file), 'w') as make_file:
        json.dump(json_data, make_file, ensure_ascii=False, indent=4)


def load_json(today, nowtime):
    json_save_dir = log_dir + "/json"
    json_file = json_save_dir + '/' + hip_name + '_' + today + '_' + nowtime + ".json"

    out_list = []

    with open(convert_path(json_file)) as load_file:
        json_data = json.load(load_file)
        parm_data = json_data['Parameter']
        parm_data = sorted(parm_data.items())

    for data in parm_data:
        k_encode = data[0].encode('utf-8')
        v = data[1].items()[0]
        v_encode = str(v[0]).encode('utf-8') + ': ' + str(v[1]).encode('utf-8') + '\n'
        convert_json = k_encode + ' ' + v_encode
        out_list.append(convert_json)
        out_list.sort()

    write_list = [i[2:] for i in out_list]

    return write_list
