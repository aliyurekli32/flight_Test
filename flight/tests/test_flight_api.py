from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from rest_framework.authtoken.models import Token

from flight.views import FlightView
from flight.models import Flight

from datetime import datetime, date


class FlightTestCase(APITestCase):
    now = datetime.now()
    current_time = now.strftime('%H:%M:%S')
    today = date.today()

    def setUp(self):
        self.factory = APIRequestFactory()
        self.flight = Flight.objects.create(
            flight_number='123ABC',
            operation_airlines='THY',
            departure_city='Adana',
            arrival_city='Ankara',
            date_of_departure=f'{self.today}',
            etd=f'{self.current_time}',
        )
        self.user = User.objects.create_user(
            username='admin',
            password='Aa654321*'
        )
        self.token = Token.objects.get(user=self.user)

    def test_flight_lis_as_non_auth_user(self):
        request = self.factory.get(
            '/flight/flights/')
        # print(reverse('flights-list'))
        response = FlightView.as_view({'get': 'list'})(request)
        print(response)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'reservation')
        self.assertEqual(len(response.data), 0)

    def test_flight_list_as_staff_user(self):
        request = self.factory.get(
            '/flight/flights/', HTTP_AUTHORIZATION=f'Token {self.token}')
        self.user.is_staff = True
        self.user.save()
        # force_authenticate(request, user=self.user)
        request.user = self.user
        response = FlightView.as_view({'get': 'list'})(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'reservation')
        self.assertEqual(len(response.data), 1)

    def test_flight_create_as_non_auth_user(self):
        request = self.factory.post(
            '/flight/flights/')
        response = FlightView.as_view({'post': 'create'})(request)
        self.assertEqual(response.status_code, 401)

    def test_flight_create_as_auth_user(self):
        request = self.factory.post(
            '/flight/flights/', HTTP_AUTHORIZATION=f'Token {self.token}')

        # request.user = self.user
        response = FlightView.as_view({'post': 'create'})(request)
        self.assertEqual(response.status_code, 403)

    def test_flight_create_as_staff_user(self):
        data = {
            "flight_number": "123ABC",
            "operation_airlines": "THY",
            "departure_city": "Adana",
            "arrival_city": "Ankara",
            "date_of_departure": "2022-01-08",
            "etd": "16:35:00",
        }
        self.user.is_staff = True
        self.user.save()
        request = self.factory.post(
            '/flight/flights/', data, HTTP_AUTHORIZATION=f'Token {self.token}')

        response = FlightView.as_view({'post': 'create'})(request)
        self.assertEqual(response.status_code, 201)

    def test_flight_update_as_staff_user(self):
        data = {
            "flight_number": "456ewd",
            "operation_airlines": "THY",
            "departure_city": "Adana",
            "arrival_city": "Ankara",
            "date_of_departure": "2022-01-08",
            "etd": "16:35:00",
        }
        print(self.flight.id)

        self.user.is_staff = True
        self.user.save()
        request = self.factory.put(
            '/flight/flights/1/', data, HTTP_AUTHORIZATION=f'Token {self.token}')

        response = FlightView.as_view(
            {'put': 'update'})(request, pk='1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Flight.objects.get(id=1).flight_number, '456ewd')

        # self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        # response = self.client.put(
        #     '/flight/flights/1/', data, format='json')
        # self.assertEqual(response.status_code, 200)
        # self.assertEqual(Flight.objects.get().flight_number, '456ewd')
