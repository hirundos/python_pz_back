#!/bin/bash

# Pizza MSA 통합 테스트 실행 스크립트

set -e  # 에러 발생 시 스크립트 중단

echo "🍕 Pizza MSA 통합 테스트 시작"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 프로젝트 루트 디렉토리로 이동
cd "$(dirname "$0")/.."

echo -e "${YELLOW}1. 환경 확인${NC}"
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ docker-compose가 설치되지 않았습니다.${NC}"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ python3가 설치되지 않았습니다.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 환경 확인 완료${NC}"

echo -e "${YELLOW}2. 테스트 환경 구축${NC}"
# 기존 테스트 컨테이너 정리
echo "기존 테스트 컨테이너 정리 중..."
docker-compose -f docker-compose.test.yml down -v || true

# 테스트 환경 구축
echo "테스트 환경 구축 중..."
docker-compose -f docker-compose.test.yml up -d test-db test-redis

# 데이터베이스가 준비될 때까지 대기
echo "데이터베이스 준비 대기 중..."
sleep 10

# 데이터베이스 헬스체크
if ! docker-compose -f docker-compose.test.yml exec -T test-db pg_isready -U test_user -d pizza_test > /dev/null 2>&1; then
    echo -e "${RED}❌ 데이터베이스 연결 실패${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 테스트 환경 구축 완료${NC}"

echo -e "${YELLOW}3. 단위 테스트 실행${NC}"
# 각 서비스별 단위 테스트 실행
echo "Login Service 단위 테스트 실행 중..."
docker-compose -f docker-compose.test.yml run --rm login-service-test

echo "Menu Service 단위 테스트 실행 중..."
docker-compose -f docker-compose.test.yml run --rm menu-service-test

echo "Order Service 단위 테스트 실행 중..."
docker-compose -f docker-compose.test.yml run --rm order-service-test

echo -e "${GREEN}✅ 단위 테스트 완료${NC}"

echo -e "${YELLOW}4. 통합 테스트 실행${NC}"
# 통합 테스트 실행
echo "통합 테스트 실행 중..."
if docker-compose -f docker-compose.test.yml run --rm integration-test-runner; then
    echo -e "${GREEN}✅ 통합 테스트 통과${NC}"
else
    echo -e "${RED}❌ 통합 테스트 실패${NC}"
    exit 1
fi

echo -e "${YELLOW}5. 테스트 결과 수집${NC}"
# 테스트 결과 디렉토리 생성
mkdir -p test-results

# 테스트 결과 파일들을 수집
if [ -f "test-results/integration_test_results.json" ]; then
    echo -e "${GREEN}✅ 테스트 결과 수집 완료${NC}"
    echo "📊 테스트 결과를 확인하려면 test-results/integration_test_results.json 파일을 확인하세요."
else
    echo -e "${YELLOW}⚠️  테스트 결과 파일이 생성되지 않았습니다.${NC}"
fi

echo -e "${YELLOW}6. 정리${NC}"
# 테스트 환경 정리
echo "테스트 환경 정리 중..."
docker-compose -f docker-compose.test.yml down -v

# 불필요한 로그 파일 정리
find . -name "*.log" -type f -delete

echo -e "${GREEN}✅ 테스트 환경 정리 완료${NC}"

echo -e "${GREEN}🎉 Pizza MSA 통합 테스트 완료!${NC}"

# 테스트 실행 시간 출력
END_TIME=$(date +%s)
if [ -f ".test_start_time" ]; then
    START_TIME=$(cat .test_start_time)
    DURATION=$((END_TIME - START_TIME))
    echo -e "${YELLOW}⏱️  총 테스트 실행 시간: ${DURATION}초${NC}"
    rm .test_start_time
fi
