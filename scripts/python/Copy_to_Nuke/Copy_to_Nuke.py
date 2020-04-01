# -*- coding:utf-8 -*-

import sys
sys.path.append("/core/inhouse/rez/packages/python_library/2.7/python/site-packages")

import pyperclip
import os
import hou


nodes = hou.selectedNodes()

cam_path_list = []
out_path_list = []
start_f_list = []
end_f_list = []
resx_list = []
resy_list = []
name_list = []



for node in nodes:
    cam_path_list.append(node.parm('camera').eval())
    start_f_list.append(node.parm('f1').eval())
    end_f_list.append(node.parm('f2').eval())
    name_list.append(node.name())

    if node.parm('override_camerares').eval() == 0:
        resx_list.append(hou.parm(node.parm('camera').eval() + '/resx').eval())
        resy_list.append(hou.parm(node.parm('camera').eval() + '/resy').eval())
    else:
        res_mult = node.parm('res_fraction').eval()
        resx = hou.parm(node.parm('camera').eval() + '/resx').eval()
        resy = hou.parm(node.parm('camera').eval() + '/resy').eval()

        resx_list.append(int(round(float(resx) * float(res_mult))))
        resy_list.append(int(round(float(resy) * float(res_mult))))


    node_name = node.type().name()

    if 'Arnold' in node_name:
        out_path_split = node.parm('ar_picture').eval().split('.')
    elif 'Mantra' in node_name:
        out_path_split = node.parm('vm_picture').eval().split('.')
    else:
        pass

    out_path_split[-2] = '####'

    new_path = '.'.join(out_path_split)
    out_path_list.append(new_path)




def write_script(path, resx, resy, start_f, end_f, name, xpos, ypos):
    head = 'set cut_paste_input [stack 0]\nversion 12.0 v3\n'
    read_head = 'Read {\n inputs 0\n'
    file_type = ' file_type exr\n'
    file_path = ' file {}\n'.format(path)
    img_format = ' format "{0} {1}"\n'.format(resx, resy)
    first = ' first ' + str(int(start_f)) + '\n'
    last = ' last ' + str(int(end_f)) + '\n'
    origfirst = ' origfirst ' + str(int(start_f)) + '\n'
    origlast = ' origlast ' + str(int(end_f)) + '\n'
    origset = ' origset true\n'
    version = ' version 0\n'
    name = ' name {}\n'.format(name)
    selected = ' selected true\n'
    xpos = ' xpos {}\n'.format(xpos)
    ypos = ' ypos {}\n'.format(ypos)
    end = '}'

    read_list = [
        head,
        read_head,
        file_type,
        file_path,
        img_format,
        first,
        last,
        origfirst,
        origlast,
        version,
        name,
        selected,
        xpos,
        ypos,
        end
    ]

    read_script = ''

    for j in read_list:
        read_script += j

    return read_script





result = ''

for i, (out, resx, resy, start_f, end_f) in enumerate(zip(out_path_list, resx_list, resy_list, start_f_list, end_f_list)):
    result += write_script(out_path_list[i], resx_list[i], resy_list[i], start_f_list[i], end_f_list[i], name_list[i], i*100, 0) + '\n'



pyperclip.copy(result)