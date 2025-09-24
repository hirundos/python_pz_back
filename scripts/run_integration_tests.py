#!/usr/bin/env python3
"""
MSA Pizza Backend 통합 테스트 스크립트

이 스크립트는 각 서비스가 독립적으로 실행되는 환경에서
서비스 간 상호작용을 테스트합니다.
"""

import os
import sys
import time
import json
import requests
import psycopg2
from typing import Dict, List, Optional
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IntegrationTestRunner:
    """통합 테스트 실행기"""

    def __init__(self):
        """환경 변수에서 서비스 URL 설정"""
        self.login_service_url = os.getenv('LOGIN_SERVICE_URL', 'http://localhost:8001')
        self.menu_service_url = os.getenv('MENU_SERVICE_URL', 'http://localhost:8002')
        self.order_service_url = os.getenv('ORDER_SERVICE_URL', 'http://localhost:8003')
        self.database_url = os.getenv('DATABASE_URL', 'postgresql://test_user:test_pass@localhost:5432/pizza_test')

        # 테스트 결과 저장
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'total': 0,
            'details': []
        }

        # 세션 설정 (연결 재사용)
        self.session = requests.Session()
        self.session.timeout = 10  # 10초 타임아웃

        logger.info("통합 테스트 초기화 완료")
        logger.info(f"Login Service: {self.login_service_url}")
        logger.info(f"Menu Service: {self.menu_service_url}")
        logger.info(f"Order Service: {self.order_service_url}")

    def log_test_result(self, test_name: str, passed: bool, message: str = "", details: str = ""):
        """테스트 결과를 기록"""
        result = {
            'test_name': test_name,
            'passed': passed,
            'message': message,
            'details': details,
            'timestamp': time.time()
        }

        self.test_results['details'].append(result)

        if passed:
            self.test_results['passed'] += 1
            logger.info(f"✅ {test_name}: {message}")
        else:
            self.test_results['failed'] += 1
            logger.error(f"❌ {test_name}: {message}")
            if details:
                logger.error(f"   Details: {details}")

    def wait_for_services(self, max_wait_time: int = 60) -> bool:
        """서비스들이 준비될 때까지 대기"""
        logger.info("서비스 준비 상태 확인 중...")

        start_time = time.time()
        services = {
            'login': self.login_service_url,
            'menu': self.menu_service_url,
            'order': self.order_service_url
        }

        while time.time() - start_time < max_wait_time:
            all_ready = True

            for service_name, service_url in services.items():
                try:
                    response = self.session.get(f"{service_url}/api/health/", timeout=5)
                    if response.status_code == 200:
                        logger.info(f"✅ {service_name} 서비스 준비됨")
                    else:
                        all_ready = False
                        break
                except requests.exceptions.RequestException:
                    logger.debug(f"⏳ {service_name} 서비스 응답 대기 중...")
                    all_ready = False
                    break

            if all_ready:
                logger.info("모든 서비스가 준비되었습니다!")
                return True

            time.sleep(2)

        logger.error("서비스 준비 타임아웃")
        return False

    def test_database_connection(self) -> bool:
        """데이터베이스 연결 테스트"""
        try:
            conn = psycopg2.connect(self.database_url)
            conn.close()
            self.log_test_result("database_connection", True, "데이터베이스 연결 성공")
            return True
        except Exception as e:
            self.log_test_result("database_connection", False, "데이터베이스 연결 실패", str(e))
            return False

    def test_user_registration_and_login(self) -> bool:
        """사용자 등록 및 로그인 통합 테스트"""
        try:
            # 1. 회원가입
            register_data = {
                "member_id": "integration_test_user",
                "member_pwd": "test_password123",
                "member_nm": "통합테스트사용자"
            }

            response = self.session.post(
                f"{self.login_service_url}/api/login/register/",
                json=register_data
            )

            if response.status_code != 201:
                self.log_test_result(
                    "user_registration",
                    False,
                    "회원가입 실패",
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False

            self.log_test_result("user_registration", True, "회원가입 성공")

            # 2. 로그인
            login_data = {
                "member_id": "integration_test_user",
                "member_pwd": "test_password123"
            }

            response = self.session.post(
                f"{self.login_service_url}/api/login/",
                json=login_data
            )

            if response.status_code != 200:
                self.log_test_result(
                    "user_login",
                    False,
                    "로그인 실패",
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False

            token = response.json().get('token')
            if not token:
                self.log_test_result("user_login", False, "JWT 토큰 획득 실패")
                return False

            # JWT 토큰을 세션에 설정
            self.session.headers.update({'Authorization': f'Bearer {token}'})

            self.log_test_result("user_login", True, "로그인 성공 및 토큰 획득")

            return True

        except Exception as e:
            self.log_test_result(
                "user_registration_login",
                False,
                "사용자 등록/로그인 테스트 실패",
                str(e)
            )
            return False

    def test_menu_service(self) -> bool:
        """메뉴 서비스 테스트"""
        try:
            # 피자 타입 조회
            response = self.session.get(f"{self.menu_service_url}/api/menu/types/")

            if response.status_code != 200:
                self.log_test_result(
                    "menu_types_retrieval",
                    False,
                    "피자 타입 조회 실패",
                    f"Status: {response.status_code}"
                )
                return False

            pizza_types = response.json()
            if not pizza_types:
                self.log_test_result("menu_types_retrieval", False, "피자 타입 데이터 없음")
                return False

            self.log_test_result("menu_types_retrieval", True, f"피자 타입 {len(pizza_types)}개 조회 성공")

            # 피자 메뉴 조회
            response = self.session.get(f"{self.menu_service_url}/api/menu/")

            if response.status_code != 200:
                self.log_test_result(
                    "menu_retrieval",
                    False,
                    "피자 메뉴 조회 실패",
                    f"Status: {response.status_code}"
                )
                return False

            pizzas = response.json()
            if not pizzas:
                self.log_test_result("menu_retrieval", False, "피자 메뉴 데이터 없음")
                return False

            self.log_test_result("menu_retrieval", True, f"피자 메뉴 {len(pizzas)}개 조회 성공")

            return True

        except Exception as e:
            self.log_test_result(
                "menu_service_test",
                False,
                "메뉴 서비스 테스트 실패",
                str(e)
            )
            return False

    def test_order_creation_flow(self) -> bool:
        """주문 생성 전체 플로우 테스트"""
        try:
            # 1. 지점 목록 조회
            response = self.session.get(f"{self.order_service_url}/api/order/branch/")

            if response.status_code != 200:
                self.log_test_result(
                    "branch_retrieval",
                    False,
                    "지점 조회 실패",
                    f"Status: {response.status_code}"
                )
                return False

            branches = response.json()
            if not branches:
                self.log_test_result("branch_retrieval", False, "지점 데이터 없음")
                return False

            # 첫 번째 지점 선택
            branch_id = branches[0]['bran_id']
            self.log_test_result("branch_retrieval", True, f"지점 조회 성공: {branch_id}")

            # 2. 피자 ID 조회 (Menu Service 호출)
            pizza_id_data = {
                "pizza_nm": "페페로니",  # 실제 피자 이름에 맞게 조정 필요
                "size": "L"
            }

            response = self.session.post(
                f"{self.menu_service_url}/api/menu/get_pizza_id/",
                json=pizza_id_data
            )

            if response.status_code != 200:
                self.log_test_result(
                    "pizza_id_lookup",
                    False,
                    "피자 ID 조회 실패",
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False

            pizza_id = response.json().get('pizza_id')
            if not pizza_id:
                self.log_test_result("pizza_id_lookup", False, "피자 ID 획득 실패")
                return False

            self.log_test_result("pizza_id_lookup", True, f"피자 ID 조회 성공: {pizza_id}")

            # 3. 주문 생성
            order_data = {
                "bran_id": branch_id,
                "date": "2024-12-25",
                "time": "18:00:00",
                "items": [
                    {
                        "pizza_id": pizza_id,
                        "quantity": 2
                    }
                ]
            }

            response = self.session.post(
                f"{self.order_service_url}/api/order/",
                json=order_data
            )

            if response.status_code != 201:
                self.log_test_result(
                    "order_creation",
                    False,
                    "주문 생성 실패",
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False

            order_id = response.json().get('order_id')
            if not order_id:
                self.log_test_result("order_creation", False, "주문 ID 획득 실패")
                return False

            self.log_test_result("order_creation", True, f"주문 생성 성공: {order_id}")

            # 4. 주문 내역 조회
            response = self.session.get(f"{self.order_service_url}/api/order/myorder/")

            if response.status_code != 200:
                self.log_test_result(
                    "order_retrieval",
                    False,
                    "주문 내역 조회 실패",
                    f"Status: {response.status_code}"
                )
                return False

            orders = response.json()
            if not orders:
                self.log_test_result("order_retrieval", False, "주문 내역 없음")
                return False

            # 생성된 주문이 있는지 확인
            found_order = None
            for order in orders:
                if order.get('order_id') == order_id:
                    found_order = order
                    break

            if not found_order:
                self.log_test_result("order_retrieval", False, "생성된 주문이 조회되지 않음")
                return False

            self.log_test_result("order_retrieval", True, f"주문 내역 조회 성공: {len(orders)}개 주문")

            return True

        except Exception as e:
            self.log_test_result(
                "order_creation_flow",
                False,
                "주문 생성 플로우 테스트 실패",
                str(e)
            )
            return False

    def test_error_scenarios(self) -> bool:
        """에러 시나리오 테스트"""
        try:
            # 1. 잘못된 JWT 토큰 테스트
            self.session.headers.update({'Authorization': 'Bearer invalid_token'})

            response = self.session.get(f"{self.order_service_url}/api/order/myorder/")

            if response.status_code == 401:
                self.log_test_result("invalid_token_handling", True, "잘못된 토큰 처리 성공")
            else:
                self.log_test_result(
                    "invalid_token_handling",
                    False,
                    "잘못된 토큰 처리가 올바르지 않음",
                    f"Status: {response.status_code}"
                )

            # 2. 존재하지 않는 엔드포인트 테스트
            response = self.session.get(f"{self.login_service_url}/api/login/nonexistent/")

            if response.status_code == 404:
                self.log_test_result("not_found_handling", True, "404 에러 처리 성공")
            else:
                self.log_test_result(
                    "not_found_handling",
                    False,
                    "404 에러 처리가 올바르지 않음",
                    f"Status: {response.status_code}"
                )

            # 토큰 헤더 제거 (다음 테스트를 위해)
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']

            return True

        except Exception as e:
            self.log_test_result(
                "error_scenarios",
                False,
                "에러 시나리오 테스트 실패",
                str(e)
            )
            return False

    def run_all_tests(self) -> bool:
        """모든 통합 테스트 실행"""
        logger.info("=== 통합 테스트 시작 ===")

        # 테스트 업데이트
        self.test_results['total'] = 6  # 전체 테스트 수

        # 1. 서비스 준비 확인
        if not self.wait_for_services():
            self.log_test_result("service_readiness", False, "서비스 준비 실패")
            return False

        # 2. 데이터베이스 연결 테스트
        if not self.test_database_connection():
            return False

        # 3. 사용자 등록 및 로그인 테스트
        if not self.test_user_registration_and_login():
            return False

        # 4. 메뉴 서비스 테스트
        if not self.test_menu_service():
            return False

        # 5. 주문 생성 플로우 테스트
        if not self.test_order_creation_flow():
            return False

        # 6. 에러 시나리오 테스트
        if not self.test_error_scenarios():
            return False

        # 테스트 결과 요약
        self.print_test_summary()

        # 전체 성공 여부 반환
        return self.test_results['failed'] == 0

    def print_test_summary(self):
        """테스트 결과 요약 출력"""
        logger.info("=== 테스트 결과 요약 ===")
        logger.info(f"전체 테스트 수: {self.test_results['total']}")
        logger.info(f"통과: {self.test_results['passed']}")
        logger.info(f"실패: {self.test_results['failed']}")

        if self.test_results['failed'] > 0:
            logger.error("실패한 테스트:")
            for result in self.test_results['details']:
                if not result['passed']:
                    logger.error(f"  - {result['test_name']}: {result['message']}")

        if self.test_results['passed'] == self.test_results['total']:
            logger.info("🎉 모든 통합 테스트 통과!")
        else:
            logger.error("⚠️  일부 테스트 실패")

    def save_results_to_file(self, filename: str = "test-results/integration_test_results.json"):
        """테스트 결과를 파일로 저장"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)

        logger.info(f"테스트 결과가 {filename}에 저장되었습니다.")


def main():
    """메인 함수"""
    runner = IntegrationTestRunner()
    success = runner.run_all_tests()

    # 결과 파일로 저장
    runner.save_results_to_file()

    # 종료 코드 설정
    exit_code = 0 if success else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
