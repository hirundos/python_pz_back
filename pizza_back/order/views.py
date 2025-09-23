from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.db.models import Max
from django.utils import timezone
from django.conf import settings
import requests
import logging

from .models import Order, OrderDetail, Branch
from pizza_back.menu.models import Pizza
from .authentication import CustomJWTAuthentication

logger = logging.getLogger(__name__)

@api_view(['GET'])
@authentication_classes([CustomJWTAuthentication])
@permission_classes([IsAuthenticated])
def myorder_list(request):
    """사용자의 주문 목록을 조회합니다."""
    try:
        orders = (
            OrderDetail.objects
            .select_related('order', 'pizza')
            .filter(order__member_id=request.user.member_id)
            .values(
                'order__order_id',
                'pizza__pizza_id',
                'quantity',
                'order__date',
                'order__time'
            )
            .order_by('-order__date', '-order__time')
        )

        result = [
            {
                'order_id': order['order__order_id'],
                'pizza_id': order['pizza__pizza_id'],
                'quantity': order['quantity'],
                'date': order['order__date'],
                'time': order['order__time'],
            }
            for order in orders
        ]

        return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error fetching order list: {str(e)}")
        return Response(
            {'error': '주문 목록을 불러오는 중 오류가 발생했습니다.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@authentication_classes([CustomJWTAuthentication])
@permission_classes([IsAuthenticated])
def order(request):
    """새로운 주문을 생성합니다."""
    lines = request.data.get('lines', [])
    branch_id = request.data.get('branchId')

    # 유효성 검사
    validation_error = _validate_order_data(lines, branch_id)
    if validation_error:
        return validation_error

    try:
        with transaction.atomic():
            # 주문 생성
            order_obj = _create_order(request.user.member_id, branch_id)

            # 주문 상세 생성
            for line in lines:
                pizza = _get_or_fetch_pizza(line)
                _create_order_detail(order_obj, pizza, line.get('quantity'))

            return Response(
                {
                    'order_id': order_obj.order_id,
                    'message': '주문이 성공적으로 완료되었습니다.'
                },
                status=status.HTTP_201_CREATED
            )

    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Order creation failed: {str(e)}")
        return Response(
            {'error': '주문 처리 중 오류가 발생했습니다.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_branch(request):
    """모든 지점 정보를 조회합니다."""
    try:
        branches = Branch.objects.all().values('bran_id', 'bran_nm')
        return Response(list(branches), status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error fetching branches: {str(e)}")
        return Response(
            {'error': '지점 정보를 불러오는 중 오류가 발생했습니다.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Helper functions
def _validate_order_data(lines, branch_id):
    """주문 데이터의 유효성을 검사합니다."""
    if not lines:
        return Response(
            {'error': '주문 항목이 없습니다.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not branch_id:
        return Response(
            {'error': '지점 ID가 필요합니다.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    return None

def _create_order(member_id, branch_id):
    """새로운 주문을 생성합니다."""
    now = timezone.now()

    # 새로운 order_id 생성
    max_order_id = Order.objects.aggregate(max_id=Max('order_id'))['max_id'] or 0

    return Order.objects.create(
        order_id=max_order_id + 1,
        date=now.date(),
        time=now.time(),
        member_id=member_id,
        bran_id=branch_id
    )

def _get_or_fetch_pizza(line):
    """피자 정보를 가져오거나 외부 API를 통해 조회합니다."""
    size = line.get('size')
    name = line.get('name')

    try:
        # 외부 API 호출
        response = requests.post(
            f"{settings.API_URL}/menu/get_pizza_id/",
            data={'size': size, 'name': name},
            timeout=10
        )

        if response.status_code != 200:
            raise ValueError(f'{size} {name}에 해당하는 피자를 찾을 수 없습니다.')

        pizza_id = response.json().get('pizza_id')

        # 데이터베이스에서 피자 확인
        try:
            return Pizza.objects.get(pizza_id=pizza_id)
        except Pizza.DoesNotExist:
            raise ValueError(f'피자 ID {pizza_id}를 데이터베이스에서 찾을 수 없습니다.')

    except requests.exceptions.RequestException as e:
        logger.error(f"Menu service connection failed: {str(e)}")
        raise ValueError('메뉴 서비스에 연결할 수 없습니다.')
    except Exception as e:
        logger.error(f"Pizza fetch error: {str(e)}")
        raise ValueError(f'{name} ({size}) 피자 처리 중 오류가 발생했습니다.')

def _create_order_detail(order_obj, pizza, quantity):
    """주문 상세 정보를 생성합니다."""
    # 새로운 order_detail_id 생성
    max_detail_id = OrderDetail.objects.aggregate(
        max_id=Max('order_detail_id')
    )['max_id'] or 0

    return OrderDetail.objects.create(
        order_detail_id=max_detail_id + 1,
        order=order_obj,
        pizza=pizza,
        quantity=quantity
    )
