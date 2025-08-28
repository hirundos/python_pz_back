from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Member
from django.db import models
from django.db.models import F
import jwt
import datetime
from django.conf import settings

## TODO 비밀번호 해싱

@csrf_exempt
def login_check(request):
    if request.method == 'POST':
        member_id = str(request.POST.get('id', ''))
        member_pw = str(request.POST.get('pw', ''))

        try:
            user = Member.objects.get(member_id=member_id, member_pwd=member_pw)
            # JWT 생성
            payload = {
                'id': member_id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
                'iat': datetime.datetime.utcnow()
            }
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
            return JsonResponse({'count': 1, 'token': token})
        except Member.DoesNotExist:
            return JsonResponse({'count': 0})
    else:
        return JsonResponse({'error': 'POST method required'}, status=405)


@csrf_exempt
def logout_view(request):
    if request.method == 'POST':
        # JWT는 서버에서 무효화하지 않으므로, 클라이언트에서 토큰 삭제 안내
        return JsonResponse({'message': 'Logged out. Session ended. Please remove token on client.'})
    else:
        return JsonResponse({'error': 'POST method required'}, status=405)


@csrf_exempt
def register_member(request):
    if request.method == 'POST':
        member_id = str(request.POST.get('id', ''))
        member_pw = str(request.POST.get('pw', ''))
        member_nm = str(request.POST.get('name', ''))

        if not member_id or not member_pw or not member_nm:
            return JsonResponse({'error': 'All fields are required.'}, status=400)

        # 이미 존재하는 아이디 체크
        if Member.objects.filter(member_id=member_id).exists():
            return JsonResponse({'error': 'ID already exists.'}, status=409)

        # 회원 생성
        Member.objects.create(member_id=member_id, member_pwd=member_pw, member_nm=member_nm)
        return JsonResponse({'message': 'Registration successful.'})
    else:
        return JsonResponse({'error': 'POST method required'}, status=405)

def verify_jwt_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload  # 유효하면 payload 반환
    except jwt.ExpiredSignatureError:
        return None  # 토큰 만료
    except jwt.InvalidTokenError:
        return None  # 유효하지 않은 토큰

# 인증이 필요한 API에서 아래와 같이 사용 예시:
# token = request.META.get('HTTP_AUTHORIZATION', '').split('Bearer ')[-1]
# payload = verify_jwt_token(token)
# if not payload:
#     return JsonResponse({'error': 'Invalid or expired token.'}, status=401)
# ...이후 인증된 사용자 로직...

