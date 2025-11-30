from django.db import models
from django.db.models import PositiveIntegerField, TextField, ForeignKey, DateTimeField, CharField, Q
from django.db.models.fields import BooleanField
from django.utils import timezone

from config import settings


class Table(models.Model):
    number = PositiveIntegerField(verbose_name='Номер стола', help_text='Укажите номер стола', unique=True)
    guests_count = PositiveIntegerField(verbose_name='Количество гостей', help_text='Укажите количество гостей')
    type = CharField(max_length=100, verbose_name='Тип стола',
                     help_text='Укажите тип стола (при необходимости)', null=True, blank=True)

    def is_available(self, start_time, duration):
        """
        Проверяет, свободен ли стол на указанное время
        """
        end_time = start_time + timezone.timedelta(hours=duration)

        conflicting_bookings = self.bookings.filter(
            Q(start_time__lt=end_time) &
            Q(start_time__gte=start_time - timezone.timedelta(hours=7))
        )

        for booking in conflicting_bookings:
            booking_end = booking.start_time + timezone.timedelta(hours=booking.duration)
            if start_time < booking_end and end_time > booking.start_time:
                return False
        return True

    def __str__(self):
        return f'Стол {self.number}'

    class Meta:
        verbose_name = 'стол'
        verbose_name_plural = 'столы'
        ordering = ['guests_count', 'type', 'number']


class Reservation(models.Model):
    guests_count = PositiveIntegerField(verbose_name='Количество гостей')
    start_time = DateTimeField(verbose_name='Время начала бронирования')
    duration = PositiveIntegerField(verbose_name='Продолжительность брони')
    comment = TextField(max_length=300, verbose_name='Комментарий', null=True, blank=True)
    table = ForeignKey('restaurant.Table', on_delete=models.PROTECT,
                       related_name='bookings', verbose_name='Выберите стол')
    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    is_active = BooleanField(verbose_name='Бронь активна', default=True)

    def __str__(self):
        return f'Бронь {self.user.email} {self.start_time}'

    class Meta:
        verbose_name = 'бронь'
        verbose_name_plural = 'брони'
        ordering = ['start_time', 'guests_count', 'table', 'user']
