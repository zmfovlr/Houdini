import subprocess
import os
import hou


def fix_path(old_path, new_sep='/'):
    _path = old_path.replace('\\', '/')
    # _path = old_path.replace('\\\\', '/')
    _path = _path.replace('//', '/')

    if _path.endswith('/'):
        _path = _path[:-1]

    _path = _path.replace('/', new_sep)

    new_path = _path

    return new_path


def error(message, severity=hou.severityType.Error):
    print('{severity}: {message}'.format(severity=severity.name(), message=message))
    hou.ui.displayMessage(message, severity=severity)


def print_report(header, *body):
    print('\n{header:-^50}'.format(header=header))

    for b in body:
        print('\t{0}'.format(b))

    print('-'*50)


def open_explorer(path):
    path = os.path.dirname(path)
    path = fix_path(path, os.path.sep)

    open_path = 'explorer {0}'.format(path)
    subprocess.Popen(open_path, shell=True)
    return