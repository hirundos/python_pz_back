#!/usr/bin/env python3
"""
Menu Service catalog 앱 인식 테스트
"""

import os
import sys
import django
from pathlib import Path

# Menu Service 경로 설정
menu_service_path = Path("services/menu").resolve()

# Python 경로에 추가
if str(menu_service_path) not in sys.path:
    sys.path.insert(0, str(menu_service_path))

# 작업 디렉토리 변경
os.chdir(menu_service_path)

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'menu_service.settings')

print(f"작업 디렉토리: {os.getcwd()}")
print(f"Python 경로: {sys.path[:3]}")

try:
    django.setup()
    print("✅ Django 설정 로드 성공")

    # catalog 앱 명시적 로드
    from catalog.apps import CatalogConfig
    print(f"✅ CatalogConfig import 성공: {CatalogConfig}")

    # 설치된 앱 확인
    from django.apps import apps
    installed_apps = [app.name for app in apps.get_app_configs()]
    print(f"✅ 설치된 앱 목록: {installed_apps}")

    # catalog 앱 확인
    if 'catalog' in installed_apps:
        print("✅ catalog 앱이 INSTALLED_APPS에 있음")

        # catalog 앱 레지스트리에서 확인
        try:
            catalog_app = apps.get_app_config('catalog')
            print(f"✅ catalog 앱 레지스트리에서 찾음: {catalog_app}")
            print(f"   - name: {catalog_app.name}")
            print(f"   - label: {catalog_app.label}")
        except LookupError as e:
            print(f"❌ catalog 앱을 레지스트리에서 찾을 수 없음: {e}")

        # 모델 import 및 사용 테스트
        try:
            from catalog.models import PizzaType
            print("✅ catalog.models.PizzaType import 성공")

            # 모델 인스턴스 생성 시도
            pizza_type = PizzaType(
                pizza_type_id='TEST001',
                pizza_nm='테스트피자',
                pizza_categ='테스트',
                pizza_img_url='http://example.com/test.jpg'
            )
            print("✅ PizzaType 모델 인스턴스 생성 가능")

        except Exception as e:
            print(f"❌ catalog.models 사용 실패: {e}")
            import traceback
            traceback.print_exc()

    else:
        print("❌ catalog 앱이 INSTALLED_APPS에 없음")

except Exception as e:
    print(f"❌ 테스트 실패: {e}")
    import traceback
    traceback.print_exc()
