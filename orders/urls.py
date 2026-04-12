from django.urls import path
from .views import (
    OrderListView, OrderDetailView, OrderCreateView,
    MockPaymentView, TrackOrderView,
    AdminDashboardView, AssignCourierView,
)

app_name = 'orders'

urlpatterns = [
    path('',                    OrderListView.as_view(),       name='list'),
    path('create/',             OrderCreateView.as_view(),     name='create'),
    path('<int:pk>/',           OrderDetailView.as_view(),     name='detail'),
    path('<int:pk>/pay/',       MockPaymentView.as_view(),     name='payment'),
    path('track/',              TrackOrderView.as_view(),      name='track'),
    # Admin
    path('admin/dashboard/',    AdminDashboardView.as_view(),  name='admin-dashboard'),
    path('admin/assign/<int:order_pk>/', AssignCourierView.as_view(), name='assign-courier'),
]
