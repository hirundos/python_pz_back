from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .models import PizzaType, Pizza


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return JsonResponse({"status": "ok"})

class PizzaListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        pizzas = Pizza.objects.select_related('pizza_type').all() 
        items = [
            {
                "pizza_id": p.pizza_id,
                "pizza_type__pizza_nm": p.pizza_type.pizza_nm, 
                "size": p.size,
                "price": p.price,
            }
            for p in pizzas
        ]
        return JsonResponse(items, safe=False)

class PizzaTypesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        items = [
            {
                "pizza_type_id": t.pizza_type_id,
                "pizza_nm": t.pizza_nm,
                "pizza_categ": t.pizza_categ,
                "pizza_img_url": t.pizza_img_url,
            }
            for t in PizzaType.objects.all()
        ]
        return JsonResponse(items, safe=False)


class GetPizzaIdView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        name = request.data.get("pizza_nm")
        size = request.data.get("size")
        try:
            pizza_type = PizzaType.objects.get(pizza_nm=name)
            pizza = Pizza.objects.get(pizza_type=pizza_type, size=size)
            return JsonResponse({"pizza_id": pizza.pizza_id})
        except (PizzaType.DoesNotExist, Pizza.DoesNotExist):
            return JsonResponse({"detail": "not found"}, status=404)


