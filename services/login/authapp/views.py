import datetime
import jwt
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .models import Member


def _issue_token(member_id: str) -> str:
    now = datetime.datetime.utcnow()
    payload = {
        "member_id": member_id,
        "iat": now,
        "exp": now + datetime.timedelta(seconds=settings.JWT_ACCESS_TTL_SECONDS),
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return JsonResponse({"status": "ok"})


@method_decorator(csrf_exempt, name="dispatch")
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data or {}
        member_id = data.get("member_id")
        password = data.get("password")
        member_nm = data.get("member_nm")
        if not member_id or not password or not member_nm:
            return JsonResponse({"detail": "missing fields"}, status=400)
        if Member.objects.filter(member_id=member_id).exists():
            return JsonResponse({"detail": "duplicate member_id"}, status=400)
        Member.objects.create(
            member_id=member_id,
            member_pwd=make_password(password),
            member_nm=member_nm,
        )
        return JsonResponse({"member_id": member_id})


@method_decorator(csrf_exempt, name="dispatch")
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data or {}
        member_id = data.get("member_id")
        password = data.get("password")
        try:
            m = Member.objects.get(member_id=member_id)
        except Member.DoesNotExist:
            return JsonResponse({"detail": "invalid credentials"}, status=401)
        if not check_password(password, m.member_pwd):
            return JsonResponse({"detail": "invalid credentials"}, status=401)
        token = _issue_token(member_id)
        return JsonResponse({"token": token})


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Stateless JWT: no server-side action.
        return JsonResponse({"status": "logged out"})


@method_decorator(csrf_exempt, name="dispatch")
class VerifyTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data or {}
        token = data.get("token")
        if not token:
            return JsonResponse({"valid": False}, status=400)
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            return JsonResponse({"valid": True, "member_id": payload.get("member_id")})
        except jwt.ExpiredSignatureError:
            return JsonResponse({"valid": False, "reason": "expired"}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({"valid": False, "reason": "invalid"}, status=401)


