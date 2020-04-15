import hou
import os
import re
import json
import shutil
from utility_scripts import main as util
reload(util)



def cache_dir():
    root = hou.getenv('OUTPUT_PATH')
    if not root:
        root = hou.getenv('HIP')
        root = os.path.join(root, 'Output')
    root = util.fix_path(root)

    sub_folders = ['cache']
    path = util.fix_path(os.sep.join(root.split('/') + sub_folders))

    return path


def cache_path(mode='path'):
    node = hou.pwd()

    name = node.evalParm('cache_name')

    if node.evalParm('enable_version'):
        ver = '_v{0:0>3}'.format(node.evalParm('version'))
    else:
        ver = ''


    if node.evalParm('trange') > 0:
        frame = '.{0:0>4}'.format(int(hou.frame()))
    else:
        frame = ''

    ext = node.evalParm('ext')

    full_name = '{name}{ver}{frame}{ext}'.format(name=name, ver=ver, frame=frame, ext=ext)


    path = util.fix_path(os.path.join(node.evalParm('cache_dir'), full_name))

    if mode == 'path':
        return path
    elif mode == 'name':
        return full_name
    else:
        return


def auto_version(node, forced=False):
    if node.evalParm('enable_version') and (node.evalParm('auto_version') or forced):
        cache_dir = node.evalParm('cache_dir')
        if not os.access(cache_dir, os.F_OK):
            node.parm('version').set(1)
            return

        files = os.listdir(cache_dir)

        versions_list = []
        for f in files:
            if not os.path.isdir(os.path.join(cache_dir, f)):
                regex = '(?P<name>{0})_v(?P<ver>\\d+)\\..+'.format(node.evalParm('cache_name'))
                match = re.match(regex, f)
                if match:
                    versions_list.append(int(match.group('ver')))

        if len(versions_list) == 0:
            node.parm('version').set(1)
            return

        else:
            versions_list = list(set(versions_list))
            versions_list.sort()

            latest_version = versions_list[-1]
            if forced:
                node.parm('version').set(latest_version)
            else:
                node.parm('version').set(latest_version+1)

    return


def latest_version(kwargs):
    node = kwargs['node']
    auto_version(node, forced=True)
    node.parm('reload').pressButton()
    return


def watchlist_val_parm(node_num, parm_num):
    node = hou.parm('watch_node_{0}'.format(node_num)).evalAsNode()
    parm_name = hou.evalParm('watch_parm_{0}_{1}'.format(node_num, parm_num))
    watch_parm = node.parm(parm_name)

    if not watch_parm:
        return

    has_keyframe = len(watch_parm.keyframes()) > 0

    try:
        watch_parm.expression()
        is_expr = True
    except hou.OperationFailed:
        is_expr = False

    if has_keyframe and not is_expr:
        return '<< Animated Parameter >>'
    elif has_keyframe and is_expr:
        return '<< Expression >>'
    else:
        return watch_parm.evalAsString()


def watchlist_action(kwargs):
    node = kwargs['node']

    parent_num = kwargs['script_multiparm_index2']
    parent_parm = node.parm('watch_node_{0}'.format(parent_num))
    parent_node = parent_parm.evalAsNode()

    if not parent_node:
        util.error('Invalid node selected')
        return

    parm_list = []
    for p in parent_node.parms():
        template = p.parmTemplate()
        parm_type = template.type()
        if parm_type == hou.parmTemplateType.Folder or parm_type == hou.parmTemplateType.FolderSet:
            continue

        parm_list.append(p)

    tree_list = []
    for p in parm_list:
        hierarchy = list(p.containingFolders())
        hierarchy.append('{0} ({1})'.format(p.parmTemplate().label(), p.name()))
        tree_list.append('/'.join(hierarchy))

    choice = hou.ui.selectFromTree(tree_list, exclusive=True, message='Select a parameter to watch',
                                   title='Watchlist Select', clear_on_cancel=True)
    if len(choice) > 0:
        idx = tree_list.index(choice[0])
        parm = parm_list[idx]

        val_parm = kwargs['parmtuple'][0]
        name_parm = node.parm(val_parm.name()[:-4])
        name_parm.set(parm.name())

    return



