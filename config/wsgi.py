import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()

# Vercel이 실행할 'app' 변수를 명시적으로 추가합니다.
app = application
