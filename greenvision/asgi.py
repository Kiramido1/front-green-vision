"""
ASGI config for Green Vision project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greenvision.settings')

application = get_asgi_application()