def watchlist_write():
    def set_string_attrib(attrib_name, attrib_val):
        if not geo.findGlobalAttrib(attrib_name):
            geo.addAttrib(hou.attribType.Global, attrib_name, '', create_local_variable=False)
        geo.setGlobalAttribValue(attrib_name, attrib_val)


    node = hou.pwd()
    parent = node.parent()
    geo = node.geometry()


    watch_metadata = {}
    num_watch_nodes = parent.evalParm('watchlist_parms')
    for n in range(num_watch_nodes):
        watch_node = parent.parm('watch_node_{0}'.format(n+1)).evalAsNode()

        if not watch_node:
            continue
        watch_node_path = watch_node.path()

        watch_metadata[watch_node_path] = {}

        num_watch_parms = parent.evalParm('watch_parms_{0}'.format(n+1))
        for p in range(num_watch_parms):
            key = parent.evalParm('watch_parm_{0}_{1}'.format(n+1, p+1))

            watch_parm = hou.parm('{0}/{1}'.format(watch_node_path, key))
            if not watch_parm:
                continue

            has_keyframe = len(watch_parm.keyframes()) > 0

            try:
                watch_parm.expression()
                is_expr = True
            except hou.OperationFailed:
                is_expr = False

            if has_keyframe and not is_expr:
                val = ('<< Animated Parameter >>', '<< Animated Parameter >>')
            else:
                val = (watch_parm.eval(), watch_parm.evalAsString())

            watch_metadata[watch_node_path][key] = val

    _watch_metadata = json.dumps(watch_metadata)
    set_string_attrib('watchlist', _watch_metadata)

    return


def watchlist_read(kwargs):
    def lock_parms(val):
        for p in node.parms():
            if p.name().startswith('read_') and p.name().endswith('_val'):
                p.lock(val)


    node = kwargs['node']
    read_node = node.node('READ_METADATA')
    geo = read_node.geometry()

    if not geo or not node.evalParm('load'):
        watchlist_dict = {}
    else:
        try:
            watchlist = geo.attribValue('watchlist')
            watchlist_dict = json.loads(watchlist)
        except hou.OperationFailed:
            watchlist_dict = {}


    lock_parms(False)

    num_keys = len(watchlist_dict.keys())
    node.parm('read_watchlist_parms').set(num_keys)

    for i, (k, v) in enumerate(watchlist_dict.items()):
        node.parm('read_watch_node_{0}'.format(i+1)).set(k)

        num_parm_keys = len(v.keys())
        node.parm('read_watch_parms_{0}'.format(i+1)).set(num_parm_keys)

        for i2, (k2, v2) in enumerate(v.items()):
            node.parm('read_watch_parm_{0}_{1}'.format(i+1, i2+1)).set(k2)
            node.parm('read_watch_parm_{0}_{1}_val'.format(i+1, i2+1)).set(v2[1])

    lock_parms(True)



def save_backup_hip(node):
    def generateReport():

    # file = name of file
    # dir = path to folder
    # path = dir/file

    parent = node.parent()

    backup_dir = hou.getenv('HOUDINI_BACKUP_DIR')
    if not backup_dir:
        hip = hou.getenv('HIP')
        backup_dir = util.fix_path(os.path.join(hip, 'backup'))
        # hou.putenv('HOUDINI_BACKUP_DIR', backup_dir)

    if not os.access(backup_dir, os.F_OK)
        try:
            os.makedirs(backup_dir)
        except:
            # ERROR
            return

    old_files = os.listdir(backup_dir)
    hou.hipFile.save()
    hou.hipFile.saveAsBackup()
    new_files = os.listdir(backup_dir)

    # delta = []
    # for f in new_files:
    #     if f not in old_files:
    #         delta.append(f)

    delta = [f for f in new_files if f not in old_files]

    if len(delta) > 1:
        # ERROR
        return

    new_backup_file = delta[0]
    if not new_backup_file:
        # ERROR
        return

    new_backup_path = util.fix_path(os.path.join(backup_dir, new_backup_file))

    cache_path = node.evalParm('sopoutput')
    _split = os.path.split(cache_path)
    cache_dir = util.fix_path(_split[0])
    cache_file = _split[1]
    cache_name = cache_file.split('.')[0]

    cache_hip_dir = os.path.join(cache_dir, 'cache_hips')

    if not os.access(cache_hip_dir, os.F_OK):
        try:
            os.makedirs(cache_hip_dir)
        except:
            # ERROR
            return

    cache_hip_file = '{name}{ext}'.format(name=cache_name, ext=os.path.splitext(new_backup_file)[-1])
    cache_hip_path = util.fix_path(os.path.join(cache_hip_dir, cache_hip_file))

    try:
        shutil.copy(new_backup_path, cache_hip_path)
    except:
        # ERROR
        return

    # PRINT


def prerender(node):
    auto_version(node.parent())
    save_backup_hip(node)

    return

def preframe(node):
    # print('preframe')
    return

def postframe(node):
    # print('postframe')
    return

def postwrite(node):
    # print('postwrite')
    return

def postrender(node):
    # print('postrender')
    return