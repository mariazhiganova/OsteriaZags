from datetime import timedelta

from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from restaurant.forms import ReservationForm
from restaurant.models import Table, Reservation
from services import send_contact_email, create_tables_options_html, is_table_available_service
from users.models import CustomUser


class ReservationTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create(email='test1@mail.com', password='12345test')
        self.table_1 = Table.objects.create(number=1, guests_count=2)
        self.table_2 = Table.objects.create(number=2, guests_count=4)
        self.future_time = timezone.now() + timedelta(hours=14)

    def test_reservation_create(self):
        """Тест создания брони"""
        reservation = Reservation.objects.create(
            user=self.user,
            table=self.table_1,
            start_time=self.future_time,
            duration=2,
            guests_count=2
        )

        self.assertEqual(Reservation.objects.count(), 1)
        self.assertEqual(reservation.user, self.user)
        self.assertEqual(reservation.table, self.table_1)
        self.assertEqual(Reservation.objects.count(), 1)
        self.assertEqual(reservation.guests_count, 2)
        self.assertEqual(reservation.duration, 2)
        self.assertTrue(reservation.is_active)

    def test_reservation_update(self):
        """Тест обновления брони"""
        reservation = Reservation.objects.create(
            user=self.user,
            table=self.table_2,
            start_time=self.future_time,
            duration=2,
            guests_count=2
        )

        reservation.guests_count = 3
        reservation.duration = 3
        reservation.save()

        updated_reservation = Reservation.objects.get(id=reservation.id)
        self.assertEqual(updated_reservation.guests_count, 3)
        self.assertEqual(updated_reservation.duration, 3)

    def test_reservation_update_permission_error(self):
        """Тест обновления брони не владельцем"""

        reservation = Reservation.objects.create(
            user=self.user,
            table=self.table_2,
            start_time=self.future_time,
            duration=2,
            guests_count=2
        )
        user = CustomUser.objects.create(email='test2@mail.com', password='54321test')

        self.client.force_login(user)

        response = self.client.post(
            reverse('restaurant:reservation_update', kwargs={'pk': reservation.pk}),
            data={
                'table': self.table_2.id,
                'start_time': self.future_time,
                'duration': 2,
                'guests_count': 3})

        self.assertIn(response.status_code, [403, 302, 404])

    def test_reservation_list(self):
        """Тест просмотра списка резервов"""
        reservation_1 = Reservation.objects.create(
            user=self.user,
            table=self.table_1,
            start_time=self.future_time,
            duration=2,
            guests_count=2
        )
        reservation_2 = Reservation.objects.create(
            user=self.user,
            table=self.table_2,
            start_time=self.future_time,
            duration=2,
            guests_count=3
        )

        reservations = Reservation.objects.all()

        self.assertEqual(reservations.count(), 2)

    def test_reservation_delete(self):
        """Тест удаления резерва"""
        reservation = Reservation.objects.create(
            user=self.user,
            table=self.table_1,
            start_time=self.future_time,
            duration=2,
            guests_count=2
        )
        self.assertEqual(Reservation.objects.count(), 1)

        reservation.delete()
        self.assertEqual(Reservation.objects.count(), 0)

    def test_form_valid_data(self):
        """Тест формы с валидными данными"""
        form_data = {
            'table': self.table_1.id,
            'start_time': self.future_time,
            'duration': 2,
            'guests_count': 2
        }
        form = ReservationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_guests_count(self):
        """Тест формы с невалидным количеством гостей (более 8)"""
        form_data = {
            'table': self.table_1.id,
            'start_time': self.future_time,
            'duration': 2,
            'guests_count': 10
        }
        form = ReservationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_form_invalid_in_past(self):
        """Тест формы с временем в прошлом"""
        form_data = {
            'table': self.table_1.id,
            'start_time': self.future_time - timedelta(days=5),
            'duration': 2,
            'guests_count': 2
        }
        form = ReservationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_form_invalid_guests_count_else(self):
        """Тест формы с неподходящим количеством гостей для стола (но менее 8)"""
        form_data = {
            'table': self.table_1.id,
            'start_time': self.future_time,
            'duration': 2,
            'guests_count': 6
        }
        form = ReservationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_form_missing_data(self):
        """Тест формы с отсутствующими данными"""
        form_data = {
            'table': self.table_1.id,
        }
        form = ReservationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_is_table_available_service(self):
        """Тест проверки доступности стола"""
        result = is_table_available_service(self.table_2, self.future_time, 2)
        self.assertTrue(result)

    def test_get_available_tables_ajax(self):
        """Тест работы AJAX """
        params = {
            'guests_count': 2,
            'start_time': self.future_time.isoformat(),
            'duration': 2
        }
        response = self.client.get(reverse('restaurant:get_available_tables'), params)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        print("Response data:", data)
        self.assertTrue(data['success'])

    def test_create_tables_options_html(self):
        """Тест генерации HTML"""
        html = create_tables_options_html([self.table_1])
        self.assertIn('Стол 1', html)

    def test_str_method(self):
        """Тест отображения стола в интерфейсе"""
        self.assertEqual(str(self.table_1), "Стол 1")


class SendEmailTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='client@example.com',
            password='12345',
            first_name='client'
        )

    def test_send_email(self):
        """Тест отправления письма на почту из формы обратной связи"""
        send_contact_email(
            self.user.first_name,
            '8925903523',
            'хочу забронировать на 10 человек',
            self.user.email
        )

        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]

        self.assertEqual(email.to, ['my.nik.mariann@gmail.com'])
        self.assertIn('Новая заявка', email.subject)
        self.assertIn(self.user.first_name, email.subject)
        self.assertIn('8925903523', email.body)
        self.assertIn('хочу забронировать на 10 человек', email.body)
