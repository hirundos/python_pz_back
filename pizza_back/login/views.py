from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Member
from django.db import models
from django.db.models import F
import jwt
import datetime
import json
from django.conf import settings

## TODO 비밀번호 해싱

@csrf_exempt
def login_check(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8')) if request.body else {}
    except json.JSONDecodeError:
        data = {}

    member_id = str(data.get('id') or request.POST.get('id', ''))
    member_pw = str(data.get('pw') or request.POST.get('pw', ''))

    if not member_id or not member_pw:
        return JsonResponse({'count': 0, 'error': 'credentials required'}, status=400)

    try:
        user = Member.objects.get(member_id=member_id, member_pwd=member_pw)
    except Member.DoesNotExist:
        return JsonResponse({'count': 0})

    payload = {
        'member_id': member_id, 
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        'iat': datetime.datetime.utcnow()
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    return JsonResponse({'count': 1, 'token': token})

@csrf_exempt
def logout_view(request):
    if request.method == 'GET':
        # JWT는 서버에서 무효화하지 않으므로, 클라이언트에서 토큰 삭제 안내
        return JsonResponse({'message': 'Logged out. Session ended. Please remove token on client.'})
    else:
        return JsonResponse({'error': 'POST method required'}, status=405)

@csrf_exempt
def register_member(request):
    if request.method == 'POST':
        try:
            # request.body에서 JSON 데이터 읽기 및 파싱
            data = json.loads(request.body.decode('utf-8'))
            member_id = data.get('id', '')
            member_pw = data.get('pw', '')
            member_nm = data.get('name', '')

        except json.JSONDecodeError:
            # JSON 파싱 오류 처리
            return JsonResponse({'error': 'Invalid JSON format.'}, status=400)

        if not member_id or not member_pw or not member_nm:
            return JsonResponse({'error': 'All fields are required.'}, status=400)

        # 이미 존재하는 아이디 체크
        if Member.objects.filter(member_id=member_id).exists():
            return JsonResponse({'error': 'ID already exists.'}, status=409)

        # 회원 생성
        Member.objects.create(member_id=member_id, member_pwd=member_pw, member_nm=member_nm)
        return JsonResponse({'message': 'Registration successful.'})

    else:
        # POST 메소드가 아닐 경우 오류 응답
        return JsonResponse({'error': 'POST method required'}, status=405)

def verify_jwt_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload 
    except jwt.ExpiredSignatureError:
        return None  # 토큰 만료
    except jwt.InvalidTokenError:
        return None  # 유효하지 않은 토큰
