import json
import jwt
from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Member


class LoginTestCase(TestCase):
    """Login 앱의 모든 기능을 테스트하는 클래스"""
    
    def setUp(self):
        """테스트 데이터 설정"""
        self.client = Client()
        self.test_user = Member.objects.create(
            member_id='testuser',
            member_pwd='testpass',
            member_nm='Test User'
        )
        
    def test_register_member_success(self):
        """정상적인 회원가입 테스트"""
        url = reverse('register_member')
        data = {
            'id': 'newuser',
            'pw': 'newpass',
            'name': 'New User'
        }
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json())
        self.assertTrue(Member.objects.filter(member_id='newuser').exists())
        
    def test_register_member_duplicate_id(self):
        """중복 ID 회원가입 테스트"""
        url = reverse('register_member')
        data = {
            'id': 'testuser',  # 이미 존재하는 ID
            'pw': 'newpass',
            'name': 'New User'
        }
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 409)
        self.assertIn('error', response.json())
        
    def test_register_member_missing_fields(self):
        """필수 필드 누락 테스트"""
        url = reverse('register_member')
        data = {
            'id': 'newuser',
            # 'pw' 누락
            'name': 'New User'
        }
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        
    def test_register_member_invalid_json(self):
        """잘못된 JSON 형식 테스트"""
        url = reverse('register_member')
        
        response = self.client.post(
            url,
            data='invalid json',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        
    def test_login_check_success(self):
        """정상적인 로그인 테스트"""
        url = reverse('login_check')
        data = {
            'id': 'testuser',
            'pw': 'testpass'
        }
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['count'], 1)
        self.assertIn('token', response_data)
        
        # JWT 토큰 검증
        token = response_data['token']
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        self.assertEqual(payload['member_id'], 'testuser')
        
    def test_login_check_wrong_credentials(self):
        """잘못된 자격증명 테스트"""
        url = reverse('login_check')
        data = {
            'id': 'testuser',
            'pw': 'wrongpass'
        }
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['count'], 0)
        self.assertNotIn('token', response_data)
        
    def test_login_check_nonexistent_user(self):
        """존재하지 않는 사용자 테스트"""
        url = reverse('login_check')
        data = {
            'id': 'nonexistent',
            'pw': 'testpass'
        }
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['count'], 0)
        
    def test_login_check_missing_credentials(self):
        """자격증명 누락 테스트"""
        url = reverse('login_check')
        data = {
            'id': 'testuser'
            # 'pw' 누락
        }
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        
    def test_login_check_wrong_method(self):
        """잘못된 HTTP 메소드 테스트"""
        url = reverse('login_check')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 405)
        self.assertIn('error', response.json())
        
    def test_logout_view_success(self):
        """로그아웃 테스트"""
        url = reverse('logout_view')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json())
        
    def test_logout_view_wrong_method(self):
        """로그아웃 잘못된 메소드 테스트"""
        url = reverse('logout_view')
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 405)
        self.assertIn('error', response.json())


class MemberModelTestCase(TestCase):
    """Member 모델 테스트"""
    
    def test_member_creation(self):
        """Member 모델 생성 테스트"""
        member = Member.objects.create(
            member_id='testuser',
            member_pwd='testpass',
            member_nm='Test User'
        )
        
        self.assertEqual(member.member_id, 'testuser')
        self.assertEqual(member.member_pwd, 'testpass')
        self.assertEqual(member.member_nm, 'Test User')
        self.assertTrue(member.is_authenticated)
        self.assertFalse(member.is_anonymous)
        
    def test_member_str_representation(self):
        """Member 모델 문자열 표현 테스트"""
        member = Member.objects.create(
            member_id='testuser',
            member_pwd='testpass',
            member_nm='Test User'
        )
        
        # __str__ 메소드가 정의되지 않았으므로 기본 동작 확인
        self.assertIsNotNone(str(member))


class JWTTestCase(TestCase):
    """JWT 토큰 관련 테스트"""
    
    def setUp(self):
        """테스트 데이터 설정"""
        self.test_user = Member.objects.create(
            member_id='testuser',
            member_pwd='testpass',
            member_nm='Test User'
        )
        
    def test_jwt_token_generation(self):
        """JWT 토큰 생성 테스트"""
        from .views import verify_jwt_token
        
        # 토큰 생성
        payload = {
            'member_id': 'testuser',
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        
        # 토큰 검증
        decoded_payload = verify_jwt_token(token)
        self.assertIsNotNone(decoded_payload)
        self.assertEqual(decoded_payload['member_id'], 'testuser')
        
    def test_jwt_token_expired(self):
        """만료된 JWT 토큰 테스트"""
        from .views import verify_jwt_token
        
        # 만료된 토큰 생성
        payload = {
            'member_id': 'testuser',
            'exp': datetime.utcnow() - timedelta(hours=1),  # 1시간 전에 만료
            'iat': datetime.utcnow() - timedelta(hours=2)
        }
        
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        
        # 토큰 검증 (만료된 토큰)
        decoded_payload = verify_jwt_token(token)
        self.assertIsNone(decoded_payload)
        
    def test_jwt_token_invalid(self):
        """유효하지 않은 JWT 토큰 테스트"""
        from .views import verify_jwt_token
        
        # 잘못된 토큰
        invalid_token = "invalid.token.here"
        
        # 토큰 검증
        decoded_payload = verify_jwt_token(invalid_token)
        self.assertIsNone(decoded_payload)
