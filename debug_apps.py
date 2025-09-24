#!/usr/bin/env python3
"""
Django 앱 디버깅 스크립트

각 서비스의 Django 앱이 올바르게 인식되는지 확인합니다.
"""

import os
import sys
import django
from pathlib import Path


def debug_service_apps(service_name, service_path):
    """서비스의 Django 앱 디버깅"""
    print(f"\n🔍 {service_name} 디버깅 시작")
    print(f"서비스 경로: {service_path}")

    try:
        # 절대 경로로 변환
        abs_service_path = Path(service_path).resolve()

        # Python 경로에 서비스 디렉토리 추가
        if str(abs_service_path) not in sys.path:
            sys.path.insert(0, str(abs_service_path))

        # Django 설정 모듈 결정
        settings_module = f"{abs_service_path.name}_service.settings"
        print(f"Settings 모듈: {settings_module}")

        # Django 설정
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

        # 현재 작업 디렉토리 변경
        original_cwd = os.getcwd()
        os.chdir(abs_service_path)

        django.setup()

        # 설치된 앱 확인
        from django.apps import apps
        installed_apps = [app.name for app in apps.get_app_configs()]
        print(f"✅ 설치된 앱 목록: {installed_apps}")

        # Django 앱 레지스트리에서 catalog 앱 직접 확인
        if service_name == "Menu Service":
            try:
                catalog_app = apps.get_app_config('catalog')
                print(f"✅ catalog 앱 레지스트리에서 찾음: {catalog_app}")
                print(f"   - name: {catalog_app.name}")
                print(f"   - label: {catalog_app.label}")
            except LookupError as e:
                print(f"❌ catalog 앱을 레지스트리에서 찾을 수 없음: {e}")

            try:
                from catalog.models import PizzaType
                print("✅ catalog.models.PizzaType import 성공")
                # 모델 인스턴스 생성 시도
                pizza_type = PizzaType(pizza_type_id='TEST', pizza_nm='테스트', pizza_categ='테스트', pizza_img_url='test.jpg')
                print("✅ PizzaType 모델 인스턴스 생성 가능")
            except Exception as e:
                print(f"❌ catalog.models 사용 실패: {e}")

        elif service_name == "Order Service":
            try:
                orders_app = apps.get_app_config('orders')
                print(f"✅ orders 앱 레지스트리에서 찾음: {orders_app}")
                print(f"   - name: {orders_app.name}")
                print(f"   - label: {orders_app.label}")
            except LookupError as e:
                print(f"❌ orders 앱을 레지스트리에서 찾을 수 없음: {e}")

            try:
                from orders.models import Branch
                print("✅ orders.models.Branch import 성공")
                # 모델 인스턴스 생성 시도
                branch = Branch(bran_id='TEST', bran_nm='테스트지점')
                print("✅ Branch 모델 인스턴스 생성 가능")
            except Exception as e:
                print(f"❌ orders.models 사용 실패: {e}")

        print(f"✅ {service_name} 디버깅 완료")

    except Exception as e:
        print(f"❌ {service_name} 디버깅 실패: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 원래 작업 디렉토리로 복원
        os.chdir(original_cwd)


def main():
    """메인 디버깅 함수"""
    print("🚀 Django 앱 디버깅 시작")
    print("=" * 50)

    debug_service_apps("Login Service", "services/login")
    debug_service_apps("Menu Service", "services/menu")
    debug_service_apps("Order Service", "services/order")

    print("\n" + "=" * 50)
    print("📊 디버깅 완료")


if __name__ == "__main__":
    main()
