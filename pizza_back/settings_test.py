from .settings import *

# 테스트에서는 SQLite 사용
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test_db.sqlite3',
    }
}

# 테스트 시 Email 등 외부 연동 비활성화/간소화 (필요 시 확장 가능)
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
