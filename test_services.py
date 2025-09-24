#!/usr/bin/env python3
"""
MSA Pizza Backend 서비스 테스트 스크립트

각 서비스의 핵심 기능을 독립적으로 테스트합니다.
"""

import os
import sys
import django
import requests
import json
from pathlib import Path
import subprocess


def test_service_in_directory(service_name, service_path):
    """지정된 디렉토리에서 서비스 테스트"""
    print(f"🔧 {service_name} 테스트 시작...")

    # 현재 작업 디렉토리 저장
    original_cwd = os.getcwd()

    try:
        # 절대 경로로 변환
        abs_service_path = Path(service_path).resolve()
        service_dir_name = abs_service_path.name  # 'login', 'menu', 'order'

        print(f"📁 작업 디렉토리: {abs_service_path}")

        # Django 설정 모듈 결정
        settings_module = f"{service_dir_name}_service.settings"

        # Python 경로에 서비스 디렉토리 추가 (절대 경로 사용)
        if str(abs_service_path) not in sys.path:
            sys.path.insert(0, str(abs_service_path))

        # 서비스 디렉토리로 이동
        os.chdir(abs_service_path)

        # Django 설정
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

        django.setup()

        if service_name == "Login Service":
            return test_login_models()
        elif service_name == "Menu Service":
            return test_menu_models()
        elif service_name == "Order Service":
            return test_order_models()
        else:
            print(f"❌ 알 수 없는 서비스: {service_name}")
            return False

    except Exception as e:
        print(f"❌ {service_name} 테스트 실패: {e}")
        return False

    finally:
        # 원래 작업 디렉토리로 복원
        os.chdir(original_cwd)


def test_login_models():
    """Login Service 모델 테스트"""
    try:
        from authapp.models import Member
        from django.contrib.auth.hashers import make_password, check_password

        # 기존 데이터 확인 및 정리
        Member.objects.filter(member_id='test_user').delete()

        # 모델 테스트
        member = Member.objects.create(
            member_id='test_user',
            member_pwd=make_password('test_password123'),
            member_nm='테스트사용자'
        )
        print("✅ Member 모델 생성 성공")

        # 비밀번호 검증 테스트
        if check_password('test_password123', member.member_pwd):
            print("✅ 비밀번호 검증 성공")
        else:
            print("❌ 비밀번호 검증 실패")
            return False

        print("✅ Login Service 테스트 통과")
        return True

    except Exception as e:
        print(f"❌ Login Service 모델 테스트 실패: {e}")
        return False


def test_menu_models():
    """Menu Service 모델 테스트"""
    try:
        from catalog.models import PizzaType, Pizza

        # 기존 데이터 확인 및 정리
        Pizza.objects.filter(pizza_id='PIZZA_TEST_L').delete()
        PizzaType.objects.filter(pizza_type_id='PT_TEST').delete()

        # 모델 테스트
        pizza_type = PizzaType.objects.create(
            pizza_type_id='PT_TEST',
            pizza_nm='테스트피자',
            pizza_categ='테스트',
            pizza_img_url='http://example.com/test.jpg'
        )
        print("✅ PizzaType 모델 생성 성공")

        pizza = Pizza.objects.create(
            pizza_id='PIZZA_TEST_L',
            pizza_type=pizza_type,
            size='L',
            price=25000.00
        )
        print("✅ Pizza 모델 생성 성공")

        print("✅ Menu Service 테스트 통과")
        return True

    except Exception as e:
        print(f"❌ Menu Service 모델 테스트 실패: {e}")
        return False


def test_order_models():
    """Order Service 모델 테스트"""
    try:
        from orders.models import Branch, Order, OrderDetail

        # 기존 데이터 확인 및 정리
        OrderDetail.objects.filter(order_detail_id=999).delete()
        Order.objects.filter(order_id='ORDER_TEST_999').delete()
        Branch.objects.filter(bran_id='BRANCH_TEST').delete()

        # 모델 테스트
        branch = Branch.objects.create(
            bran_id='BRANCH_TEST',
            bran_nm='테스트지점'
        )
        print("✅ Branch 모델 생성 성공")

        order = Order.objects.create(
            order_id='ORDER_TEST_999',
            member_id='test_user',
            bran=branch,
            date='2024-01-15',
            time='14:30:00'
        )
        print("✅ Order 모델 생성 성공")

        order_detail = OrderDetail.objects.create(
            order_detail_id=999,
            order=order,
            pizza_id='PIZZA_TEST_001',
            quantity=2
        )
        print("✅ OrderDetail 모델 생성 성공")

        print("✅ Order Service 테스트 통과")
        return True

    except Exception as e:
        print(f"❌ Order Service 모델 테스트 실패: {e}")
        return False


