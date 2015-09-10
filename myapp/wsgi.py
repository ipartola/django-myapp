"""
WSGI config for myapp project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myapp.settings")

os.environ['X_DJANGO_PROJECT_PATH'] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

application = get_wsgi_application()
