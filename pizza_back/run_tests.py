#!/usr/bin/env python
"""
테스트 실행 스크립트
이 스크립트는 pizza_back 프로젝트의 모든 테스트를 실행하고 결과를 보고합니다.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, description):
    """명령어를 실행하고 결과를 반환합니다."""
    print(f"\n{'='*60}")
    print(f"실행 중: {description}")
    print(f"명령어: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
            
        return result.returncode == 0, result.stdout, result.stderr
        
    except Exception as e:
        print(f"명령어 실행 중 오류 발생: {e}")
        return False, "", str(e)


def check_dependencies():
    """필요한 의존성이 설치되어 있는지 확인합니다."""
    print("의존성 확인 중...")
    
    required_packages = [
        'django',
        'djangorestframework',
        'djangorestframework-simplejwt',
        'django-cors-headers',
        'psycopg2-binary',
        'PyJWT'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"누락된 패키지: {', '.join(missing_packages)}")
        print("다음 명령어로 설치하세요:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("모든 의존성이 설치되어 있습니다.")
    return True


def run_all_tests():
    """모든 테스트를 실행합니다."""
    print("전체 테스트 실행 중...")
    
    success, stdout, stderr = run_command(
        "python manage.py test --verbosity=2",
        "전체 테스트 실행"
    )
    
    if success:
        print("\n✅ 모든 테스트가 성공적으로 완료되었습니다!")
    else:
        print("\n❌ 일부 테스트가 실패했습니다.")
        if stderr:
            print(f"오류: {stderr}")
    
    return success


def run_app_tests(app_name):
    """특정 앱의 테스트를 실행합니다."""
    print(f"{app_name} 앱 테스트 실행 중...")
    
    success, stdout, stderr = run_command(
        f"python manage.py test pizza_back.{app_name} --verbosity=2",
        f"{app_name} 앱 테스트 실행"
    )
    
    if success:
        print(f"\n✅ {app_name} 앱 테스트가 성공적으로 완료되었습니다!")
    else:
        print(f"\n❌ {app_name} 앱 테스트가 실패했습니다.")
        if stderr:
            print(f"오류: {stderr}")
    
    return success


def run_coverage_report():
    """테스트 커버리지 리포트를 생성합니다."""
    print("테스트 커버리지 리포트 생성 중...")
    
    # coverage 설치 확인
    try:
        import coverage
    except ImportError:
        print("coverage 패키지가 설치되지 않았습니다.")
        print("다음 명령어로 설치하세요: pip install coverage")
        return False
    
    # 커버리지 실행
    success, stdout, stderr = run_command(
        "coverage run --source='.' manage.py test",
        "커버리지 데이터 수집"
    )
    
    if not success:
        print("커버리지 데이터 수집에 실패했습니다.")
        return False
    
    # 텍스트 리포트 생성
    success, stdout, stderr = run_command(
        "coverage report",
        "텍스트 커버리지 리포트 생성"
    )
    
    if success:
        print("\n📊 커버리지 리포트:")
        print(stdout)
    
    # HTML 리포트 생성
    success, stdout, stderr = run_command(
        "coverage html",
        "HTML 커버리지 리포트 생성"
    )
    
    if success:
        print("\n📁 HTML 리포트가 htmlcov/ 디렉토리에 생성되었습니다.")
        print("브라우저에서 htmlcov/index.html을 열어보세요.")
    
    return success


def run_specific_test(test_path):
    """특정 테스트를 실행합니다."""
    print(f"특정 테스트 실행 중: {test_path}")
    
    success, stdout, stderr = run_command(
        f"python manage.py test {test_path} --verbosity=2",
        f"특정 테스트 실행: {test_path}"
    )
    
    if success:
        print(f"\n✅ 테스트가 성공적으로 완료되었습니다!")
    else:
        print(f"\n❌ 테스트가 실패했습니다.")
        if stderr:
            print(f"오류: {stderr}")
    
    return success


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description='Pizza Backend API 테스트 실행 스크립트',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python run_tests.py                    # 모든 테스트 실행
  python run_tests.py --app login       # login 앱 테스트만 실행
  python run_tests.py --app menu        # menu 앱 테스트만 실행
  python run_tests.py --app order       # order 앱 테스트만 실행
  python run_tests.py --coverage        # 커버리지 리포트 생성
  python run_tests.py --test pizza_back.login.tests.LoginTestCase.test_login_check_success
        """
    )
    
    parser.add_argument(
        '--app',
        choices=['login', 'menu', 'order'],
        help='특정 앱의 테스트만 실행'
    )
    
    parser.add_argument(
        '--test',
        help='특정 테스트 클래스나 메소드 실행'
    )
    
    parser.add_argument(
        '--coverage',
        action='store_true',
        help='테스트 커버리지 리포트 생성'
    )
    
    parser.add_argument(
        '--check-deps',
        action='store_true',
        help='의존성 확인만 수행'
    )
    
    args = parser.parse_args()
    
    print("🍕 Pizza Backend API 테스트 실행기")
    print("=" * 50)
    
    # 의존성 확인
    if not check_dependencies():
        sys.exit(1)
    
    if args.check_deps:
        print("의존성 확인이 완료되었습니다.")
        return
    
    # Django 설정 확인
    if not os.path.exists('manage.py'):
        print("❌ manage.py 파일을 찾을 수 없습니다.")
        print("프로젝트 루트 디렉토리에서 실행하세요.")
        sys.exit(1)
    
    success = True
    
    try:
        if args.test:
            success = run_specific_test(args.test)
        elif args.app:
            success = run_app_tests(args.app)
        elif args.coverage:
            success = run_coverage_report()
        else:
            success = run_all_tests()
            
    except KeyboardInterrupt:
        print("\n\n⏹️ 테스트 실행이 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류가 발생했습니다: {e}")
        sys.exit(1)
    
    if success:
        print("\n🎉 모든 작업이 성공적으로 완료되었습니다!")
        sys.exit(0)
    else:
        print("\n💥 일부 작업이 실패했습니다.")
        sys.exit(1)


if __name__ == '__main__':
    main()
