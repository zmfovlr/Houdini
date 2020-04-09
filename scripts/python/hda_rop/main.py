import hou
import os
import re
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



def prerender(node):
    # print('prerender')
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