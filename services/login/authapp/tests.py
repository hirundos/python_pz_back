import json
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Member


class MemberModelTest(TestCase):
    """Member 모델 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.test_member = Member.objects.create(
            member_id="test_user",
            member_pwd="test_password123",
            member_nm="테스트사용자"
        )

    def test_member_creation(self):
        """Member 모델 생성 테스트"""
        self.assertEqual(self.test_member.member_id, "test_user")
        self.assertEqual(self.test_member.member_nm, "테스트사용자")
        self.assertTrue(isinstance(self.test_member, Member))

    def test_member_str(self):
        """Member 모델 문자열 표현 테스트"""
        self.assertEqual(str(self.test_member), "test_user")


class LoginAPITest(APITestCase):
    """로그인 API 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.test_member = Member.objects.create(
            member_id="test_user",
            member_pwd="test_password123",
            member_nm="테스트사용자"
        )
        self.login_url = reverse('login')
        self.register_url = reverse('register')
        self.logout_url = reverse('logout')

    def test_successful_login(self):
        """성공적인 로그인 테스트"""
        data = {
            "member_id": "test_user",
            "password": "test_password123"
        }
        response = self.client.post(self.login_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('member_id', response.data)

    def test_failed_login_wrong_password(self):
        """잘못된 비밀번호로 로그인 실패 테스트"""
        data = {
            "member_id": "test_user",
            "password": "wrong_password"
        }
        response = self.client.post(self.login_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_failed_login_nonexistent_user(self):
        """존재하지 않는 사용자로 로그인 실패 테스트"""
        data = {
            "member_id": "nonexistent_user",
            "member_pwd": "test_password123"
        }
        response = self.client.post(self.login_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_successful_registration(self):
        """성공적인 회원가입 테스트"""
        data = {
            "member_id": "new_user",
            "password": "new_password123",
            "member_nm": "새사용자"
        }
        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)

        # 데이터베이스에 사용자 생성되었는지 확인
        self.assertTrue(Member.objects.filter(member_id="new_user").exists())

    def test_failed_registration_duplicate_id(self):
        """중복 ID로 회원가입 실패 테스트"""
        data = {
            "member_id": "test_user",  # 이미 존재하는 ID
            "member_pwd": "new_password123",
            "member_nm": "새사용자"
        }
        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_failed_registration_missing_fields(self):
        """필수 필드 누락으로 회원가입 실패 테스트"""
        data = {
            "member_id": "new_user"
            # member_pwd와 member_nm 누락
        }
        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout(self):
        """로그아웃 테스트"""
        response = self.client.get(self.logout_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # JsonResponse의 content를 확인
        self.assertIn('logged out', response.content.decode())


class AuthenticationMiddlewareTest(APITestCase):
    """인증 미들웨어 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.test_member = Member.objects.create(
            member_id="test_user",
            member_pwd="test_password123",
            member_nm="테스트사용자"
        )

    def test_valid_jwt_token(self):
        """유효한 JWT 토큰 테스트"""
        # 로그인하여 토큰 획득
        login_data = {
            "member_id": "test_user",
            "member_pwd": "test_password123"
        }
        login_response = self.client.post(reverse('login'), login_data, format='json')

        # 로그인 성공 확인
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn('token', login_response.data)

    def test_invalid_jwt_token(self):
        """유효하지 않은 JWT 토큰 테스트"""
        # 잘못된 토큰으로 로그인 시도
        login_data = {
            "member_id": "test_user",
            "member_pwd": "wrong_password"
        }
        response = self.client.post(reverse('login'), login_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_missing_credentials(self):
        """자격증명 누락 테스트"""
        # 빈 데이터로 로그인 시도
        login_data = {}
        response = self.client.post(reverse('login'), login_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
