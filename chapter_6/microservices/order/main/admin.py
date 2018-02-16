from django.contrib import admin

from .models import Order
from .models import OrderCustomer
from .models import OrderItems


admin.site.register(OrderCustomer)
admin.site.register(OrderItems)
admin.site.register(Order)
