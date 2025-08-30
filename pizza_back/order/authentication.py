from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import jwt
from django.conf import settings
from django.apps import apps

class CustomJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ')[1]

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            member_id = payload.get('member_id')

            if not member_id:
                raise AuthenticationFailed('Invalid token')

            from pizza_back.login.models import Member

            user = Member.objects.get(member_id=member_id)
            return (user, token)

        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token')
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expired')
        except Member.DoesNotExist:
            raise AuthenticationFailed('User not found')