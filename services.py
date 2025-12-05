from datetime import timedelta

from django.core.mail import send_mail

from config import settings
from restaurant.models import Table


def send_contact_email(name, phone, message, email):
    """
    Сервисная функция: реализует отправку письма из формы обратной связи
    """
    text = f'''{name} оставил(а) заявку на обратную связь.
    Телефон: {phone}
    Email: {email}
    Сообщение: {message}

    Отправлено с сайта Osteria ZAGS'''

    send_mail(
        subject=f'📨 Новая заявка от {name}',
        message=text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.ADMIN_EMAIL],
    )


def get_available_tables_service(guests_count, start_time, duration, exclude_booking_id=None):
    """
    Сервисная функция: находит доступные столы
    """
    suitable_tables = Table.objects.filter(guests_count__gte=guests_count)

    available_tables = []
    for table in suitable_tables:
        if is_table_available_service(table, start_time, duration, exclude_booking_id):
            available_tables.append(table)

    return available_tables


def is_table_available_service(table, start_time, duration, exclude_booking_id=None):
    """
    Сервисная функция: Проверяет доступность конкретного стола и возвращает True если свободен, False если занят
    """
    end_time = start_time + timedelta(hours=duration)

    conflicting_bookings = table.bookings.filter(
        start_time__gte=start_time - timedelta(hours=24),
        start_time__lt=end_time + timedelta(hours=24)
    )

    if exclude_booking_id:
        conflicting_bookings = conflicting_bookings.exclude(id=exclude_booking_id)

    for booking in conflicting_bookings:
        booking_end = booking.start_time + timedelta(hours=booking.duration)
        if start_time < booking_end and end_time > booking.start_time:
            return False

    return True


def create_tables_options_html(available_tables, current_table_id=None):
    """
    Сервисная функция: создает HTML код для выпадающего списка
    При редактировании current_table_id будет выбран автоматически
    """
    options_html = '<option value="">Выберите стол...</option>'

    for table in available_tables:
        display_name = f'Стол {table.number} (до {table.guests_count} гостей'
        if table.type:
            display_name += f', {table.type}'
        display_name += ')'

        selected = 'selected' if str(table.id) == str(current_table_id) else ''

        options_html += f'<option value="{table.id}" {selected}>{display_name}</option>'

    return options_html
