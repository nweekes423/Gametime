# app/nba_notifier/wsgi.py
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nba_notifier.settings')
application = get_wsgi_application()

