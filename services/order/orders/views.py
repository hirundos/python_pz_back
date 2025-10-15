import jwt
import requests
import os
from django.conf import settings
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .models import Order, OrderDetail, Branch
import datetime 
from django.db.models import Max

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
                "pizza_id": o.pizza_id,
                "quantity": o.quantity,
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
        
        data = request.data or {}
        
        bran_id = data.get("branchId")
        items = data.get("lines", []) 

        now = datetime.datetime.now()
        date = now.strftime("%Y-%m-%d") 
        time = now.strftime("%H:%M:%S")
        
        # 필수 필드 검사: bran_id와 items 목록만 확인
        if not (bran_id and isinstance(items, list) and len(items) > 0):
            return JsonResponse({"detail": "invalid payload"}, status=400)

        menu_service_url = os.getenv('MENU_SERVICE_URL', 'http://menu-service.default.svc.cluster.local:8000')
        processed_items = [] 
        
        for item in items:
            pizza_name = item.get("name") 
            size = item.get("size")
            quantity = item.get("quantity")
            
            if not (pizza_name and size and quantity):
                 return JsonResponse({"detail": "missing item details"}, status=400)

            try:
                response = requests.post(
                    f"{menu_service_url}/api/menu/get_pizza_id/",
                    json={"pizza_nm": pizza_name, "size": size},
                    timeout=5
                )
                
                if response.status_code != 200:
                    return JsonResponse({"detail": f"피자 '{pizza_name}'을 찾을 수 없습니다."}, status=400)
                
                pizza_id = response.json().get("pizza_id") 
                
                processed_items.append({
                    "pizza_id": pizza_id,
                    "quantity": quantity
                })
                
            except requests.RequestException:
                return JsonResponse({"detail": "메뉴 서비스 연결 실패"}, status=503)

        # DB에 주문 정보 저장
        order = Order.objects.create(member_id=member_id, bran_id=bran_id, date=date, time=time)
        
        # DB에 주문 상세 정보 저장
        for item in processed_items: 
            OrderDetail.objects.create(
                order=order,
                pizza_id=item["pizza_id"],
                quantity=item["quantity"]
            )
            
        return JsonResponse({"order_id": order.order_id}, status=201)

class BranchListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        items = [{"bran_id": b.bran_id, "bran_nm": b.bran_nm} for b in Branch.objects.all()]
        return JsonResponse(items, safe=False)


