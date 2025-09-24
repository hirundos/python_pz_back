import os
import sys
import jwt
from datetime import datetime, timedelta
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.db import transaction
from unittest.mock import patch, MagicMock
from orders.models import Branch, Order, OrderDetail
from django.conf import settings

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def create_test_jwt_token(member_id="test_user"):
    """테스트용 JWT 토큰 생성"""
    payload = {
        'member_id': member_id,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


class OrderModelTest(TestCase):
    """주문 모델 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.branch = Branch.objects.create(
            bran_id="BRANCH001",
            bran_nm="강남점"
        )

        self.order = Order.objects.create(
            order_id="ORDER_TEST_001",
            member_id="test_user_001",
            bran=self.branch,
            date="2024-01-15",
            time="14:30:00"
        )

        self.order_detail = OrderDetail.objects.create(
            order_detail_id=1,
            order=self.order,
            pizza_id="PIZZA_TEST_001",
            quantity=2
        )

    def test_branch_creation(self):
        """Branch 모델 생성 테스트"""
        self.assertEqual(self.branch.bran_id, "BRANCH001")
        self.assertEqual(self.branch.bran_nm, "강남점")
        self.assertTrue(isinstance(self.branch, Branch))

    def test_order_creation(self):
        """Order 모델 생성 테스트"""
        self.assertEqual(self.order.order_id, "ORDER_TEST_001")
        self.assertEqual(self.order.member_id, "test_user_001")
        self.assertEqual(self.order.bran, self.branch)
        self.assertEqual(self.order.date, "2024-01-15")
        self.assertEqual(self.order.time, "14:30:00")
        self.assertTrue(isinstance(self.order, Order))

    def test_order_detail_creation(self):
        """OrderDetail 모델 생성 테스트"""
        self.assertEqual(self.order_detail.order_detail_id, 1)
        self.assertEqual(self.order_detail.order, self.order)
        self.assertEqual(self.order_detail.pizza_id, "PIZZA_TEST_001")
        self.assertEqual(self.order_detail.quantity, 2)
        self.assertTrue(isinstance(self.order_detail, OrderDetail))

    def test_order_str(self):
        """Order 모델 문자열 표현 테스트"""
        self.assertEqual(str(self.order), "ORDER_TEST_001")

    def test_branch_str(self):
        """Branch 모델 문자열 표현 테스트"""
        self.assertEqual(str(self.branch), "BRANCH001")

    def test_foreign_key_relationship(self):
        """외래키 관계 테스트"""
        self.assertEqual(self.order_detail.order.order_id, "ORDER_TEST_001")
        self.assertEqual(self.order.bran.bran_nm, "강남점")


class OrderAPITest(APITestCase):
    """주문 API 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.branch1 = Branch.objects.create(
            bran_id="BRANCH001",
            bran_nm="강남점"
        )
        self.branch2 = Branch.objects.create(
            bran_id="BRANCH002",
            bran_nm="홍대점"
        )

        self.order_url = reverse('order-list')
        self.myorder_url = reverse('myorder')
        self.branch_url = reverse('branch-list')

    def test_get_all_branches(self):
        """전체 지점 목록 조회 테스트"""
        response = self.client.get(self.branch_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 2)

        # 응답 데이터 구조 검증
        for branch in data:
            self.assertIn('bran_id', branch)
            self.assertIn('bran_nm', branch)

    def test_empty_branches_database(self):
        """빈 데이터베이스에서 지점 조회 테스트"""
        # 모든 지점 삭제
        Branch.objects.all().delete()

        response = self.client.get(self.branch_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 0)

    @patch('orders.views.requests.post')
    def test_create_order_success(self, mock_post):
        """주문 생성 성공 테스트"""
        # Mock API 응답 설정
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"pizza_id": "PIZZA_TEST_001"}
        mock_post.return_value = mock_response

        # 인증 헤더 설정 (실제 JWT 토큰 사용)
        token = create_test_jwt_token("test_user")
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        data = {
            "bran_id": "BRANCH001",
            "date": "2024-01-15",
            "time": "14:30:00",
            "items": [
                {
                    "pizza_id": "PIZZA_TEST_001",
                    "quantity": 2
                }
            ]
        }

        response = self.client.post(self.order_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('order_id', response.json())

        # 주문이 생성되었는지 확인
        order = Order.objects.filter(member_id="test_user").first()
        self.assertIsNotNone(order)

    @patch('orders.views.requests.post')
    def test_create_order_unauthorized(self, mock_post):
        """인증되지 않은 사용자의 주문 생성 실패 테스트"""
        data = {
            "bran_id": "BRANCH001",
            "date": "2024-01-15",
            "time": "14:30:00",
            "items": [
                {
                    "pizza_id": "PIZZA_TEST_001",
                    "quantity": 2
                }
            ]
        }

        response = self.client.post(self.order_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('orders.views.requests.post')
    def test_create_order_invalid_data(self, mock_post):
        """잘못된 데이터로 주문 생성 실패 테스트"""
        # 인증 헤더 설정
        token = create_test_jwt_token("test_user")
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        # 필수 필드 누락
        data = {
            "bran_id": "BRANCH001",
            # date, time, items 누락
        }

        response = self.client.post(self.order_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('orders.views.requests.post')
    def test_create_order_menu_api_failure(self, mock_post):
        """메뉴 API 호출 실패 시 주문 생성 실패 테스트"""
        # Mock API 실패 응답 설정
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_post.return_value = mock_response

        # 인증 헤더 설정
        token = create_test_jwt_token("test_user")
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        data = {
            "bran_id": "BRANCH001",
            "date": "2024-01-15",
            "time": "14:30:00",
            "items": [
                {
                    "pizza_id": "INVALID_PIZZA",
                    "quantity": 2
                }
            ]
        }

        response = self.client.post(self.order_url, data, format='json')

        # 주문이 생성되지 않아야 함
        self.assertNotEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_my_orders_unauthorized(self):
        """인증되지 않은 사용자의 주문 내역 조회 실패 테스트"""
        response = self.client.get(self.myorder_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_my_orders_empty(self):
        """빈 주문 내역 조회 테스트"""
        token = create_test_jwt_token("test_user")
        response = self.client.get(self.myorder_url, HTTP_AUTHORIZATION=f'Bearer {token}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 0)


class OrderTransactionTest(TestCase):
    """주문 트랜잭션 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.branch = Branch.objects.create(
            bran_id="TX_BRANCH001",
            bran_nm="트랜잭션테스트점"
        )

    @patch('orders.views.requests.post')
    def test_order_creation_rollback_on_error(self, mock_post):
        """에러 발생 시 주문 생성 롤백 테스트"""
        # Mock API 실패 응답 설정
        mock_response = MagicMock()
        mock_response.status_code = 500  # 서버 에러
        mock_post.return_value = mock_response

        # 트랜잭션 내에서 실행되는지 확인
        with transaction.atomic():
            # 인증 헤더 설정 (TestCase에서는 직접 헤더 설정)
            token = create_test_jwt_token("test_user")

            data = {
                "bran_id": "TX_BRANCH001",
                "date": "2024-01-15",
                "time": "14:30:00",
                "items": [
                    {
                        "pizza_id": "PIZZA_ERROR_TEST",
                        "quantity": 1
                    }
                ]
            }

            # 이 요청은 실패해야 하고, 데이터베이스에 아무것도 저장되지 않아야 함
            response = self.client.post(reverse('order-list'), data, format='json', HTTP_AUTHORIZATION=f'Bearer {token}')

            # 실패 응답 확인
            self.assertNotEqual(response.status_code, status.HTTP_201_CREATED)

            # 데이터베이스에 주문이 생성되지 않았는지 확인
            self.assertFalse(Order.objects.filter(member_id="test_user").exists())


class OrderDataIntegrityTest(TestCase):
    """주문 데이터 무결성 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.branch = Branch.objects.create(
            bran_id="INTEGRITY_BRANCH001",
            bran_nm="무결성테스트점"
        )

        self.order = Order.objects.create(
            order_id="INTEGRITY_ORDER_001",
            member_id="integrity_user",
            bran=self.branch,
            date="2024-01-15",
            time="14:30:00"
        )

    def test_cascade_delete_order_detail(self):
        """주문 삭제 시 주문 상세도 함께 삭제되는지 테스트"""
        # 주문 상세 생성
        order_detail = OrderDetail.objects.create(
            order_detail_id=100,
            order=self.order,
            pizza_id="PIZZA_INTEGRITY_TEST",
            quantity=1
        )

        # 주문 삭제
        self.order.delete()

        # 주문 상세도 삭제되었는지 확인
        with self.assertRaises(OrderDetail.DoesNotExist):
            OrderDetail.objects.get(order_detail_id=100)

    def test_order_detail_cannot_exist_without_order(self):
        """주문 없이 주문 상세가 존재할 수 없음 테스트"""
        # 주문 삭제
        self.order.delete()

        # 주문 상세 생성 시도 (실패 예상)
        with self.assertRaises(Exception):
            OrderDetail.objects.create(
                order_detail_id=200,
                order=self.order,  # 이미 삭제된 주문
                pizza_id="PIZZA_TEST",
                quantity=1
            )
