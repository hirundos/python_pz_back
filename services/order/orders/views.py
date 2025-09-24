import jwt
import requests
import os
from django.conf import settings
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .models import Order, OrderDetail, Branch


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return JsonResponse({"status": "ok"})


def _get_member_id_from_auth(request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload.get("member_id")
    except Exception:
        return None


class MyOrderView(APIView):
    def get(self, request):
        member_id = _get_member_id_from_auth(request)
        if not member_id:
            return JsonResponse({"detail": "unauthorized"}, status=401)
        items = [
            {
                "order_id": o.order_id,
                "bran_id": o.bran_id,
                "date": o.date,
                "time": o.time,
            }
            for o in Order.objects.filter(member_id=member_id)
        ]
        return JsonResponse(items, safe=False)


class CreateOrderView(APIView):
    def post(self, request):
        member_id = _get_member_id_from_auth(request)
        if not member_id:
            return JsonResponse({"detail": "unauthorized"}, status=401)
        bran_id = request.data.get("bran_id")
        date = request.data.get("date")
        time = request.data.get("time")
        items = request.data.get("items", [])
        if not (bran_id and date and time and isinstance(items, list)):
            return JsonResponse({"detail": "invalid payload"}, status=400)

        # 주문 ID 생성 (실제로는 UUID나 다른 방식으로 생성해야 함)
        import uuid
        order_id = f"ORDER_{uuid.uuid4().hex[:10]}"

        # Menu API에서 피자 ID 검증
        menu_service_url = os.getenv('MENU_SERVICE_URL', 'http://localhost:8002')
        for item in items:
            pizza_name = item.get("pizza_id")  # 피자 이름
            try:
                response = requests.post(
                    f"{menu_service_url}/api/menu/get_pizza_id/",
                    json={"pizza_nm": pizza_name, "size": "L"},
                    timeout=5
                )
                if response.status_code != 200:
                    return JsonResponse({"detail": f"피자 '{pizza_name}'을 찾을 수 없습니다."}, status=400)
            except requests.RequestException:
                return JsonResponse({"detail": "메뉴 서비스 연결 실패"}, status=503)

        order = Order.objects.create(order_id=order_id, member_id=member_id, bran_id=bran_id, date=date, time=time)
        for item in items:
            OrderDetail.objects.create(
                order=order,
                pizza_id=item["pizza_id"],
                quantity=item["quantity"]
            )
        return JsonResponse({"order_id": order_id}, status=201)


class BranchListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        items = [{"bran_id": b.bran_id, "bran_nm": b.bran_nm} for b in Branch.objects.all()]
        return JsonResponse(items, safe=False)