def test_api_endpoints():
    """API 엔드포인트 테스트"""
    print("🌐 API 엔드포인트 테스트 시작...")

    # 각 서비스의 서버를 백그라운드에서 시작
    processes = []

    try:
        # Login Service 시작
        login_proc = subprocess.Popen([
            sys.executable, "manage.py", "runserver", "8001", "--noreload"
        ], cwd="services/login", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        processes.append(("Login", login_proc, 8001))

        # Menu Service 시작
        menu_proc = subprocess.Popen([
            sys.executable, "manage.py", "runserver", "8002", "--noreload"
        ], cwd="services/menu", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        processes.append(("Menu", menu_proc, 8002))

        # Order Service 시작
        order_proc = subprocess.Popen([
            sys.executable, "manage.py", "runserver", "8003", "--noreload"
        ], cwd="services/order", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        processes.append(("Order", order_proc, 8003))

        print("⏳ 서비스 시작 대기 중...")
        import time
        time.sleep(8)  # 서비스 시작 대기

        # API 테스트
        results = []

        # Login Service API 테스트
        try:
            response = requests.post('http://localhost:8001/login/register/', json={
                'member_id': 'api_test_user',
                'password': 'test123',
                'member_nm': 'API테스트사용자'
            })
            if response.status_code == 201:
                print("✅ Login Service 회원가입 API 성공")
                results.append(True)
            else:
                print(f"❌ Login Service 회원가입 API 실패: {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"❌ Login Service API 연결 실패: {e}")
            results.append(False)

        # Menu Service API 테스트
        try:
            response = requests.get('http://localhost:8002/menu/types/')
            if response.status_code == 200:
                print(f"✅ Menu Service 피자 타입 조회 API 성공 (데이터: {len(response.json())}개)")
                results.append(True)
            else:
                print(f"❌ Menu Service 피자 타입 조회 API 실패: {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"❌ Menu Service API 연결 실패: {e}")
            results.append(False)

        # Order Service API 테스트
        try:
            response = requests.get('http://localhost:8003/order/branch/')
            if response.status_code == 200:
                print(f"✅ Order Service 지점 조회 API 성공 (데이터: {len(response.json())}개)")
                results.append(True)
            else:
                print(f"❌ Order Service 지점 조회 API 실패: {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"❌ Order Service API 연결 실패: {e}")
            results.append(False)

        return all(results)

    finally:
        # 프로세스 정리
        for name, proc, port in processes:
            try:
                proc.terminate()
                proc.wait(timeout=5)
                print(f"🛑 {name} Service 서버 중지")
            except:
                proc.kill()
                print(f"💀 {name} Service 서버 강제 종료")


def main():
    """메인 테스트 함수"""
    print("🚀 MSA Pizza Backend 서비스 테스트 시작")
    print("=" * 50)

    results = []

    # 각 서비스별 모델 테스트 (올바른 디렉토리에서)
    results.append(test_service_in_directory("Login Service", "services/login"))
    results.append(test_service_in_directory("Menu Service", "services/menu"))
    results.append(test_service_in_directory("Order Service", "services/order"))

    print("\n" + "=" * 50)

    # API 엔드포인트 테스트
    api_result = test_api_endpoints()
    results.append(api_result)

    print("\n" + "=" * 50)
    print("📊 테스트 결과 요약")
    print("=" * 50)

    service_names = ["Login Service", "Menu Service", "Order Service", "API Endpoints"]
    for i, (name, result) in enumerate(zip(service_names, results)):
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{name}: {status}")

    if all(results):
        print("\n🎉 모든 테스트 통과! MSA 서비스가 정상 작동합니다.")
        return 0
    else:
        print(f"\n⚠️  {sum(results)}/{len(results)}개 테스트 통과")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
