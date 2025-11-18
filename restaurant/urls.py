from django.urls import path
from django.views.generic import TemplateView

from restaurant.apps import RestaurantConfig

app_name = RestaurantConfig.name

urlpatterns = [
    path('', TemplateView.as_view(template_name='restaurant/index.html'), name='home'),

]
