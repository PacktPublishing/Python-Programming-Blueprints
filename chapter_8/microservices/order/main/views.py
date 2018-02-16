from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.response import Response


from .models import Order
from .status import Status
from .view_helper import OrderListAPIBaseView
from .view_helper import set_status_handler
from .serializers import OrderSerializer


class OrdersByCustomerView(OrderListAPIBaseView):
    lookup_field = 'customer_id'

    def get_queryset(self, customer_id):
        return Order.objects.get_all_orders_by_customer(customer_id)


class IncompleteOrdersByCustomerView(OrderListAPIBaseView):
    lookup_field = 'customer_id'

    def get_queryset(self, customer_id):
        return Order.objects.get_customer_incomplete_orders(
            customer_id
        )


class CompletedOrdersByCustomerView(OrderListAPIBaseView):
    lookup_field = 'customer_id'

    def get_queryset(self, customer_id):
        return Order.objects.get_customer_completed_orders(
            customer_id
        )


class OrderByStatusView(OrderListAPIBaseView):
    lookup_field = 'status_id'

    def get_queryset(self, status_id):
        return Order.objects.get_orders_by_status(
            Status(status_id)
        )


class CreateOrderView(generics.CreateAPIView):

    def post(self, request, *arg, **args):
        serializer = OrderSerializer(data=request.data)

        if serializer.is_valid():
            order = serializer.save()
            return Response(
                {'order_id': order.id},
                status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)


def cancel_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)

    return set_status_handler(
        lambda: Order.objects.cancel_order(order)
    )


def set_next_status(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)

    return set_status_handler(
        lambda: Order.objects.set_next_status(order)
    )


def set_status(request, order_id, status_id):
    order = get_object_or_404(Order, order_id=order_id)

    try:
        status = Status(status_id)
    except ValueError:
        return HttpResponse(
            'The status value is invalid.',
            status=status.HTTP_400_BAD_REQUEST)

    return set_status_handler(
        lambda: Order.objects.set_status(order, status)
    )
