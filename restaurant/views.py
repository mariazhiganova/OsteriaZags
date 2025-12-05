from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, TemplateView

from restaurant.forms import ReservationForm
from restaurant.models import Reservation, Table
from services import send_contact_email, create_tables_options_html, get_available_tables_service


class HomeView(TemplateView):
    template_name = 'restaurant/home.html'

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name', 'пользователь')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        message = request.POST.get('message', '')

        if phone or email:
            try:
                send_contact_email(name, phone, message, email)

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return HttpResponse('OK')

                else:
                    messages.success(request, 'Спасибо! Мы скоро с вами свяжемся.')
                    return redirect('index')

            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return HttpResponse('Error', status=400)
                else:
                    messages.error(request, 'Ошибка отправки. Попробуйте позже.')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return HttpResponse('Validation Error', status=400)
            else:
                messages.error(request, 'Заполните телефон или email.')

        return self.render_to_response(self.get_context_data())


class ReservationCreateView(LoginRequiredMixin, CreateView):
    model = Reservation
    form_class = ReservationForm
    template_name = 'restaurant/reservation_create.html'
    success_url = reverse_lazy('restaurant:reservation_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


def get_available_tables_ajax(request):
    if request.method == 'GET':
        try:
            guests_count = int(request.GET.get('guests_count'))
            start_time_str = request.GET.get('start_time')
            duration = int(request.GET.get('duration'))
            current_table_id = request.GET.get('current_table_id')
            exclude_booking_id = request.GET.get('exclude_booking_id')

            if 'Z' in start_time_str or '+' in start_time_str:
                start_time = timezone.datetime.fromisoformat(start_time_str)
            else:
                naive_time = timezone.datetime.fromisoformat(start_time_str)
                start_time = timezone.make_aware(naive_time)

            available_tables = get_available_tables_service(
                guests_count, start_time, duration, exclude_booking_id
            )

            options_html = create_tables_options_html(available_tables, current_table_id)

            return JsonResponse({
                'success': True,
                'options_html': options_html,
                'count': len(available_tables),
                'table_ids': [table.id for table in available_tables]
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'options_html': '<option value="">Ошибка загрузки</option>',
                'error': str(e)
            })


class ReservationListView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = 'restaurant/lk.html'
    context_object_name = 'reservations'

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.groups.filter(name='Managers').exists():
            return queryset
        return queryset.filter(user=self.request.user)


class ReservationUpdateView(LoginRequiredMixin, UpdateView):
    model = Reservation
    form_class = ReservationForm
    template_name = 'restaurant/reservation_create.html'
    context_object_name = 'reservation'
    success_url = reverse_lazy('restaurant:reservation_list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        if obj.user == self.request.user or self.request.user.groups.filter(name='Managers').exists():
            return obj

        raise PermissionDenied('Нет прав на редактирование брони')


class ReservationDeleteView(LoginRequiredMixin, DeleteView):
    model = Reservation
    template_name = 'restaurant/confirm_delete_reservation.html'
    success_url = reverse_lazy('restaurant:reservation_list')
    context_object_name = 'reservation'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        if obj.user == self.request.user or self.request.user.groups.filter(name='Managers').exists():
            return obj

        raise PermissionDenied('Нет прав на удаление брони')
