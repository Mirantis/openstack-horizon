import logging
import os
import sys

if (os.path.exists(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../.venv'))):
    activate_this = os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../.venv/'), "bin/activate_this.py")
    execfile(activate_this, dict(__file__=activate_this))


from django.conf import settings
import django.core.handlers.wsgi
# Add this file path to sys.path in order to import settings
sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'openstack_dashboard.settings'
sys.stdout = sys.stderr

DEBUG = False

application = django.core.handlers.wsgi.WSGIHandler()

