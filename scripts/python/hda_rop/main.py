import hou
import os
import re
import json
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



def prerender(node):
    auto_version(node.parent())

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