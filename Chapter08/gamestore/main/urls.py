from django.urls import path
from . import views
from django.contrib.auth.views import login
from django.contrib.auth.views import logout
from .forms import AuthenticationForm


urlpatterns = [
    path(r'', views.index, name='index'),
    path(r'accounts/login/', login, {
        'template_name': 'login.html',
        'authentication_form': AuthenticationForm
    }, name='login'),
    path(r'accounts/logout/', logout, {
      'next_page': '/'
    }, name='logout'),
    path(r'accounts/signup/', views.signup, name='signup'),
    path(r'games-list/highlighted/', views.show_highlighted_games),
    path(r'games-list/all/', views.show_all_games),
    path(r'cart/', views.ShoppingCartEditView.as_view(), name='user-cart'),
    path(r'cart/add/<int:game_id>/', views.add_to_cart),
    path(r'cart/send', views.send_cart),
    path(r'my-orders/', views.my_orders),
]
