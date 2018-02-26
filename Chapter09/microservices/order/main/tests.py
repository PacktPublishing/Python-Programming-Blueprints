from django.test import TestCase


from dateutil.relativedelta import relativedelta

from django.test import TestCase
from django.utils import timezone

from .models import OrderCustomer, Order
from .status import Status

from .exceptions import InvalidArgumentError
from .exceptions import OrderAlreadyCancelledError
from .exceptions import OrderAlreadyCompletedError


class OrderModelTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.customer_001 = OrderCustomer.objects.create(
            customer_id=1,
            email='customer_001@test.com'
        )

        Order.objects.create(order_customer=cls.customer_001)

        Order.objects.create(order_customer=cls.customer_001,
                             status=Status.Completed.value)

        cls.customer_002 = OrderCustomer.objects.create(
            customer_id=1,
            email='customer_002@test.com'
        )

        Order.objects.create(order_customer=cls.customer_002)

    def test_cancel_order(self):
        order = Order.objects.get(pk=1)

        self.assertIsNotNone(order)
        self.assertEqual(Status.Received.value, order.status)

        Order.objects.cancel_order(order)

        self.assertEqual(Status.Cancelled.value, order.status)

    def test_cancel_completed_order(self):
        order = Order.objects.get(pk=2)

        self.assertIsNotNone(order)
        self.assertEqual(Status.Completed.value, order.status)

        with self.assertRaises(OrderCancellationError):
            Order.objects.cancel_order(order)

    def test_cancel_order_with_invalid_argument(self):
        with self.assertRaises(InvalidArgumentError):
            Order.objects.cancel_order({'id': 1})

    def test_get_all_orders_by_customer(self):
        orders = Order.objects.get_all_orders_by_customer(customer_id=1)

        self.assertEqual(2, len(orders),
                         msg='It should have returned 2 orders.')

    def test_get_all_order_by_customer_with_invalid_id(self):
        with self.assertRaises(InvalidArgumentError):
            Order.objects.get_all_orders_by_customer('o')

    def test_get_customer_incomplete_orders(self):
        orders = Order.objects.get_customer_incomplete_orders(customer_id=1)

        self.assertEqual(1, len(orders))
        self.assertEqual(Status.Received.value, orders[0].status)

    def test_get_customer_incomplete_orders_with_invalid_id(self):
        with self.assertRaises(InvalidArgumentError):
            Order.objects.get_customer_incomplete_orders('o')

    def test_get_customer_completed_orders(self):
        orders = Order.objects.get_customer_completed_orders(customer_id=1)

        self.assertEqual(1, len(orders))
        self.assertEqual(Status.Completed.value, orders[0].status)

    def test_get_customer_completed_orders_with_invalid_id(self):
        with self.assertRaises(InvalidArgumentError):
            Order.objects.get_customer_completed_orders('o')

    def test_get_order_by_status(self):
        order = Order.objects.get_orders_by_status(Status.Received)

        self.assertEqual(2, len(order),
                         msg=('There should be only 2 orders '
                              'with status=Received.'))

        self.assertEqual('customer_001@test.com',
                         order[0].order_customer.email)

    def test_get_order_by_status_with_invalid_status(self):
        with self.assertRaises(InvalidArgumentError):
            Order.objects.get_orders_by_status(1)

    def test_get_orders_by_period(self):
        date_from = timezone.now() - relativedelta(days=1)
        date_to = date_from + relativedelta(days=2)

        orders = Order.objects.get_orders_by_period(date_from, date_to)

        self.assertEqual(3, len(orders))

        date_from = timezone.now() + relativedelta(days=3)
        date_to = date_from + relativedelta(months=1)

        orders = Order.objects.get_orders_by_period(date_from, date_to)

        self.assertEqual(0, len(orders))

    def test_get_orders_by_period_with_invalid_start_date(self):
        start_date = timezone.now()

        with self.assertRaises(InvalidArgumentError):
            Order.objects.get_orders_by_period(start_date, None)

    def test_get_orders_by_period_with_invalid_end_date(self):
        end_date = timezone.now()

        with self.assertRaises(InvalidArgumentError):
            Order.objects.get_orders_by_period(None, end_date)

    def test_set_next_status(self):
        order = Order.objects.get(pk=1)

        self.assertTrue(order is not None,
                        msg='The order is None.')

        self.assertEqual(Status.Received.value, order.status,
                         msg='The status should have been Status.Received.')

        Order.objects.set_next_status(order)

        self.assertEqual(Status.Processing.value, order.status,
                         msg='The status should have been Status.Processing.')

    def test_set_next_status_on_completed_order(self):
        order = Order.objects.get(pk=2)

        with self.assertRaises(OrderAlreadyCompletedError):
            Order.objects.set_next_status(order)

    def test_set_next_status_on_invalid_order(self):
        with self.assertRaises(InvalidArgumentError):
            Order.objects.set_next_status({'order': 1})

    def test_set_status(self):
        order = Order.objects.get(pk=1)

        Order.objects.set_status(order, Status.Processing)

        self.assertEqual(Status.Processing.value, order.status)

    def test_set_status_on_completed_order(self):
        order = Order.objects.get(pk=2)

        with self.assertRaises(OrderAlreadyCompletedError):
            Order.objects.set_status(order, Status.Processing)

    def test_set_status_on_cancelled_order(self):
        order = Order.objects.get(pk=1)
        Order.objects.cancel_order(order)

        with self.assertRaises(OrderAlreadyCancelledError):
            Order.objects.set_status(order, Status.Processing)

    def test_set_status_with_invalid_order(self):
        with self.assertRaises(InvalidArgumentError):
            Order.objects.set_status(None, Status.Processing)

    def test_set_status_with_invalid_status(self):
        order = Order.objects.get(pk=1)

        with self.assertRaises(InvalidArgumentError):
            Order.objects.set_status(order, {'status': 1})