# config/wsgi.py
import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django_app = get_wsgi_application()

# ★ WhiteNoise로 직접 래핑 (서버리스에서도 확실히 정적 서빙)
application = WhiteNoise(django_app, root=str(settings.STATIC_ROOT))
# /static/ 경로에 정적 파일을 명시적으로 매핑
application.add_files(str(settings.STATIC_ROOT), prefix='static/')

# Vercel 진입점
app = application
