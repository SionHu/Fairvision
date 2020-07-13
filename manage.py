#!/usr/bin/env python3
import ntpath
import os
import sys

def tryActivate(venv_folder):
    '''
    Attempt to activate a virtual environment from within Python
    '''
    try:
        activate_this_path = os.path.join(venv_folder, 'Scripts', 'activate_this.py') if os.path is ntpath else os.path.join(venv_folder, 'bin', 'activate_this.py')
        if os.path.exists(activate_this_path):
            with open(activate_this_path) as f:
                exec(f.read(), {'__file__': activate_this_path})
            return True
    except:
        pass
    return False

# activate the virtual environment if found
path = os.path.dirname(os.path.abspath(__file__))
try:
    import django
except ImportError:
    if not tryActivate('venv') and tryActivate('mycs'):
        print("Unable to find a virtual environment.")
    try:
        import django
    except ImportError:
        print("Unable to activate virtual environment. Perhaps you are using the wrong version of Python.")

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "csgame.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise
    execute_from_command_line(sys.argv)
