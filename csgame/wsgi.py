"""
WSGI config for csgame project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os
import sys, glob
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, glob.glob(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'venv/lib/python*/site-packages'))[-1])

from django.core.wsgi import get_wsgi_application

os.environ["DJANGO_SETTINGS_MODULE"] = "csgame.settings"

application = get_wsgi_application()
