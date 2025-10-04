"""
WSGI config for Green Vision project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greenvision.settings')

application = get_wsgi_application()
