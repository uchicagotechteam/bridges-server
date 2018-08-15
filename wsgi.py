#!/usr/bin/python
"""
WSGI config for bridges server
"""
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'bridges_server.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
