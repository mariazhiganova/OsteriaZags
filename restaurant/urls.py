from django.urls import path
from django.views.generic import TemplateView

from restaurant.apps import RestaurantConfig
from restaurant.views import ReservationCreateView, ReservationListView, ReservationDeleteView, ReservationUpdateView, \
    HomeView, get_available_tables_ajax

app_name = RestaurantConfig.name

urlpatterns = [
    path('', HomeView.as_view(template_name='restaurant/index.html'), name='home'),
    path('about', TemplateView.as_view(template_name='restaurant/about.html'), name='about'),

    path('reservation/create/', ReservationCreateView.as_view(), name='reservation_create'),
    path('get-available-tables/', get_available_tables_ajax, name='get_available_tables'),
    path('reservation/list/', ReservationListView.as_view(), name='reservation_list'),
    path('reservation/<int:pk>/update/', ReservationUpdateView.as_view(), name='reservation_update'),
    path('reservation/<int:pk>/delete/', ReservationDeleteView.as_view(), name='reservation_delete'),
]
