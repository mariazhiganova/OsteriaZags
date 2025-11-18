from django.db import models
from django.db.models import PositiveIntegerField, TextField, ForeignKey, DateTimeField, CharField

from config import settings


class Table(models.Model):
    number = PositiveIntegerField(verbose_name='Номер стола', help_text='Укажите номер стола', unique=True)
    guests_count = PositiveIntegerField(verbose_name='Количество гостей', help_text='Укажите количество гостей')
    type = CharField(max_length=100, verbose_name='Тип стола',
                     help_text='Выберите тип стола (при необходимости)', null=True, blank=True)


class Reservation(models.Model):
    guests_count = PositiveIntegerField(verbose_name='Количество гостей', help_text='Выберите количество гостей')
    start_time = DateTimeField(verbose_name='Время начала бронирования', help_text='Укажите время начала бронирования')
    duration = PositiveIntegerField(verbose_name='Продолжительность брони',
                                    help_text='Выберите продолжительность брони')

    comment = TextField(max_length=300, verbose_name='Комментарий',
                        help_text='Укажите комментарий (при необходимости)', null=True, blank=True)
    table = ForeignKey(Table, on_delete=models.PROTECT, related_name='bookings', verbose_name='Выберите стол')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')

    def __str__(self):
        return self.start_time

    class Meta:
        verbose_name = 'бронь'
        verbose_name_plural = 'брони'
        ordering = ['guests_count', 'start_time', 'table']
