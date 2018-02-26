from django.contrib import admin

from .models import GamePlatform
from .models import Game
from .models import PriceList

admin.autodiscover()

admin.site.register(GamePlatform)
admin.site.register(Game)
admin.site.register(PriceList)
