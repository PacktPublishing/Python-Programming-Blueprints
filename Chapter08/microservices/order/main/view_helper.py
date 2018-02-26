from rest_framework import generics, status
from rest_framework.response import Response

from django.http import HttpResponse

from .exceptions import InvalidArgumentError
from .exceptions import OrderAlreadyCancelledError
from .exceptions import OrderAlreadyCompletedError

from .serializers import OrderSerializer


class OrderListAPIBaseView(generics.ListAPIView):
    serializer_class = OrderSerializer
    lookup_field = ''

    def get_queryset(self, lookup_field_id):
        pass

    def list(self, request, *args, **kwargs):
        try:
            result = self.get_queryset(kwargs.get(self.lookup_field, None))
        except Exception as err:
            return Response(err, status=status.HTTP_400_BAD_REQUEST)

        serializer = OrderSerializer(result, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


def set_status_handler(set_status_delegate):
    try:
        set_status_delegate()
    except (
            InvalidArgumentError,
            OrderAlreadyCancelledError,
            OrderAlreadyCompletedError) as err:
        return HttpResponse(err, status=status.HTTP_400_BAD_REQUEST)

    return HttpResponse(status=status.HTTP_204_NO_CONTENT)
