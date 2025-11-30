from django import forms
from django.utils import timezone
from datetime import time
from django.core.exceptions import ValidationError
from django.forms.models import ModelForm

from restaurant.models import Reservation
from services import is_table_available_service


class ReservationForm(ModelForm):
    class Meta:
        model = Reservation
        exclude = ['user', 'is_active']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            })
        }

    def __init__(self, *args, **kwargs):
        super(ReservationForm, self).__init__(*args, **kwargs)

        self.fields['duration'].widget.attrs.update({
            'class': 'form-control reservation-field',
            'placeholder': 'Укажите длительность бронирования (в часах)'
        })
        self.fields['guests_count'].widget.attrs.update({
            'class': 'form-control reservation-field',
            'placeholder': 'Укажите количество гостей'
        })
        self.fields['table'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Выберите из доступных столов)'
        })
        self.fields['comment'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Оставьте комментарий (при необходимости)'
        })

    def clean_guests_count(self):
        guests_count = self.cleaned_data.get('guests_count')
        if guests_count > 8:
            raise ValidationError('Для бронирования от 7 персон просьба обратиться к администратору')
        return guests_count

    def clean_start_time(self):
        start_time = self.cleaned_data.get('start_time')
        now = timezone.now()
        opening_time = time(9, )
        closing_time = time(22, 0)

        if start_time:
            min_start_time = now + timezone.timedelta(hours=2)

            if start_time < min_start_time:
                raise ValidationError('Бронирование возможно не позднее чем за два часа до планируемого посещения')

            if start_time < now:
                raise ValidationError('Невозможно бронирование в прошлом. Проверьте дату')

            if start_time.time() > closing_time or start_time.time() < opening_time:
                raise ValidationError(
                    'Бронирование возможно с 9:00 и до 22:00. Обратите внимание на часы работы заведения')

        return start_time

    def clean_table(self):
        table = self.cleaned_data.get('table')
        if not table:
            raise ValidationError('Необходимо выбрать стол')

        if self.instance and self.instance.pk:
            return table

        available_tables = self.fields['table'].queryset
        if available_tables and table not in available_tables:
            raise ValidationError(
                'Выбранный стол недоступен для указанных параметров. '
                'Пожалуйста, выберите стол из списка доступных.'
            )

        return table

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        duration = cleaned_data.get('duration')
        table = cleaned_data.get('table')
        guests_count = cleaned_data.get('guests_count')

        if table and guests_count and guests_count > table.guests_count:
            raise forms.ValidationError('Столик слишком мал для такого количества гостей')

        if table and start_time and duration:
            if not is_table_available_service(table, start_time, duration):
                if not self.instance.pk or self.instance.table_id != table.id:
                    raise forms.ValidationError('Выбранный столик уже занят на это время')

        if start_time and duration:
            end_time = start_time + timezone.timedelta(hours=duration)

            if end_time.date() != start_time.date():
                raise forms.ValidationError('Бронирование должно начинаться и заканчиваться в один день')

            if end_time.time() > time(22, 0) or end_time.date() > start_time.date():
                raise forms.ValidationError('Бронирование должно заканчиваться до 22:00')

        return cleaned_data
