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
