from django.contrib import admin

from restaurant.models import Table, Reservation


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_filter = ('number', 'guests_count')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_filter = ('start_time', 'guests_count', 'table', 'user')
