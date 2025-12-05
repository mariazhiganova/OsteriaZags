from django.db import models
from django.db.models import ImageField
from django.db.models.fields import CharField, TextField


class ContentBlock(models.Model):
    slug = models.SlugField(max_length=100, unique=True, verbose_name='Slug (метка)', help_text='Уникальная метка')
    image = ImageField(upload_to='img', null=True, blank=True, verbose_name='Фото')
    title = CharField(max_length=50, null=True, blank=True, verbose_name='Заголовок')
    subtitle = CharField(max_length=50, null=True, blank=True, verbose_name='Подзаголовок')
    body = TextField(max_length=5000, null=True, blank=True, verbose_name='Текст')

    def __str__(self):
        return self.title or 'Без названия'

    class Meta:
        verbose_name = 'блок контента'
        verbose_name_plural = 'блоки контента'
