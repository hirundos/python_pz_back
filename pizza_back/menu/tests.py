import json
from django.test import TestCase, Client
from django.urls import reverse
from .models import PizzaType, Pizza


class MenuTestCase(TestCase):
    """Menu 앱의 모든 기능을 테스트하는 클래스"""
    
    def setUp(self):
        """테스트 데이터 설정"""
        self.client = Client()
        
        # 테스트용 피자 타입 생성
        self.pizza_type = PizzaType.objects.create(
            pizza_type_id='P001',
            pizza_nm='마르게리타',
            pizza_categ='클래식',
            pizza_img_url='https://example.com/margherita.jpg'
        )
        
        # 테스트용 피자 생성
        self.pizza_small = Pizza.objects.create(
            pizza_id='P001_S',
            pizza_type_id=self.pizza_type,
            size='Small',
            price=15000.0
        )
        
        self.pizza_large = Pizza.objects.create(
            pizza_id='P001_L',
            pizza_type_id=self.pizza_type,
            size='Large',
            price=25000.0
        )
        
        # 추가 피자 타입과 피자 생성
        self.pizza_type2 = PizzaType.objects.create(
            pizza_type_id='P002',
            pizza_nm='페퍼로니',
            pizza_categ='미트',
            pizza_img_url='https://example.com/pepperoni.jpg'
        )
        
        self.pizza_medium = Pizza.objects.create(
            pizza_id='P002_M',
            pizza_type_id=self.pizza_type2,
            size='Medium',
            price=20000.0
        )
        
    def test_pizza_list_success(self):
        """피자 목록 조회 성공 테스트"""
        url = reverse('pizza_list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)  # 3개의 피자
        
        # 첫 번째 피자 데이터 확인
        first_pizza = data[0]
        self.assertIn('pizza_type_id__pizza_categ', first_pizza)
        self.assertIn('pizza_type_id__pizza_nm', first_pizza)
        self.assertIn('size', first_pizza)
        self.assertIn('price', first_pizza)
        
    def test_pizza_list_empty_database(self):
        """빈 데이터베이스에서 피자 목록 조회 테스트"""
        # 모든 피자 삭제
        Pizza.objects.all().delete()
        
        url = reverse('pizza_list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)
        
    def test_pizza_type_list_success(self):
        """피자 종류 목록 조회 성공 테스트"""
        url = reverse('pizza_type_list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)  # 2개의 피자 타입
        
        # 첫 번째 피자 타입 데이터 확인
        first_type = data[0]
        self.assertIn('pizza_nm', first_type)
        self.assertIn('pizza_img_url', first_type)
        
    def test_pizza_type_list_empty_database(self):
        """빈 데이터베이스에서 피자 종류 목록 조회 테스트"""
        # 모든 피자 타입 삭제
        PizzaType.objects.all().delete()
        
        url = reverse('pizza_type_list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)
        
    def test_get_pizza_id_success(self):
        """피자 ID 조회 성공 테스트"""
        url = reverse('get_pizza_id')
        data = {
            'size': 'Small',
            'name': '마르게리타'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn('pizza_id', response_data)
        self.assertEqual(response_data['pizza_id'], 'P001_S')
        
    def test_get_pizza_id_different_size(self):
        """다른 사이즈로 피자 ID 조회 테스트"""
        url = reverse('get_pizza_id')
        data = {
            'size': 'Large',
            'name': '마르게리타'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn('pizza_id', response_data)
        self.assertEqual(response_data['pizza_id'], 'P001_L')
        
    def test_get_pizza_id_nonexistent_pizza_type(self):
        """존재하지 않는 피자 타입으로 ID 조회 테스트"""
        url = reverse('get_pizza_id')
        data = {
            'size': 'Small',
            'name': '존재하지않는피자'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn('error', response_data)
        
    def test_get_pizza_id_nonexistent_size(self):
        """존재하지 않는 사이즈로 ID 조회 테스트"""
        url = reverse('get_pizza_id')
        data = {
            'size': 'ExtraLarge',
            'name': '마르게리타'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn('error', response_data)
        
    def test_get_pizza_id_missing_size(self):
        """사이즈 누락으로 피자 ID 조회 테스트"""
        url = reverse('get_pizza_id')
        data = {
            'name': '마르게리타'
            # 'size' 누락
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn('error', response_data)
        
    def test_get_pizza_id_missing_name(self):
        """이름 누락으로 피자 ID 조회 테스트"""
        url = reverse('get_pizza_id')
        data = {
            'size': 'Small'
            # 'name' 누락
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn('error', response_data)
        
    def test_get_pizza_id_wrong_method(self):
        """잘못된 HTTP 메소드로 피자 ID 조회 테스트"""
        url = reverse('get_pizza_id')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 405)


class PizzaTypeModelTestCase(TestCase):
    """PizzaType 모델 테스트"""
    
    def test_pizza_type_creation(self):
        """PizzaType 모델 생성 테스트"""
        pizza_type = PizzaType.objects.create(
            pizza_type_id='P001',
            pizza_nm='마르게리타',
            pizza_categ='클래식',
            pizza_img_url='https://example.com/margherita.jpg'
        )
        
        self.assertEqual(pizza_type.pizza_type_id, 'P001')
        self.assertEqual(pizza_type.pizza_nm, '마르게리타')
        self.assertEqual(pizza_type.pizza_categ, '클래식')
        self.assertEqual(pizza_type.pizza_img_url, 'https://example.com/margherita.jpg')
        
    def test_pizza_type_str_representation(self):
        """PizzaType 모델 문자열 표현 테스트"""
        pizza_type = PizzaType.objects.create(
            pizza_type_id='P001',
            pizza_nm='마르게리타',
            pizza_categ='클래식',
            pizza_img_url='https://example.com/margherita.jpg'
        )
        
        # __str__ 메소드가 정의되지 않았으므로 기본 동작 확인
        self.assertIsNotNone(str(pizza_type))


class PizzaModelTestCase(TestCase):
    """Pizza 모델 테스트"""
    
    def setUp(self):
        """테스트 데이터 설정"""
        self.pizza_type = PizzaType.objects.create(
            pizza_type_id='P001',
            pizza_nm='마르게리타',
            pizza_categ='클래식',
            pizza_img_url='https://example.com/margherita.jpg'
        )
        
    def test_pizza_creation(self):
        """Pizza 모델 생성 테스트"""
        pizza = Pizza.objects.create(
            pizza_id='P001_S',
            pizza_type_id=self.pizza_type,
            size='Small',
            price=15000.0
        )
        
        self.assertEqual(pizza.pizza_id, 'P001_S')
        self.assertEqual(pizza.pizza_type_id, self.pizza_type)
        self.assertEqual(pizza.size, 'Small')
        self.assertEqual(pizza.price, 15000.0)
        
    def test_pizza_foreign_key_relationship(self):
        """Pizza와 PizzaType 간의 외래키 관계 테스트"""
        pizza = Pizza.objects.create(
            pizza_id='P001_S',
            pizza_type_id=self.pizza_type,
            size='Small',
            price=15000.0
        )
        
        # 외래키 관계 확인
        self.assertEqual(pizza.pizza_type_id.pizza_nm, '마르게리타')
        
    def test_pizza_cascade_delete(self):
        """PizzaType 삭제 시 Pizza CASCADE 삭제 테스트"""
        pizza = Pizza.objects.create(
            pizza_id='P001_S',
            pizza_type_id=self.pizza_type,
            size='Small',
            price=15000.0
        )
        
        # PizzaType 삭제
        self.pizza_type.delete()
        
        # Pizza도 함께 삭제되었는지 확인
        self.assertFalse(Pizza.objects.filter(pizza_id='P001_S').exists())
        
    def test_pizza_str_representation(self):
        """Pizza 모델 문자열 표현 테스트"""
        pizza = Pizza.objects.create(
            pizza_id='P001_S',
            pizza_type_id=self.pizza_type,
            size='Small',
            price=15000.0
        )
        
        # __str__ 메소드가 정의되지 않았으므로 기본 동작 확인
        self.assertIsNotNone(str(pizza))


class MenuIntegrationTestCase(TestCase):
    """Menu 앱 통합 테스트"""
    
    def setUp(self):
        """테스트 데이터 설정"""
        self.client = Client()
        
        # 다양한 피자 타입과 피자 생성
        pizza_types = [
            ('P001', '마르게리타', '클래식', 'https://example.com/margherita.jpg'),
            ('P002', '페퍼로니', '미트', 'https://example.com/pepperoni.jpg'),
            ('P003', '하와이안', '프리미엄', 'https://example.com/hawaiian.jpg'),
        ]
        
        for type_id, name, category, img_url in pizza_types:
            pizza_type = PizzaType.objects.create(
                pizza_type_id=type_id,
                pizza_nm=name,
                pizza_categ=category,
                pizza_img_url=img_url
            )
            
            # 각 타입별로 다양한 사이즈의 피자 생성
            sizes = ['Small', 'Medium', 'Large']
            base_prices = [15000, 20000, 25000]
            
            for i, (size, price) in enumerate(zip(sizes, base_prices)):
                Pizza.objects.create(
                    pizza_id=f'{type_id}_{size[0]}',
                    pizza_type_id=pizza_type,
                    size=size,
                    price=price
                )
        
    def test_complete_menu_workflow(self):
        """완전한 메뉴 워크플로우 테스트"""
        # 1. 피자 타입 목록 조회
        type_url = reverse('pizza_type_list')
        type_response = self.client.get(type_url)
        self.assertEqual(type_response.status_code, 200)
        types = type_response.json()
        self.assertEqual(len(types), 3)
        
        # 2. 피자 목록 조회
        pizza_url = reverse('pizza_list')
        pizza_response = self.client.get(pizza_url)
        self.assertEqual(pizza_response.status_code, 200)
        pizzas = pizza_response.json()
        self.assertEqual(len(pizzas), 9)  # 3개 타입 × 3개 사이즈
        
        # 3. 특정 피자의 ID 조회
        id_url = reverse('get_pizza_id')
        id_data = {'size': 'Medium', 'name': '페퍼로니'}
        id_response = self.client.post(id_url, id_data)
        self.assertEqual(id_response.status_code, 200)
        pizza_id = id_response.json()['pizza_id']
        self.assertEqual(pizza_id, 'P002_M')
        
    def test_menu_data_consistency(self):
        """메뉴 데이터 일관성 테스트"""
        # 피자 타입과 피자 간의 관계 일관성 확인
        pizza_types = PizzaType.objects.all()
        pizzas = Pizza.objects.all()
        
        # 모든 피자가 유효한 피자 타입을 참조하는지 확인
        for pizza in pizzas:
            # pizza.pizza_type_id는 객체, pizza.pizza_type_id_id는 FK의 원시 ID
            self.assertTrue(PizzaType.objects.filter(pk=pizza.pizza_type_id_id).exists())
            
        # 각 피자 타입에 해당하는 피자가 존재하는지 확인
        for pizza_type in pizza_types:
            self.assertTrue(Pizza.objects.filter(pizza_type_id=pizza_type).exists())
