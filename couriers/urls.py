from django.urls import path
from .views import CourierDashboardView, UpdateOrderStatusView

app_name = 'couriers'

urlpatterns = [
    path('',                     CourierDashboardView.as_view(),  name='dashboard'),
    path('<int:pk>/update/',     UpdateOrderStatusView.as_view(), name='update-status'),
]
