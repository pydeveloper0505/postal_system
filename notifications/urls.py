from django.urls import path
from .views import NotificationListView, MarkAllReadView, MarkReadView

app_name = 'notifications'

urlpatterns = [
    path('',              NotificationListView.as_view(), name='list'),
    path('mark-all/',     MarkAllReadView.as_view(),      name='mark-all-read'),
    path('<int:pk>/read/', MarkReadView.as_view(),        name='mark-read'),
]
