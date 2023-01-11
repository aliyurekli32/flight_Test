from django.shortcuts import render
from rest_framework import viewsets
from .serializers import FlightSerializer, ReservationSerializer, StaffFlightSerializer
from .models import Flight, Reservation
from rest_framework.permissions import IsAdminUser
from .permissions import IsStafforReadOnly
from datetime import datetime, date
from django.db.models import Q

# Create your views here.


class FlightView(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    permission_classes = (IsStafforReadOnly,)

    def get_serializer_class(self):
        serializer = super().get_serializer_class()
        if self.request.user.is_staff:
            return StaffFlightSerializer
        return serializer

    def get_queryset(self):
        now = datetime.now()
        current_time = now.strftime('%H:%M:%S')
        today = date.today()

        if self.request.user.is_staff:
            return super().get_queryset()

        else:
            # queryset = Flight.objects.filter(date_of_departure__gt=today)

            # if Flight.objects.filter(date_of_departure=today):
            #     today_qs = Flight.objects.filter(
            #         date_of_departure=today).filter(etd__gt=current_time)

            #     queryset = queryset.union(today_qs)
            # return queryset
            return Flight.objects.filter(Q(date_of_departure__gt=today) | Q(date_of_departure=today, etd__gt=current_time))


class ReservationView(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(user=self.request.user)
