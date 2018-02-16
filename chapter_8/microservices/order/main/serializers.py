import functools

from rest_framework import serializers

from .models import Order, OrderItems, OrderCustomer


class OrderCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderCustomer
        fields = ('customer_id', 'email', 'name', )

    def create(self, validated_data):
        order_item = OrderCustomer.objects.create(**validated_data)
        order_item.save()
        return order_item


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItems
        fields = ('name', 'price_per_unit', 'product_id', 'quantity', )


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    order_customer = OrderCustomerSerializer()
    status = serializers.SerializerMethodField()

    class Meta:
        depth = 1
        model = Order
        fields = ('items', 'total', 'order_customer',
                  'created_at', 'id', 'status', )

    def get_status(self, obj):
        return obj.get_status_display()

    def _create_order_item(self, item, order):
        item['order'] = order
        return OrderItems(**item)

    def create(self, validated_data):
        validated_customer = validated_data.pop('order_customer')
        validated_items = validated_data.pop('items')

        customer = OrderCustomer.objects.create(**validated_customer)

        validated_data['order_customer'] = customer
        order = Order.objects.create(**validated_data)

        mapped_items = map(
            functools.partial(
                self._create_order_item, order=order), validated_items
        )

        OrderItems.objects.bulk_create(mapped_items)

        return order
