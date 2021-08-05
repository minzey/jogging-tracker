from django.urls import path
from joggingapi import views


urlpatterns = [
    path('jogs/', views.JogCreate.as_view(), name='create_jog_record'),
    path('jogs/<int:pk>', views.JogDetail.as_view(), name='jog_detail'),
    path('reports/weekly-averages/', views.WeeklyJogReport.as_view(), name='weekly_averages_report'),
]