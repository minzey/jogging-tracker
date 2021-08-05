from datetime import datetime, timedelta

from rest_framework import generics
from rest_framework.views import APIView
from django.http import JsonResponse

from .models import JogRecord
from userapi.models import FitnessUser
from .serializers import JogRecordSerializer
from .permissions import IsJogRecordOwnerOrStaff
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, NotFound

from .reports import weekly_distance_and_speed_average


class JogCreate(generics.CreateAPIView):
    """
    API for creating jog records
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = JogRecordSerializer

class JogList(generics.ListAPIView):
    # todo: add filter queryset support
    pass


class JogDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    API for fetching Jog records
    """

    queryset = JogRecord.objects.all()
    serializer_class = JogRecordSerializer
    permission_classes = [IsJogRecordOwnerOrStaff,]

class WeeklyJogReport(APIView):
    """
    Computes weekly jog report
    """
    permission_classes = [IsAuthenticated,]

    def validate(self, jogger):
        logged_in_user_role = FitnessUser.get_auth_role(self.request.user.id)

        if self.request.user == jogger:
            # can access self report
            return True

        if logged_in_user_role == FitnessUser.Role.ADMIN.value:
            return True

        else:
            raise PermissionDenied("You cannot access other users' reports!")

    def get(self, request):

        jogger_id = request.data.get('jogger_id', request.user.id)
        try:
            jogger = FitnessUser.objects.get(id=jogger_id)
        except FitnessUser.DoesNotExist:
            raise NotFound(f"Jogger with user_id = {jogger_id} does not exist! Please try again with a different id.")
        self.validate(jogger)

        date = request.data.get('date', None)
        if date is None:
            date = datetime.today().date()
        else:
            date = datetime.strptime(date, "%Y-%m-%d")

        week_start_date = date - timedelta(days=date.weekday())
        week_end_date = week_start_date + timedelta(days=6)

        report_data = weekly_distance_and_speed_average(jogger, week_start_date, week_end_date)
        return JsonResponse(report_data)









