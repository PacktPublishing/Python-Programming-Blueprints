from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from .forms import SignupForm
from django.contrib.auth.models import User
from .models import Game

from django.views.generic.edit import UpdateView
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.db.models import Sum, F, DecimalField

from .models import ShoppingCart
from .models import ShoppingCartItem
from .forms import ShoppingCartFormSet

from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

import json
import requests
from django.core.serializers.json import DjangoJSONEncoder
from gamestore import settings
from http import HTTPStatus
from .models import OrderItem


def _prepare_order_data(cart):

    cart_items = ShoppingCartItem.objects.values_list(
        'game__name',
        'price_per_unit',
        'game__id',
        'quantity').filter(cart__id=cart.id)

    order = cart_items.aggregate(
        total_order=Sum(F('price_per_unit') * F('quantity'),
                        output_field=DecimalField(decimal_places=2))
    )

    order_items = [OrderItem(*x)._asdict() for x in cart_items]

    order_customer = {
        'customer_id': cart.user.id,
        'email': cart.user.email,
        'name': f'{cart.user.first_name} {cart.user.last_name}'
    }

    order_dict = {
        'items': order_items,
        'order_customer': order_customer,
        'total': order['total_order']
    }

    return json.dumps(order_dict, cls=DjangoJSONEncoder)


@login_required
def my_orders(request):
    headers = {
        'Authorization': f'Token {settings.ORDER_SERVICE_AUTHTOKEN}',
        'Content-type': 'application/json'
    }

    get_order_endpoint = f'/api/customer/{request.user.id}/orders/get/'
    service_url = f'{settings.ORDER_SERVICE_BASEURL}{get_order_endpoint}'

    response = requests.get(
        service_url,
        headers=headers
    )

    if HTTPStatus(response.status_code) is HTTPStatus.OK:
        request_data = json.loads(response.text)
        context = {'orders': request_data}
    else:
        messages.add_message(
            request,
            messages.ERROR,
            ('Unfortunately, we could not retrieve your orders.'
             ' Try again later.'))
        context = {'orders': []}

    return render(request, 'main/my-orders.html', context)


@login_required
def send_cart(request):
    cart = ShoppingCart.objects.get(user_id=request.user.id)

    data = _prepare_order_data(cart)

    headers = {
        'Authorization': f'Token {settings.ORDER_SERVICE_AUTHTOKEN}',
        'Content-type': 'application/json'
    }

    service_url = f'{settings.ORDER_SERVICE_BASEURL}/api/order/add/'

    response = requests.post(
        service_url,
        headers=headers,
        data=data)

    if HTTPStatus(response.status_code) is HTTPStatus.CREATED:
        request_data = json.loads(response.text)
        ShoppingCart.objects.empty(cart)
        messages.add_message(
            request,
            messages.INFO,
            ('We received your order!'
             'ORDER ID: {}').format(request_data['order_id']))
    else:
        messages.add_message(
            request,
            messages.ERROR,
            ('Unfortunately, we could not receive your order.'
             ' Try again later.'))

    return HttpResponseRedirect(reverse_lazy('user-cart'))


@login_required
def add_to_cart(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    cart = ShoppingCart.objects.get_by_user(request.user)

    existing_item = ShoppingCartItem.objects.get_existing_item(cart, game)

    if existing_item is None:

        price = (Decimal(0)
                 if not hasattr(game, 'pricelist')
                 else game.pricelist.price_per_unit)

        new_item = ShoppingCartItem(
            game=game,
            quantity=1,
            price_per_unit=price,
            cart=cart
        )
        new_item.save()
    else:
        existing_item.quantity = F('quantity') + 1
        existing_item.save()

    messages.add_message(
        request,
        messages.INFO,
        f'The game {game.name} has been added to your cart.')

    return HttpResponseRedirect(reverse_lazy('user-cart'))


class ShoppingCartEditView(UpdateView):
    model = ShoppingCart
    form_class = ShoppingCartFormSet
    template_name = 'main/cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        items = ShoppingCartItem.objects.get_items(self.object)

        context['is_cart_empty'] = (items.count() == 0)

        order = items.aggregate(
            total_order=Sum(F('price_per_unit') * F('quantity'),
                            output_field=DecimalField())
        )

        context['total_order'] = order['total_order']

        return context

    def get_object(self):
        try:
            return ShoppingCart.objects.get_by_user(self.request.user)
        except ShoppingCart.DoesNotExist:
            new_cart = ShoppingCart.objects.create_cart(self.request.user)
            new_cart.save()
            return new_cart

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(reverse_lazy('user-cart'))


def index(request):
    max_highlighted_games = 3
    max_game_list = 9

    highlighted_games_list = Game.objects.get_highlighted()
    games_list = Game.objects.get_not_highlighted()

    show_more_link_highlighted = highlighted_games_list.count() > max_highlighted_games
    show_more_link_games = games_list.count() > max_game_list

    context = {
        'highlighted_games_list': highlighted_games_list[:max_highlighted_games],
        'games_list': games_list[:max_game_list],
        'show_more_link_games': show_more_link_games,
        'show_more_link_highlighted': show_more_link_highlighted
    }

    return render(request, 'main/index.html', context)


@csrf_protect
def signup(request):

    if request.method == 'POST':

        form = SignupForm(request.POST)

        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            user.save()

            return render(request, 'main/create_account_success.html', {})

    else:
        form = SignupForm()

    return render(request, 'main/signup.html', {'form': form})


def show_all_games(request):
    games = Game.objects.all()

    context = {'games': games}

    return render(request, 'main/all_games.html', context)


def show_highlighted_games(request):
    games = Game.objects.get_highlighted()

    context = {'games': games}

    return render(request, 'main/highlighted.html', context)
