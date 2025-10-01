# Pizza MSA Backend 🏗️

Kubernetes 환경에서 실행되는 마이크로서비스 아키텍처 기반 피자 주문 시스템

## 🏛️ 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Login Service │    │   Menu Service  │    │  Order Service  │
│   (사용자 인증)  │◄──►│  (메뉴 관리)     │◄──►│  (주문 처리)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    │   (공유 DB)      │
                    └─────────────────┘
```

### 서비스 구성

| 서비스 | 포트 | 설명 |
|--------|------|------|
| Login Service | 8001 | 사용자 인증 및 JWT 토큰 관리 |
| Menu Service | 8002 | 피자 메뉴 및 타입 관리 |
| Order Service | 8003 | 주문 생성 및 관리 |
| PostgreSQL | 5432 | 공유 데이터베이스 |

## 🚀 빠른 시작

### 1. 사전 요구사항

- Docker & Docker Compose
- Python 3.11+
- PostgreSQL 13+

### 2. 환경 설정

```bash
# 리포지토리 클론
git clone <repository-url>
cd python_back_pizza

# 환경 변수 설정
cp .env.example .env
# .env 파일에 실제 값들을 설정
```

### 3. 서비스 시작

```bash
# 전체 서비스 시작
docker-compose up -d

# 또는 개발 환경에서 개별 서비스 시작
cd services/login && python manage.py runserver 0.0.0.0:8001
cd services/menu && python manage.py runserver 0.0.0.0:8002
cd services/order && python manage.py runserver 0.0.0.0:8003
```

## 🧪 테스트 실행

### 개요

MSA 환경에 최적화된 포괄적인 테스트 전략을 제공합니다:

- **단위 테스트**: 각 서비스 내부 로직 테스트
- **통합 테스트**: 서비스 간 상호작용 테스트
- **계약 테스트**: API 계약 준수 여부 테스트
- **성능 테스트**: 서비스 응답 시간 및 처리량 테스트

### 테스트 실행 방법

#### 1. 전체 테스트 실행 (권장)

```bash
# 통합 테스트 실행 스크립트 사용
./scripts/run_all_tests.sh
```

#### 2. 개별 서비스 테스트

```bash
# Login Service 테스트
cd services/login
python manage.py test authapp.tests --verbosity=2

# Menu Service 테스트
cd services/menu
python manage.py test catalog.tests --verbosity=2

# Order Service 테스트
cd services/order
python manage.py test orders.tests --verbosity=2
```

#### 3. Docker Compose를 사용한 테스트

```bash
# 테스트 환경 구축 및 단위 테스트 실행
docker-compose -f docker-compose.test.yml up login-service-test
docker-compose -f docker-compose.test.yml up menu-service-test
docker-compose -f docker-compose.test.yml up order-service-test

# 통합 테스트 실행
docker-compose -f docker-compose.test.yml up integration-test-runner
```

#### 4. 커버리지 리포트 생성

```bash
# 각 서비스별 커버리지 확인
cd services/login
coverage run --source='.' manage.py test
coverage report
coverage html

cd services/menu
coverage run --source='.' manage.py test
coverage report
coverage html

cd services/order
coverage run --source='.' manage.py test
coverage report
coverage html
```

### 테스트 구성 요소

#### 1. 단위 테스트

각 서비스의 모델, 뷰, 유틸리티 함수를 독립적으로 테스트:

- **Login Service**: Member 모델, JWT 인증 로직
- **Menu Service**: Pizza, PizzaType 모델, 메뉴 API
- **Order Service**: Order, OrderDetail, Branch 모델, 트랜잭션 로직

#### 2. 통합 테스트

서비스 간 상호작용을 검증하는 시나리오 기반 테스트:

- **사용자 플로우**: 회원가입 → 로그인 → 메뉴 조회 → 주문 → 주문확인
- **서비스 연계**: JWT 토큰 기반 서비스 간 인증
- **데이터 일관성**: 트랜잭션 롤백 및 데이터 무결성 검증

#### 3. 테스트 인프라

- **테스트 데이터베이스**: 독립적인 PostgreSQL 인스턴스
- **테스트 데이터 팩토리**: 리얼한 테스트 데이터 자동 생성
- **API 클라이언트**: 서비스 간 HTTP 통신을 위한 공통 클라이언트

### 테스트 데이터

테스트용 샘플 데이터가 `scripts/init-test-db.sql`에 정의되어 있습니다:

```sql
-- 테스트 사용자
INSERT INTO pizza_test.member (member_id, member_pwd, member_nm)
VALUES ('test_user', 'hashed_password_123', '테스트사용자');

