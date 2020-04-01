import hou
import json
import os
import sys
from utility_scripts import main as util

proj_list = 'D:\Job\Study\Rebelway\Python\Week_6\project_list.json'


def read_json():
    try:
        with open(proj_list, 'r') as f:
            data = json.load(f)
    except ValueError:
        data = {}

    return data


def create_folder_and_var(var, path):
    path = util.fix_path(path)
    hou.putenv(var, path)

    if not os.access(path, os.F_OK):
        os.makedirs(path)
        print('Creating variable {0} and folder [{1}]'.format(var, path))

    return


def unset_all_scene_vars():
    variables = [
        'SCENE',
        'SCENE_PATH',
        'SAVE_PATH',
        'OUTPUT_PATH',
        'CACHE_PATH',
        'RENDER_PATH'
    ]
    for v in variables:
        hou.unsetenv(v)
    return


def project_menu(kwargs):
    data = read_json()
    menu = ['-', '-']
    for k in data.keys():
        menu.append(k)
        menu.append(k)

    return menu


def scene_menu(kwargs):
    menu = []
    scenes_path = hou.getenv('SCENES_PATH')
    if scenes_path and os.access(scenes_path, os.F_OK):
        for f in os.listdir(scenes_path):
            if os.path.isdir(util.fix_path(os.path.join(scenes_path, f))):
                menu.append(f)
                menu.append(f)
    return menu


def set_project(kwargs):
    node = kwargs['node']
    project_name = node.evalParm('proj')
    # project_name = kwargs['script_value']

    node.parm('scene').set('')
    unset_all_scene_vars()

    data = read_json()

    if project_name == '-':
        hou.unsetenv('PROJECT')
        hou.unsetenv('CODE')
        hou.unsetenv('PROJ_FPS')
        hou.setFps(24)
        hou.unsetenv('PROJECT_PATH')
        hou.unsetenv('SCENES_PATH')
        hou.unsetenv('HDA_PATH')
        hou.unsetenv('SCRIPTS_PATH')
        node.cook(True)
        return

    try:
        project_data = data[project_name]
    except KeyError:
        util.error('Project Data not found')
        return

    hou.putenv('PROJECT', project_name)

    hou.putenv('CODE', project_data['CODE'])

    fps = project_data['FPS']
    hou.putenv('PROJ_FPS', str(fps))
    hou.setFps(fps)

    project_path = project_data['PATH']
    hou.putenv('PROJECT_PATH', project_data['PATH'])

    create_folder_and_var('SCENES_PATH', util.fix_path(os.path.join(project_path, 'scenes')))

    hda_path = util.fix_path(os.path.join(project_path, 'hda'))
    create_folder_and_var('HDA_PATH', hda_path)

    scripts_path = util.fix_path(os.path.join(project_path, 'scripts'))
    create_folder_and_var('SCRIPTS_PATH', scripts_path)

    hda_paths = [hda_path, ]
    scan_path = hou.getenv('HOUDINI_OTLSCAN_PATH')
    if scan_path:
        hda_paths += scan_path.split(';')
    hda_paths = list(set(hda_paths))
    hou.putenv('HOUDINI_OTLSCAN_PATH', ';'.join(hda_paths))
    hou.hda.reloadAllFiles()

    sys.path.append(scripts_path)

    node.cook(True)


def set_scene(kwargs):
    node = kwargs['node']
    scene_name = node.evalParm('scene')

    # If null scene > unset all
    if scene_name == '':
        unset_all_scene_vars()
        node.cook(True)
        return


    # If no PROJECT_PATH var
    project_path = hou.getenv('PROJECT_PATH')
    if not project_path or not os.access(project_path, os.F_OK):
        util.error('Project path is invalid')
        return

    # If no SCENES_PATH var
    scenes_path = hou.getenv('SCENES_PATH')
    if not scenes_path or not os.access(scenes_path, os.F_OK):
        util.error('Scenes path is invalid')
        return

    # If SCENES_PATH var but no folder
    if not os.access(scenes_path, os.F_OK):
        os.makedirs(scenes_path)

    scene_path = util.fix_path(os.path.join(scenes_path, scene_name))
    if not os.access(scene_path, os.F_OK):
        message = 'Scene folder "{0}" does not exist\n'\
                  'Create this folder now?'.format(scene_name)
        choice = hou.ui.displayMessage(message, severity=hou.severityType.ImportantMessage, buttons=('Yes', 'No'))
        if choice == 0:
            os.makedirs(scene_path)
        else:
            unset_all_scene_vars()
            node.cook(True)
            return

    hou.putenv('SCENE', scene_name)
    hou.putenv('SCENE_PATH', scene_path)

    create_folder_and_var('SAVE_PATH', os.path.join(scene_path, 'working_files'))

    output_path = os.path.join(scene_path, 'output')
    create_folder_and_var('OUTPUT_PATH', output_path)
    create_folder_and_var('CACHE_PATH', os.path.join(output_path, 'cache'))
    create_folder_and_var('RENDER_PATH', os.path.join(output_path, 'render'))

    node.cook(True)


def onLoaded(kwargs):
    node = kwargs['node']
    curr_scene = node.evalParm('scene')
    # print(curr_scene)

    node.parm('proj').pressButton()
    if not curr_scene == '':
        node.parm('scene').set(curr_scene)
        if curr_scene in scene_menu({}):
            node.parm('scene').pressButton()


def onCreated(kwargs):
    node = kwargs['node']

    node.setName('SCENE_DATA')

    # node.setUserData('nodeshape', 'circle')
    node.setColor(hou.Color(0.58, 0.2, 0.48))
    node.setGenericFlag(hou.nodeFlag.Display, False)
    node.setGenericFlag(hou.nodeFlag.Selectable, False)

    node.parm('proj').set(hou.getenv('PROJECT'))
    node.parm('scene').set(hou.getenv('SCENE'))
