from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from django.db.models import Max
from django.db import models
from django.db.models import F
from .models import Order, OrderDetail, Branch
from pizza_back.menu.models import Pizza
from .authentication import CustomJWTAuthentication
from django.conf import settings
from django.utils import timezone
import requests


@api_view(['GET'])
@authentication_classes([CustomJWTAuthentication])
def myorder_list(request):
    member_id = request.user.member_id 

    orders = (
        OrderDetail.objects
        .select_related('order')
        .filter(order__member_id=member_id)
        .values(
            'order__order_id',
            'pizza__pizza_id',
            'quantity',
            'order__date',
            'order__time'
        )
        .order_by('-order__date', '-order__time')
    )

    # 필드명 맞추기
    result = [
        {
            'order_id': o['order__order_id'],
            'pizza_id': o['pizza__pizza_id'],
            'quantity': o['quantity'],
            'date': o['order__date'],
            'time': o['order__time'],
        }
        for o in orders
    ]
    return Response(result)

@api_view(['POST'])
@authentication_classes([CustomJWTAuthentication])
@permission_classes([IsAuthenticated])
def order(request):
    data = request.data
    lines = data.get('lines', [])
    branch = data.get('branchId')
    member_id = request.user.member_id

    if not lines:
        return Response({'error': 'No items in order'}, status=400)

    if not branch:
        return Response({'error': 'Branch ID is required'}, status=400)

    today = timezone.now()
    pizza_date = today.strftime('%Y-%m-%d')
    pizza_time = today.strftime('%H:%M:%S')

    with transaction.atomic():
        # order_id 생성
        max_order = Order.objects.aggregate(max_id=Max('order_id'))
        order_id = (max_order['max_id'] or 0) + 1

        # 주문 생성 (한 번만)
        order_obj = Order.objects.create(
            order_id=order_id,
            date=pizza_date,
            time=pizza_time,
            member_id=member_id,
            bran_id=branch
        )

        for line in lines:
            size = line.get('size')
            name = line.get('name')
            quantity = line.get('quantity')

            # pizza_id를 menu app의 API로 조회
            try:
                menu_api_url = settings.API_URL + '/menu/get_pizza_id/'
                resp = requests.post(
                    menu_api_url, 
                    data={'size': size, 'name': name},
                )

                if resp.status_code != 200:
                    transaction.set_rollback(True)
                    return Response({'error': f'No pizza found for {size} {name}'}, status=400)
                pizza_id = resp.json().get('pizza_id')

                try:
                    pizza = Pizza.objects.get(pizza_id=pizza_id)
                except Pizza.DoesNotExist:
                    transaction.set_rollback(True)
                    return Response({
                        'error': f'Pizza with id {pizza_id} not found in database'
                    }, status=400)

            except requests.exceptions.RequestException as e:
                transaction.set_rollback(True)
                return Response({
                    'error': f'Failed to connect to menu service',
                    'detail': str(e)
                }, status=500)
            except Exception as e:
                transaction.set_rollback(True)
                return Response({
                    'error': f'Error processing pizza: {name} ({size})',
                    'detail': str(e)
                }, status=400)
            except Exception:
                transaction.set_rollback(True)
                return Response({'error': f'No pizza found for {size} {name}'}, status=400)

            # order_detail_id 생성
            max_detail = OrderDetail.objects.aggregate(max_id=Max('order_detail_id'))
            order_detail_id = (max_detail['max_id'] or 0) + 1

            # 주문 상세 생성
            OrderDetail.objects.create(
                order_detail_id=order_detail_id,
                order=order_obj,
                pizza=pizza,
                quantity=quantity
            )

    return Response({'order_id': order_id, 'message': 'Order placed successfully'}, status=201)

@api_view(['GET'])
def get_branch(request):
    branches = Branch.objects.all()

    try:
        return Response([{'bran_id': branch.bran_id, 'bran_nm': branch.bran_nm} for branch in branches])
    except Branch.DoesNotExist:
        return Response({'error': 'Branch not found'}, status=404)

    