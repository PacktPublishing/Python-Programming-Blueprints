from django.contrib import admin

from .models import Order
from .models import OrderCustomer
from .models import OrderItems

from .notifier import notify
from .notification_type import NotificationType
from .serializers import OrderSerializer
from .status import Status

class OrderAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        order_current_status = Status(obj.status)
        status_changed = 'status' in form.changed_data

        if (status_changed and order_current_status is Status.Shipping):
            notify(OrderSerializer(obj), NotificationType.ORDER_SHIPPED)

        super(OrderAdmin, self).save_model(request, obj, form, change)


admin.site.register(OrderCustomer)
admin.site.register(OrderItems)
admin.site.register(Order, OrderAdmin)



