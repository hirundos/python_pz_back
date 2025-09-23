# 테스트 가이드

이 문서는 pizza_back 프로젝트의 테스트 실행 방법과 테스트 구조에 대해 설명합니다.

## 테스트 구조

### 1. Login App 테스트 (`pizza_back/login/tests.py`)
- **LoginTestCase**: 로그인, 회원가입, 로그아웃 기능 테스트
- **MemberModelTestCase**: Member 모델 테스트
- **JWTTestCase**: JWT 토큰 생성 및 검증 테스트

### 2. Menu App 테스트 (`pizza_back/menu/tests.py`)
- **MenuTestCase**: 피자 목록, 피자 종류, 피자 ID 조회 테스트
- **PizzaTypeModelTestCase**: PizzaType 모델 테스트
- **PizzaModelTestCase**: Pizza 모델 테스트
- **MenuIntegrationTestCase**: 메뉴 앱 통합 테스트

### 3. Order App 테스트 (`pizza_back/order/tests.py`)
- **OrderTestCase**: 주문 생성, 주문 내역 조회, 지점 조회 테스트
- **OrderModelTestCase**: Order 모델 테스트
- **OrderDetailModelTestCase**: OrderDetail 모델 테스트
- **BranchModelTestCase**: Branch 모델 테스트
- **CustomJWTAuthenticationTestCase**: JWT 인증 테스트
- **OrderIntegrationTestCase**: 주문 앱 통합 테스트

## 테스트 실행 방법

### 1. 기본 테스트 실행

```bash
# 모든 테스트 실행
python manage.py test

# 특정 앱 테스트 실행
python manage.py test pizza_back.login
python manage.py test pizza_back.menu
python manage.py test pizza_back.order

# 특정 테스트 클래스 실행
python manage.py test pizza_back.login.tests.LoginTestCase

# 특정 테스트 메소드 실행
python manage.py test pizza_back.login.tests.LoginTestCase.test_login_check_success
```

### 2. 테스트 실행 스크립트 사용

```bash
# 모든 테스트 실행
python run_tests.py

# 특정 앱 테스트 실행
python run_tests.py --app login
python run_tests.py --app menu
python run_tests.py --app order

# 특정 테스트 실행
python run_tests.py --test pizza_back.login.tests.LoginTestCase.test_login_check_success

# 커버리지 리포트 생성
python run_tests.py --coverage

# 의존성 확인
python run_tests.py --check-deps
```

### 3. 커버리지 리포트 생성

```bash
# 커버리지 데이터 수집
coverage run --source='.' manage.py test

# 텍스트 리포트 생성
coverage report

# HTML 리포트 생성
coverage html
```

## 테스트 데이터

각 테스트는 `setUp()` 메소드에서 필요한 테스트 데이터를 생성합니다:

- **사용자 데이터**: 테스트용 Member 객체
- **피자 데이터**: PizzaType과 Pizza 객체
- **지점 데이터**: Branch 객체
- **주문 데이터**: Order와 OrderDetail 객체

## 모킹(Mocking)

외부 API 호출이 필요한 테스트는 `unittest.mock`을 사용하여 모킹합니다:

```python
@patch('requests.post')
def test_order_creation_success(self, mock_post):
    # 외부 API 응답 모킹
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'pizza_id': 'P001_S'}
    mock_post.return_value = mock_response
```

## 테스트 실행 전 준비사항

### 1. 의존성 설치

```bash
# 기본 의존성
pip install -r requirements.txt

# 테스트 의존성 (선택사항)
pip install -r requirements-test.txt
```

### 2. 데이터베이스 설정

테스트는 별도의 테스트 데이터베이스를 사용합니다. Django가 자동으로 테스트용 데이터베이스를 생성하고 삭제합니다.

### 3. 환경 변수 설정

테스트 실행 시 다음 환경 변수가 필요할 수 있습니다:

```bash
export DJANGO_SETTINGS_MODULE=pizza_back.settings
export SECRET_KEY=your-secret-key
```

## 테스트 결과 해석

### 성공적인 테스트 실행 예시

```
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
...........
----------------------------------------------------------------------
Ran 11 tests in 0.123s

OK
Destroying test database for alias 'default'...
```

### 실패한 테스트 예시

```
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
F..........
======================================================================
FAIL: test_login_check_success (pizza_back.login.tests.LoginTestCase)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/path/to/test.py", line 45, in test_login_check_success
    self.assertEqual(response.status_code, 200)
AssertionError: 400 != 200

----------------------------------------------------------------------
Ran 11 tests in 0.123s

FAILED (failures=1)
Destroying test database for alias 'default'...
```

## 문제 해결

### 1. 데이터베이스 연결 오류

```
django.db.utils.OperationalError: could not connect to server
```

**해결 방법**: PostgreSQL 서버가 실행 중인지 확인하고, `settings.py`의 데이터베이스 설정을 확인하세요.

### 2. 모듈 임포트 오류

```
ModuleNotFoundError: No module named 'pizza_back.login'
```

**해결 방법**: 프로젝트 루트 디렉토리에서 테스트를 실행하고, `PYTHONPATH`가 올바르게 설정되었는지 확인하세요.

### 3. JWT 토큰 오류

```
jwt.exceptions.InvalidTokenError: Invalid token
```

**해결 방법**: `settings.py`의 `SECRET_KEY`가 올바르게 설정되었는지 확인하세요.

## 지속적 통합(CI) 설정

GitHub Actions를 사용한 CI 설정 예시:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run tests
      run: python run_tests.py --coverage
      env:
        DATABASE_URL: postgres://postgres:postgres@localhost:5432/test_db
```

## 추가 리소스

- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Django REST Framework Testing](https://www.django-rest-framework.org/api-guide/testing/)
- [Python unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
