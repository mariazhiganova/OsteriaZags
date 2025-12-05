from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from restaurant.models import Reservation


@shared_task
def inactivate_reservation():
    """
    Смена флага is_active на False у всех прошедших броней
    """
    reservations = Reservation.objects.filter(is_active=True)

    for res in reservations:
        end_time = res.start_time + timedelta(hours=res.duration)
        print(end_time)
        now = timezone.now()
        print(now)

        if end_time < now:
            res.is_active = False
            res.save()
