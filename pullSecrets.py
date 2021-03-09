#!/usr/bin/env python3
"""
Script to download the secret repository for Crowdsourcing into the virtual
environment. This script is only for members of CAM2 to make setting up the
repository easy.
"""

import ntpath
import os
import shutil
import subprocess
from distutils.util import strtobool

activate_this = '''
#### FROM virtualenv PROJECT ###

"""By using execfile(this_file, dict(__file__=this_file)) you will
activate this virtualenv environment.

This can be used when you must use an existing Python interpreter, not
the virtualenv bin/python
"""

try:
    __file__
except NameError:
    raise AssertionError(
        "You must run this like execfile('path/to/activate_this.py', dict(__file__='path/to/activate_this.py'))")
import sys
import os

old_os_path = os.environ.get('PATH', '')
os.environ['PATH'] = os.path.dirname(os.path.abspath(__file__)) + os.pathsep + old_os_path
base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if sys.platform == 'win32':
    site_packages = os.path.join(base, 'Lib', 'site-packages')
else:
    site_packages = os.path.join(base, 'lib', 'python%s' % sys.version[:3], 'site-packages')
prev_sys_path = list(sys.path)
import site
site.addsitedir(site_packages)
sys.real_prefix = sys.prefix
sys.prefix = base
# Move the added items to the front of the path:
new_sys_path = []
for item in list(sys.path):
    if item not in prev_sys_path:
        new_sys_path.append(item)
        sys.path.remove(item)
sys.path[:0] = new_sys_path
'''

FOLDER = 'venv'

def updateVenv(venv_folder, make=True):
    import venv
    activate_this_path = os.path.join(venv_folder, 'Scripts', 'activate_this.py') if os.path is ntpath else os.path.join(venv_folder, 'bin', 'activate_this.py')
    python_path = os.path.join(venv_folder, 'Scripts', 'python3.exe') if os.path is ntpath else os.path.join(venv_folder, 'bin', 'python3')
    if make:
        venv.create(venv_folder, with_pip=True, prompt="fairvision.app")
    if not os.path.exists(activate_this_path):
        with open(activate_this_path, 'w') as f:
            f.write(activate_this)
        os.chmod(activate_this_path, 0o777)
    exec(activate_this, {'__file__': activate_this_path})
    subprocess.run([python_path, '-m', 'pip', 'install', '-r', 'requirements.txt']).check_returncode()

def chooseNewFolder():
    global FOLDER
    FOLDER = None
    while FOLDER is None or not os.path.exists(FOLDER):
        FOLDER = input("Where is your virtual environment: ")
        if not os.path.exists(FOLDER) or not os.path.isdir(FOLDER):
            if strtobool(input(f"{FOLDER} doesn't exist. Do you want to make a virtual environment here: ")):
                updateVenv('venv')
            else:
                FOLDER = None
    with open('.venv', 'w') as venvFile:
        venvFile.write(FOLDER)

if __name__ == '__main__':
    cwd = os.getcwd()
    try:
        path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(path)

        # Shim for Xiao
        if os.path.exists('.venv'):
            with open('.venv') as venvFile:
                FOLDER = venvFile.read().strip()
            if not os.path.exists(FOLDER) or not os.path.isdir(FOLDER):
                print(f"{FOLDER} doesn't exist. Choose a different folder.")
                chooseNewFolder()
        elif not os.path.exists('venv'):
            if os.path.exists('mycs'):
                FOLDER = 'mycs'
                pass # updateVenv('mycs', False)
            else:
                chooseNewFolder()
        else:
            pass # updateVenv('venv', False)

        if os.path.exists(os.path.join(FOLDER, 'secrets')):
            # git pull
            try:
                os.chdir(os.path.join(FOLDER, 'secrets'))
                subprocess.run(['git', 'pull']).check_returncode()
            finally:
                os.chdir(path)
            if not os.path.islink('.env'):
                shutil.copyfile(os.path.join(FOLDER, 'secrets/.env'), '.env')
        else:
            # git clone
            try:
                os.chdir(FOLDER)
                subprocess.run(['git', 'clone', 'https://github.com/PurdueCAM2Project/Fairvision-secrets', 'secrets']).check_returncode()
            finally:
                os.chdir(path)
            try:
                os.symlink(os.path.join(FOLDER, 'secrets/.env'), '.env')
            except:
                shutil.copyfile(os.path.join(FOLDER, 'secrets/.env'), '.env')

    finally:
        os.chdir(cwd)
