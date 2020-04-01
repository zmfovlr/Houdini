import hou
import os
import re
from utility_scripts import main as util
reload(util)


def clean_name(name):
    new_name = name.lower().strip()
    regex = r'\W+'
    new_name = re.sub(regex, '_', new_name)
    return new_name


def save_scene(kwargs=None, task=None, desc=None):
    if kwargs:
        ctrl = kwargs['ctrlclick']
    else:
        ctrl = False

    # Find scene_data node
    scene_data = None
    scene_data_nodes = []
    for n in hou.node('/obj').children():
        if n.type().nameComponents()[2].startswith('scene_data'):
            scene_data_nodes.append(n)
    if len(scene_data_nodes) > 1:
        util.error('Multiple SCENE DATA nodes found\nAborting Operation')
    elif len(scene_data_nodes) == 1:
        scene_data = scene_data_nodes[0]
    else:
        util.error('SCENE DATA node not found\nPlease create one and select a scene before saving')
        return

    # Gather variables
    save_path = hou.getenv('SAVE_PATH')
    scene = hou.getenv('SCENE')

    if not save_path or not scene:
        util.error('Local variables not defined\nPlease use SCENE DATA node to set these correctly')
        return

    # Set task and desc from curr scene or initialize
    curr_name = hou.hipFile.basename()
    regex = r'^(?P<scene>\w+)-(?P<task>\w+)-(?P<full_ver>v(?P<ver>\d{3,}))(-(?P<desc>\w+))?-(?P<user>\w+)' \
            r'(\.(?P<ext>\w+))$'
    match = re.match(regex, curr_name, flags=re.IGNORECASE)
    if match:
        if not task:
            task = match.group('task')
        if not desc:
            desc = match.group('desc')

    if not task:
        task = ''
    if not desc:
        desc = ''

    ask_input = True
    if ctrl and task != '':
        ask_input = False

    # Input Task and Description
    if ask_input:
        repeat = True
        while repeat:
            repeat = False

            user_input = hou.ui.readMultiInput('Select Task and Description', ('Task', 'Description (optional'),
                                               buttons=('OK', 'Cancel'), initial_contents=(task, desc))
            if user_input[0] == 1:
                return

            task = user_input[1][0]
            desc = user_input[1][1]

            if task == '':
                util.error('Task cannot be left blank', hou.severityType.Warning)
                repeat = True
                continue


    # Set version
    regex = '(?P<scene>{scene})-(?P<task>{task})-v(?P<ver_num>\\d{{3,}})'.format(scene=scene, task=task)
    ver_nums = []
    for f in os.listdir(save_path):
        if not os.path.isdir(f):
            match = re.match(regex, f, flags=re.IGNORECASE)
            if match:
                ver_nums.append(int(match.group('ver_num')))

    if len(ver_nums) > 0:
        high_ver = sorted(ver_nums)[-1]
        ver = 'v{0:>03}'.format(high_ver+1)
    else:
        ver = 'v001'

    # Set User
    user = hou.getenv('USER').lower()

    components = [scene, task, ver, desc, user]
    for i, c in enumerate(components):
        if c and c != '':
            components[i] = clean_name(c)
        else:
            del components[i]

    # Set extension
    lic_dict = {
        'Commercial': 'hip',
        'Indie': 'hiplc',
        'Apprentice': 'hipnc',
        'ApprenticeHD': 'hipnc',
        'Education': 'hipnc'
    }
    lic = hou.licenseCategory().name()
    ext = lic_dict[lic]

    # Build Filename
    name = '-'.join(components)
    filename = '{path}/{name}.{ext}'.format(path=save_path, name=name, ext=ext)

    # Save
    hou.hipFile.save(filename)