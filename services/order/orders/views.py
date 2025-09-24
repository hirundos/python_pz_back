import jwt
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
        order_id = request.data.get("order_id")
        date = request.data.get("date")
        time = request.data.get("time")
        details = request.data.get("details", [])
        if not (order_id and bran_id and date and time and isinstance(details, list)):
            return JsonResponse({"detail": "invalid payload"}, status=400)
        Order.objects.create(order_id=order_id, member_id=member_id, bran_id=bran_id, date=date, time=time)
        for d in details:
            OrderDetail.objects.create(order_detail_id=d["order_detail_id"], order_id=order_id, pizza_id=d["pizza_id"], quantity=d["quantity"]) 
        return JsonResponse({"order_id": order_id}, status=201)


class BranchListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        items = [{"bran_id": b.bran_id, "bran_nm": b.bran_nm} for b in Branch.objects.all()]
        return JsonResponse(items, safe=False)


