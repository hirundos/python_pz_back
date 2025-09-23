import json
import jwt
from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from unittest.mock import patch, Mock
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from .models import Order, OrderDetail, Branch
from .authentication import CustomJWTAuthentication
from pizza_back.menu.models import PizzaType, Pizza
from pizza_back.login.models import Member


class OrderTestCase(APITestCase):
    """Order 앱의 모든 기능을 테스트하는 클래스"""
    
    def setUp(self):
        """테스트 데이터 설정"""
        # 테스트용 사용자 생성
        self.test_user = Member.objects.create(
            member_id='testuser',
            member_pwd='testpass',
            member_nm='Test User'
        )
        
        # 테스트용 지점 생성
        self.test_branch = Branch.objects.create(
            bran_id='B001',
            bran_nm='강남점'
        )
        
        # 테스트용 피자 타입과 피자 생성
        self.pizza_type = PizzaType.objects.create(
            pizza_type_id='P001',
            pizza_nm='마르게리타',
            pizza_categ='클래식',
            pizza_img_url='https://example.com/margherita.jpg'
        )
        
        self.test_pizza = Pizza.objects.create(
            pizza_id='P001_S',
            pizza_type_id=self.pizza_type,
            size='Small',
            price=15000.0
        )
        
        # JWT 토큰 생성
        self.token = self._create_jwt_token('testuser')
        
    def _create_jwt_token(self, member_id):
        """JWT 토큰 생성 헬퍼 메소드"""
        payload = {
            'member_id': member_id,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        
    def _authenticate_request(self):
        """요청 인증 헬퍼 메소드"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
    @patch('requests.post')
    def test_order_creation_success(self, mock_post):
        """정상적인 주문 생성 테스트"""
        # 외부 API 모킹
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'pizza_id': 'P001_S'}
        mock_post.return_value = mock_response
        
        url = reverse('order')
        data = {
            'lines': [
                {
                    'size': 'Small',
                    'name': '마르게리타',
                    'quantity': 2
                }
            ],
            'branchId': 'B001'
        }
        
        self._authenticate_request()
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = response.json()
        self.assertIn('order_id', response_data)
        self.assertIn('message', response_data)
        
        # 데이터베이스에 주문이 생성되었는지 확인
        self.assertTrue(Order.objects.filter(member_id='testuser').exists())
        self.assertTrue(OrderDetail.objects.filter(order__member_id='testuser').exists())
        
    def test_order_creation_unauthenticated(self):
        """인증되지 않은 사용자의 주문 생성 테스트"""
        url = reverse('order')
        data = {
            'lines': [
                {
                    'size': 'Small',
                    'name': '마르게리타',
                    'quantity': 2
                }
            ],
            'branchId': 'B001'
        }
        
        # 인증 없이 요청
        response = self.client.post(url, data, format='json')
        
        # 인증 누락 시 DRF는 보통 403 Forbidden을 반환
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_order_creation_empty_lines(self):
        """빈 주문 항목으로 주문 생성 테스트"""
        url = reverse('order')
        data = {
            'lines': [],
            'branchId': 'B001'
        }
        
        self._authenticate_request()
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.json())
        
    def test_order_creation_missing_branch_id(self):
        """지점 ID 누락으로 주문 생성 테스트"""
        url = reverse('order')
        data = {
            'lines': [
                {
                    'size': 'Small',
                    'name': '마르게리타',
                    'quantity': 2
                }
            ]
            # 'branchId' 누락
        }
        
        self._authenticate_request()
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.json())
        
    @patch('requests.post')
    def test_order_creation_menu_service_error(self, mock_post):
        """메뉴 서비스 오류로 주문 생성 실패 테스트"""
        # 외부 API 오류 모킹
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        
        url = reverse('order')
        data = {
            'lines': [
                {
                    'size': 'Small',
                    'name': '존재하지않는피자',
                    'quantity': 2
                }
            ],
            'branchId': 'B001'
        }
        
        self._authenticate_request()
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.json())
        
    def test_myorder_list_success(self):
        """주문 내역 조회 성공 테스트"""
        # 테스트용 주문 생성
        order = Order.objects.create(
            order_id=1,
            member_id='testuser',
            bran_id='B001',
            date=timezone.now().date(),
            time=timezone.now().time()
        )
        
        OrderDetail.objects.create(
            order_detail_id=1,
            order=order,
            pizza=self.test_pizza,
            quantity=2
        )
        
        url = reverse('myorder_list')
        self._authenticate_request()
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        
        order_data = data[0]
        self.assertIn('order_id', order_data)
        self.assertIn('pizza_id', order_data)
        self.assertIn('quantity', order_data)
        self.assertIn('date', order_data)
        self.assertIn('time', order_data)
        
    def test_myorder_list_empty(self):
        """빈 주문 내역 조회 테스트"""
        url = reverse('myorder_list')
        self._authenticate_request()
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)
        
    def test_myorder_list_unauthenticated(self):
        """인증되지 않은 사용자의 주문 내역 조회 테스트"""
        url = reverse('myorder_list')
        
        # 인증 없이 요청
        response = self.client.get(url)
        
        # 인증 누락 시 DRF는 보통 403 Forbidden을 반환
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_get_branch_success(self):
        """지점 목록 조회 성공 테스트"""
        # 추가 지점 생성
        Branch.objects.create(
            bran_id='B002',
            bran_nm='홍대점'
        )
        
        url = reverse('get_branch')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
        
        # 지점 데이터 확인
        branch_data = data[0]
        self.assertIn('bran_id', branch_data)
        self.assertIn('bran_nm', branch_data)
        
    def test_get_branch_empty(self):
        """빈 지점 목록 조회 테스트"""
        # 모든 지점 삭제
        Branch.objects.all().delete()
        
        url = reverse('get_branch')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)


class OrderModelTestCase(TestCase):
    """Order 모델 테스트"""
    
    def setUp(self):
        """테스트 데이터 설정"""
        self.test_branch = Branch.objects.create(
            bran_id='B001',
            bran_nm='강남점'
        )
        
    def test_order_creation(self):
        """Order 모델 생성 테스트"""
        order = Order.objects.create(
            order_id=1,
            member_id='testuser',
            bran_id='B001',
            date='2024-01-01',
            time='12:00:00'
        )
        
        self.assertEqual(order.order_id, 1)
        self.assertEqual(order.member_id, 'testuser')
        self.assertEqual(order.bran_id, 'B001')
        self.assertEqual(order.date, '2024-01-01')
        self.assertEqual(order.time, '12:00:00')
        
    def test_order_str_representation(self):
        """Order 모델 문자열 표현 테스트"""
        order = Order.objects.create(
            order_id=1,
            member_id='testuser',
            bran_id='B001',
            date='2024-01-01',
            time='12:00:00'
        )
        
        # __str__ 메소드가 정의되지 않았으므로 기본 동작 확인
        self.assertIsNotNone(str(order))


class OrderDetailModelTestCase(TestCase):
    """OrderDetail 모델 테스트"""
    
    def setUp(self):
        """테스트 데이터 설정"""
        self.test_branch = Branch.objects.create(
            bran_id='B001',
            bran_nm='강남점'
        )
        
        self.test_order = Order.objects.create(
            order_id=1,
            member_id='testuser',
            bran_id='B001',
            date='2024-01-01',
            time='12:00:00'
        )
        
        self.pizza_type = PizzaType.objects.create(
            pizza_type_id='P001',
            pizza_nm='마르게리타',
            pizza_categ='클래식',
            pizza_img_url='https://example.com/margherita.jpg'
        )
        
        self.test_pizza = Pizza.objects.create(
            pizza_id='P001_S',
            pizza_type_id=self.pizza_type,
            size='Small',
            price=15000.0
        )
        
    def test_order_detail_creation(self):
        """OrderDetail 모델 생성 테스트"""
        order_detail = OrderDetail.objects.create(
            order_detail_id=1,
            order=self.test_order,
            pizza=self.test_pizza,
            quantity=2
        )
        
        self.assertEqual(order_detail.order_detail_id, 1)
        self.assertEqual(order_detail.order, self.test_order)
        self.assertEqual(order_detail.pizza, self.test_pizza)
        self.assertEqual(order_detail.quantity, 2)
        
    def test_order_detail_foreign_key_relationships(self):
        """OrderDetail의 외래키 관계 테스트"""
        order_detail = OrderDetail.objects.create(
            order_detail_id=1,
            order=self.test_order,
            pizza=self.test_pizza,
            quantity=2
        )
        
        # 외래키 관계 확인
        self.assertEqual(order_detail.order.member_id, 'testuser')
        self.assertEqual(order_detail.pizza.pizza_type_id.pizza_nm, '마르게리타')
        
    def test_order_detail_cascade_delete(self):
        """Order 삭제 시 OrderDetail CASCADE 삭제 테스트"""
        order_detail = OrderDetail.objects.create(
            order_detail_id=1,
            order=self.test_order,
            pizza=self.test_pizza,
            quantity=2
        )
        
        # Order 삭제
        self.test_order.delete()
        
        # OrderDetail도 함께 삭제되었는지 확인
        self.assertFalse(OrderDetail.objects.filter(order_detail_id=1).exists())
        
    def test_order_detail_str_representation(self):
        """OrderDetail 모델 문자열 표현 테스트"""
        order_detail = OrderDetail.objects.create(
            order_detail_id=1,
            order=self.test_order,
            pizza=self.test_pizza,
            quantity=2
        )
        
        # __str__ 메소드가 정의되지 않았으므로 기본 동작 확인
        self.assertIsNotNone(str(order_detail))


class BranchModelTestCase(TestCase):
    """Branch 모델 테스트"""
    
    def test_branch_creation(self):
        """Branch 모델 생성 테스트"""
        branch = Branch.objects.create(
            bran_id='B001',
            bran_nm='강남점'
        )
        
        self.assertEqual(branch.bran_id, 'B001')
        self.assertEqual(branch.bran_nm, '강남점')
        
    def test_branch_str_representation(self):
        """Branch 모델 문자열 표현 테스트"""
        branch = Branch.objects.create(
            bran_id='B001',
            bran_nm='강남점'
        )
        
        # __str__ 메소드가 정의되지 않았으므로 기본 동작 확인
        self.assertIsNotNone(str(branch))


class CustomJWTAuthenticationTestCase(TestCase):
    """CustomJWTAuthentication 테스트"""
    
    def setUp(self):
        """테스트 데이터 설정"""
        self.test_user = Member.objects.create(
            member_id='testuser',
            member_pwd='testpass',
            member_nm='Test User'
        )
        
        self.auth = CustomJWTAuthentication()
        
    def test_authenticate_success(self):
        """정상적인 인증 테스트"""
        # 유효한 JWT 토큰 생성
        payload = {
            'member_id': 'testuser',
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        
        # Mock request 생성
        class MockRequest:
            def __init__(self, auth_header):
                self.META = {'HTTP_AUTHORIZATION': auth_header}
        
        request = MockRequest(f'Bearer {token}')
        
        # 인증 테스트
        result = self.auth.authenticate(request)
        
        self.assertIsNotNone(result)
        user, token_result = result
        self.assertEqual(user.member_id, 'testuser')
        self.assertEqual(token_result, token)
        
    def test_authenticate_no_header(self):
        """Authorization 헤더가 없는 경우 테스트"""
        class MockRequest:
            def __init__(self):
                self.META = {}
        
        request = MockRequest()
        
        result = self.auth.authenticate(request)
        self.assertIsNone(result)
        
    def test_authenticate_wrong_format(self):
        """잘못된 Authorization 헤더 형식 테스트"""
        class MockRequest:
            def __init__(self, auth_header):
                self.META = {'HTTP_AUTHORIZATION': auth_header}
        
        request = MockRequest('InvalidFormat token')
        
        result = self.auth.authenticate(request)
        self.assertIsNone(result)
        
    def test_authenticate_expired_token(self):
        """만료된 토큰 테스트"""
        # 만료된 JWT 토큰 생성
        payload = {
            'member_id': 'testuser',
            'exp': datetime.utcnow() - timedelta(hours=1),
            'iat': datetime.utcnow() - timedelta(hours=2)
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        
        class MockRequest:
            def __init__(self, auth_header):
                self.META = {'HTTP_AUTHORIZATION': auth_header}
        
        request = MockRequest(f'Bearer {token}')
        
        # 인증 테스트 (예외 발생)
        with self.assertRaises(Exception):
            self.auth.authenticate(request)
            
    def test_authenticate_invalid_token(self):
        """유효하지 않은 토큰 테스트"""
        class MockRequest:
            def __init__(self, auth_header):
                self.META = {'HTTP_AUTHORIZATION': auth_header}
        
        request = MockRequest('Bearer invalid.token.here')
        
        # 인증 테스트 (예외 발생)
        with self.assertRaises(Exception):
            self.auth.authenticate(request)
            
    def test_authenticate_nonexistent_user(self):
        """존재하지 않는 사용자 테스트"""
        # 존재하지 않는 사용자의 토큰 생성
        payload = {
            'member_id': 'nonexistent',
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        
        class MockRequest:
            def __init__(self, auth_header):
                self.META = {'HTTP_AUTHORIZATION': auth_header}
        
        request = MockRequest(f'Bearer {token}')
        
        # 인증 테스트 (예외 발생)
        with self.assertRaises(Exception):
            self.auth.authenticate(request)


class OrderIntegrationTestCase(TestCase):
    """Order 앱 통합 테스트"""
    
    def setUp(self):
        """테스트 데이터 설정"""
        self.client = APIClient()
        
        # 테스트용 사용자 생성
        self.test_user = Member.objects.create(
            member_id='testuser',
            member_pwd='testpass',
            member_nm='Test User'
        )
        
        # 테스트용 지점 생성
        self.test_branch = Branch.objects.create(
            bran_id='B001',
            bran_nm='강남점'
        )
        
        # 테스트용 피자 데이터 생성
        pizza_types = [
            ('P001', '마르게리타', '클래식', 'https://example.com/margherita.jpg'),
            ('P002', '페퍼로니', '미트', 'https://example.com/pepperoni.jpg'),
        ]
        
        for type_id, name, category, img_url in pizza_types:
            pizza_type = PizzaType.objects.create(
                pizza_type_id=type_id,
                pizza_nm=name,
                pizza_categ=category,
                pizza_img_url=img_url
            )
            
            Pizza.objects.create(
                pizza_id=f'{type_id}_S',
                pizza_type_id=pizza_type,
                size='Small',
                price=15000.0
            )
        
        # JWT 토큰 생성
        self.token = self._create_jwt_token('testuser')
        
    def _create_jwt_token(self, member_id):
        """JWT 토큰 생성 헬퍼 메소드"""
        payload = {
            'member_id': member_id,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        
    def _authenticate_request(self):
        """요청 인증 헬퍼 메소드"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
    @patch('requests.post')
    def test_complete_order_workflow(self, mock_post):
        """완전한 주문 워크플로우 테스트"""
        # 외부 API 모킹
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'pizza_id': 'P001_S'}
        mock_post.return_value = mock_response
        
        # 1. 지점 목록 조회
        branch_url = reverse('get_branch')
        branch_response = self.client.get(branch_url)
        self.assertEqual(branch_response.status_code, status.HTTP_200_OK)
        branches = branch_response.json()
        self.assertEqual(len(branches), 1)
        
        # 2. 주문 생성
        order_url = reverse('order')
        order_data = {
            'lines': [
                {
                    'size': 'Small',
                    'name': '마르게리타',
                    'quantity': 2
                }
            ],
            'branchId': 'B001'
        }
        
        self._authenticate_request()
        order_response = self.client.post(order_url, order_data, format='json')
        self.assertEqual(order_response.status_code, status.HTTP_201_CREATED)
        
        # 3. 주문 내역 조회
        myorder_url = reverse('myorder_list')
        myorder_response = self.client.get(myorder_url)
        self.assertEqual(myorder_response.status_code, status.HTTP_200_OK)
        orders = myorder_response.json()
        self.assertEqual(len(orders), 1)
        
        # 주문 데이터 확인
        order_data = orders[0]
        self.assertEqual(order_data['pizza_id'], 'P001_S')
        self.assertEqual(order_data['quantity'], 2)