-- 테스트 피자 메뉴
INSERT INTO pizza_test.pizza_types (pizza_type_id, pizza_nm, pizza_categ, pizza_img_url)
VALUES ('PT001', '페페로니', '클래식', 'http://example.com/pepperoni.jpg');
```

### CI/CD 파이프라인

GitHub Actions를 통한 자동화된 테스트:

```yaml
# .github/workflows/test.yml
name: MSA Tests
on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run All Tests
        run: ./scripts/run_all_tests.sh
```

### 테스트 결과

테스트 실행 후 결과는 `test-results/integration_test_results.json`에 저장됩니다:

```json
{
  "passed": 5,
  "failed": 1,
  "total": 6,
  "details": [
    {
      "test_name": "user_registration_login",
      "passed": true,
      "message": "사용자 등록/로그인 성공",
      "timestamp": 1640995200
    }
  ]
}
```

## 📁 프로젝트 구조

```
python_back_pizza/
├── services/                    # 마이크로서비스
│   ├── login/                  # 로그인 서비스
│   │   ├── authapp/
│   │   │   ├── models.py       # 사용자 모델
│   │   │   ├── views.py        # 인증 뷰
│   │   │   ├── urls.py         # URL 라우팅
│   │   │   └── tests.py        # 테스트 코드
│   │   └── login_service/      # Django 프로젝트 설정
│   ├── menu/                   # 메뉴 서비스
│   │   ├── catalog/
│   │   │   ├── models.py       # 피자 모델
│   │   │   ├── views.py        # 메뉴 뷰
│   │   │   ├── urls.py         # URL 라우팅
│   │   │   └── tests.py        # 테스트 코드
│   │   └── menu_service/       # Django 프로젝트 설정
│   └── order/                  # 주문 서비스
│       ├── orders/
│       │   ├── models.py       # 주문 모델
│       │   ├── views.py        # 주문 뷰
│       │   ├── urls.py         # URL 라우팅
│       │   └── tests.py        # 테스트 코드
│       └── order_service/      # Django 프로젝트 설정
├── scripts/                    # 테스트 및 유틸리티 스크립트
│   ├── run_all_tests.sh       # 전체 테스트 실행
│   ├── run_integration_tests.py # 통합 테스트
│   └── init-test-db.sql       # 테스트 DB 초기화
├── docker-compose.test.yml    # 테스트 환경 Docker Compose
├── Dockerfile.test-runner     # 통합 테스트 Docker 이미지
├── requirements-test.txt      # 테스트 의존성
└── docs/                      # 문서
    ├── v0.md                  # 시스템 설계 문서
    └── TEST_GUIDE.md         # 테스트 가이드
```

## 🔧 개발 가이드

### 새로운 기능 추가

1. 해당 서비스 디렉토리로 이동
2. 모델/뷰/URL 업데이트
3. 테스트 코드 작성
4. 통합 테스트 시나리오 추가

### 서비스 간 통신

```python
# 다른 서비스 호출 예시
import requests

def call_menu_service(pizza_name: str, size: str):
    response = requests.post(
        'http://menu-service:8000/api/menu/get_pizza_id/',
        json={'pizza_nm': pizza_name, 'size': size}
    )
    return response.json()
```

### 데이터베이스 설계

- 각 서비스는 독립적인 테이블 사용
- 외래키는 최소한으로 사용 (서비스 간 결합도 낮춤)
- 데이터 정합성은 애플리케이션 레벨에서 관리

## 📊 모니터링 및 로깅

- 각 서비스별 헬스체크 엔드포인트 제공
- 구조화된 로깅 (JSON 형식)
- 분산 추적을 위한 Correlation ID 사용

