from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import PizzaType, Pizza


class PizzaModelTest(TestCase):
    """피자 모델 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.pizza_type = PizzaType.objects.create(
            pizza_type_id="TEST001",
            pizza_nm="테스트피자",
            pizza_categ="테스트",
            pizza_img_url="http://example.com/test.jpg"
        )

        self.pizza = Pizza.objects.create(
            pizza_id="TEST_PIZZA_001",
            pizza_type=self.pizza_type,
            size="L",
            price=25000.00
        )

    def test_pizza_type_creation(self):
        """PizzaType 모델 생성 테스트"""
        self.assertEqual(self.pizza_type.pizza_type_id, "TEST001")
        self.assertEqual(self.pizza_type.pizza_nm, "테스트피자")
        self.assertEqual(self.pizza_type.pizza_categ, "테스트")
        self.assertTrue(isinstance(self.pizza_type, PizzaType))

    def test_pizza_creation(self):
        """Pizza 모델 생성 테스트"""
        self.assertEqual(self.pizza.pizza_id, "TEST_PIZZA_001")
        self.assertEqual(self.pizza.size, "L")
        self.assertEqual(self.pizza.price, 25000.00)
        self.assertEqual(self.pizza.pizza_type, self.pizza_type)
        self.assertTrue(isinstance(self.pizza, Pizza))

    def test_pizza_type_str(self):
        """PizzaType 모델 문자열 표현 테스트"""
        self.assertEqual(str(self.pizza_type), "TEST001")

    def test_pizza_str(self):
        """Pizza 모델 문자열 표현 테스트"""
        self.assertEqual(str(self.pizza), "TEST_PIZZA_001")

    def test_foreign_key_relationship(self):
        """외래키 관계 테스트"""
        self.assertEqual(self.pizza.pizza_type.pizza_nm, "테스트피자")


class MenuAPITest(APITestCase):
    """메뉴 API 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.pizza_type1 = PizzaType.objects.create(
            pizza_type_id="PT001",
            pizza_nm="페페로니",
            pizza_categ="클래식",
            pizza_img_url="http://example.com/pepperoni.jpg"
        )
        self.pizza_type2 = PizzaType.objects.create(
            pizza_type_id="PT002",
            pizza_nm="치즈",
            pizza_categ="클래식",
            pizza_img_url="http://example.com/cheese.jpg"
        )

        self.pizza1 = Pizza.objects.create(
            pizza_id="PIZZA_001_L",
            pizza_type=self.pizza_type1,
            size="L",
            price=25000.00
        )
        self.pizza2 = Pizza.objects.create(
            pizza_id="PIZZA_001_M",
            pizza_type=self.pizza_type1,
            size="M",
            price=20000.00
        )
        self.pizza3 = Pizza.objects.create(
            pizza_id="PIZZA_002_L",
            pizza_type=self.pizza_type2,
            size="L",
            price=23000.00
        )

        self.menu_url = reverse('menu-list')
        self.types_url = reverse('pizza-types-list')
        self.get_pizza_id_url = reverse('get_pizza_id')

    def test_get_all_pizzas(self):
        """전체 피자 목록 조회 테스트"""
        response = self.client.get(self.menu_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        # 응답 데이터 구조 검증
        for pizza in response.data:
            self.assertIn('pizza_id', pizza)
            self.assertIn('pizza_type', pizza)
            self.assertIn('size', pizza)
            self.assertIn('price', pizza)

    def test_get_pizza_types(self):
        """피자 타입 목록 조회 테스트"""
        response = self.client.get(self.types_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # 응답 데이터 구조 검증
        for pizza_type in response.data:
            self.assertIn('pizza_type_id', pizza_type)
            self.assertIn('pizza_nm', pizza_type)
            self.assertIn('pizza_categ', pizza_type)
            self.assertIn('pizza_img_url', pizza_type)

    def test_get_pizza_id_success(self):
        """피자 ID 조회 성공 테스트"""
        data = {
            "pizza_nm": "페페로니",
            "size": "L"
        }
        response = self.client.post(self.get_pizza_id_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['pizza_id'], "PIZZA_001_L")

    def test_get_pizza_id_not_found(self):
        """존재하지 않는 피자 ID 조회 테스트"""
        data = {
            "pizza_nm": "존재하지않는피자",
            "size": "L"
        }
        response = self.client.post(self.get_pizza_id_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_pizza_id_invalid_size(self):
        """잘못된 사이즈로 피자 ID 조회 테스트"""
        data = {
            "pizza_nm": "페페로니",
            "size": "XL"  # 존재하지 않는 사이즈
        }
        response = self.client.post(self.get_pizza_id_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_empty_menu_database(self):
        """빈 데이터베이스에서 메뉴 조회 테스트"""
        # 모든 데이터 삭제
        Pizza.objects.all().delete()
        PizzaType.objects.all().delete()

        response = self.client.get(self.menu_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_empty_types_database(self):
        """빈 데이터베이스에서 피자 타입 조회 테스트"""
        # 모든 데이터 삭제
        PizzaType.objects.all().delete()

        response = self.client.get(self.types_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class PizzaDataIntegrityTest(TestCase):
    """피자 데이터 무결성 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.pizza_type = PizzaType.objects.create(
            pizza_type_id="INTEGRITY_TEST",
            pizza_nm="무결성테스트피자",
            pizza_categ="테스트",
            pizza_img_url="http://example.com/integrity.jpg"
        )

    def test_pizza_cannot_exist_without_type(self):
        """피자 타입 없이 피자가 존재할 수 없음 테스트"""
        # 피자 타입이 삭제되면 연결된 피자도 삭제되어야 함
        pizza = Pizza.objects.create(
            pizza_id="INTEGRITY_PIZZA",
            pizza_type=self.pizza_type,
            size="L",
            price=25000.00
        )

        # 피자 타입 삭제
        self.pizza_type.delete()

        # 연결된 피자도 삭제되었는지 확인 (CASCADE가 설정되지 않았으므로 수동으로 확인)
        with self.assertRaises(Pizza.DoesNotExist):
            Pizza.objects.get(pizza_id="INTEGRITY_PIZZA")

    def test_duplicate_pizza_id_not_allowed(self):
        """중복된 피자 ID는 허용되지 않음 테스트"""
        # 첫 번째 피자 생성
        Pizza.objects.create(
            pizza_id="DUPLICATE_TEST",
            pizza_type=self.pizza_type,
            size="L",
            price=25000.00
        )

        # 중복 ID로 피자 생성 시도 (실패 예상)
        with self.assertRaises(Exception):  # Django는 기본적으로 중복 키 에러 발생
            Pizza.objects.create(
                pizza_id="DUPLICATE_TEST",  # 중복 ID
                pizza_type=self.pizza_type,
                size="M",
                price=20000.00
            )
