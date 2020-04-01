import hou
import os
import json
from utility_scripts import main as util
reload(util)

proj_list = 'D:\Job\Study\Rebelway\Python\Week_6\project_list.json'

def read_json():
    try:
        with open(proj_list, 'r') as f:
            data = json.load(f)
    except ValueError:
        data = {}

    return data


# def fix_path(old_path, new_sep='/'):
#     _path = old_path.replace('\\', '/')
#     _path = old_path.replace('\\\\', '/')
#     _path = _path.replace('//', '/')
#
#     if _path.endswith('/'):
#         _path = _path[:-1]
#
#     _path = _path.replace('/', new_sep)
#
#     new_path = _path
#     return new_path
#
#
# def error(message, severity=hou.severityType.Error):
#     print('{severity}: {message}'.format(severity=severity.name(), message=message))
#     hou.ui.displayMessage(message, severity=severity)
#
#
# def print_report(header, *body):
#     print('\n{header:-^50}'.format(header=header))
#
#     for b in body:
#         print('\t{0}'.format(b))
#
#     print('-'*50)


def manage_proj():
    sel = hou.ui.displayMessage('Select an action', buttons=('Add', 'Remove', 'Details', 'Cancel'))
    if sel == 0:
        add_proj()
    elif sel == 1:
        remove_proj()
    elif sel == 2:
        details_proj()
    else:
        return


def add_proj():
    data = read_json()
    # Init
    _proj_name = None
    path = None
    path_name = None
    path_code = None
    path_fps = None
    # Select Proejct Path
    repeat = True
    while repeat:
        repeat = False
        _path = hou.ui.selectFile(title='Select Project Directory', file_type=hou.fileType.Directory)
        path = os.path.dirname(_path)

        if path == '':
            return

        for k, v in data.items():
            if util.fix_path(path) == util.fix_path(v['PATH']):
                util.error('Project path is already used by another project {0}\nPlease select a different path'.format(k))
                repeat = True
                break
        if repeat:
            continue


        _proj_name = os.path.split(path)[-1]


    # Select Project Name, Code and FPS
    repeat = True
    while repeat:
        repeat = False
        inputs = hou.ui.readMultiInput(message='Enter Project Data', input_labels=('Project Name', 'Project Code', 'FPS'),
                                       buttons=('OK', 'Cancel'), initial_contents=(_proj_name, '', '24'))

        if inputs[0] == 1:
            return

        proj_name = inputs[1][0]
        proj_code = inputs[1][1]
        proj_fps = inputs[1][2]

        if proj_name == '' or proj_code == '' or proj_fps == '':
            util.error('Please fill in all fields')
            repeat = True
            continue

        try:
            proj_fps = int(proj_fps)
        except ValueError:
            util.error('FPS not set to a number. \n Please enter a whole number')
            repeat = True
            continue

        for k, v in data.items():
            if proj_name == k:
                util.error('Project name is already in use\nPlease select a different name')
                repeat = True
                break

            if proj_code == v['CODE']:
                util.error('Project code is already in use\nPlease select a different code')
                repeat = True
                break

        if repeat:
            continue





    if proj_name and proj_code and proj_fps:
        proj_data = {
            'CODE' : proj_code,
            'PATH' : path,
            'FPS' : proj_fps
        }
        data[proj_name] = proj_data

    if data:
        with open(proj_list, 'w') as f:
            json.dump(data, f, sort_keys=True, indent=4)


def remove_proj():
    data = read_json()
    projects = data.keys()
    sel = hou.ui.selectFromList(projects, message='Select Project to Remove', title='Remove Project',
                          column_header='Projects', clear_on_cancel=True)
    if len(sel) == 0:
        return

    for i in sel:
        key = projects[i]
        del data[key]

    with open(proj_list, 'w') as f:
        json.dump(data, f, sort_keys=True, indent=4)


def details_proj():
    data = read_json()
    projects = data.keys()
    sel = hou.ui.selectFromList(projects, exclusive=True, message='Select Project to view details',
                                title='Project Details', column_header='Projects', clear_on_cancel=True)
    if len(sel) == 0:
        return

    proj = projects[sel[0]]
    proj_data = data[proj]

    util.print_report('Project Details',
                 'Name: {0}'.format(proj),
                 'Code: {0}'.format(proj_data['CODE']),
                 'Path: {0}'.format(proj_data['PATH']),
                 'FPS: {0}'.format(proj_data['FPS'])
                 )
