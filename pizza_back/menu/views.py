# filepath: pizza_back/menu/views.py
from django.http import JsonResponse
from django.db import models
from django.db.models import F
from .models import Pizza, PizzaType
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

def pizza_list(request):
    pizzas = Pizza.objects.select_related('pizza_type').values(
        'pizza_type__pizza_categ', 
        'pizza_type__pizza_nm', 
        'size', 
        'price', 
    )
    return JsonResponse(list(pizzas), safe=False)

def pizza_type_list(request):
    pizza_types = PizzaType.objects.values(
        'pizza_nm',
        'pizza_img_url'
    )
    return JsonResponse(list(pizza_types), safe=False)

@csrf_exempt
@require_POST
def get_pizza_id(request):
    size = request.POST.get('size')
    name = request.POST.get('name')
    if not size or not name:
        return JsonResponse({'error': 'size and name required'}, status=400)
    try:
        pizza_type = PizzaType.objects.get(pizza_nm=name)
        pizza = Pizza.objects.get(size=size, pizza_type=pizza_type)
        return JsonResponse({'pizza_id': pizza.pizza_id})
    except (PizzaType.DoesNotExist, Pizza.DoesNotExist):
        return JsonResponse({'error': 'No pizza found for given size and name'}, status=404)

