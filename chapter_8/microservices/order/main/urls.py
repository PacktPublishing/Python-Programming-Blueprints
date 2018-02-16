from django.urls import path

from .views import (
    cancel_order,
    set_next_status,
    set_status,
    OrdersByCustomerView,
    IncompleteOrdersByCustomerView,
    CompletedOrdersByCustomerView,
    OrderByStatusView,
    CreateOrderView,
)

urlpatterns = [
    path(
        r'order/add/',
        CreateOrderView.as_view()
    ),
    path(
        r'customer/<int:customer_id>/orders/get/',
        OrdersByCustomerView.as_view()
    ),
    path(
        r'customer/<int:customer_id>/orders/incomplete/get/',
        IncompleteOrdersByCustomerView.as_view()
    ),
    path(
        r'customer/<int:customer_id>/orders/complete/get/',
        CompletedOrdersByCustomerView.as_view()
    ),
    path(
        r'order/<int:order_id>/cancel',
        cancel_order
    ),
    path(
        r'order/status/<int:status_id>/get/',
        OrderByStatusView.as_view()
    ),
    path(
        r'order/<int:order_id>/status/<int:status_id>/set/',
        set_status
    ),
    path(
        r'order/<int:order_id>/status/next/',
        set_next_status
    ),
]
