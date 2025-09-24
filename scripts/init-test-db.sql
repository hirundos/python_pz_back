-- 테스트 데이터베이스 초기화 스크립트

-- 테스트용 스키마 생성
CREATE SCHEMA IF NOT EXISTS pizza_test;

-- 테스트 데이터 시딩

-- 1. 테스트 사용자 생성
INSERT INTO pizza_test.member (member_id, member_pwd, member_nm)
VALUES
    ('test_user', 'hashed_password_123', '테스트사용자'),
    ('integration_test_user', 'test_password123', '통합테스트사용자')
ON CONFLICT (member_id) DO NOTHING;

-- 2. 테스트 피자 타입 생성
INSERT INTO pizza_test.pizza_types (pizza_type_id, pizza_nm, pizza_categ, pizza_img_url)
VALUES
    ('PT001', '페페로니', '클래식', 'http://example.com/pepperoni.jpg'),
    ('PT002', '치즈', '클래식', 'http://example.com/cheese.jpg'),
    ('PT003', '불고기', '프리미엄', 'http://example.com/bulgogi.jpg')
ON CONFLICT (pizza_type_id) DO NOTHING;

-- 3. 테스트 피자 생성
INSERT INTO pizza_test.pizza (pizza_id, pizza_type_id, size, price)
VALUES
    ('PIZZA_001_L', 'PT001', 'L', 25000.00),
    ('PIZZA_001_M', 'PT001', 'M', 20000.00),
    ('PIZZA_002_L', 'PT002', 'L', 23000.00),
    ('PIZZA_002_M', 'PT002', 'M', 18000.00),
    ('PIZZA_003_L', 'PT003', 'L', 28000.00),
    ('PIZZA_003_M', 'PT003', 'M', 23000.00)
ON CONFLICT (pizza_id) DO NOTHING;

-- 4. 테스트 지점 생성
INSERT INTO pizza_test.branch (bran_id, bran_nm)
VALUES
    ('BRANCH001', '강남점'),
    ('BRANCH002', '홍대점'),
    ('BRANCH003', '신촌점')
ON CONFLICT (bran_id) DO NOTHING;

-- 5. 테스트 주문 생성 (통합 테스트용)
INSERT INTO pizza_test.orders (order_id, member_id, bran_id, date, time)
VALUES
    ('ORDER_TEST_001', 'test_user', 'BRANCH001', '2024-01-15', '14:30:00')
ON CONFLICT (order_id) DO NOTHING;

-- 6. 테스트 주문 상세 생성
INSERT INTO pizza_test.order_detail (order_detail_id, order_id, pizza_id, quantity)
VALUES
    (1, 'ORDER_TEST_001', 'PIZZA_001_L', 2)
ON CONFLICT (order_detail_id) DO NOTHING;

-- 인덱스 생성 (성능 최적화)
CREATE INDEX IF NOT EXISTS idx_member_member_id ON pizza_test.member(member_id);
CREATE INDEX IF NOT EXISTS idx_pizza_type_id ON pizza_test.pizza(pizza_type_id);
CREATE INDEX IF NOT EXISTS idx_orders_member_id ON pizza_test.orders(member_id);
CREATE INDEX IF NOT EXISTS idx_order_detail_order_id ON pizza_test.order_detail(order_id);
