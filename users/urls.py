from django.urls import path
from .views import (
    RegisterView, CustomLoginView, CustomLogoutView,
    ProfileView, AddressListView, AddressCreateView,
    CourierListView, CourierDetailView, LeaveReviewView,
)

app_name = 'users'

urlpatterns = [
    path('register/',                RegisterView.as_view(),       name='register'),
    path('login/',                   CustomLoginView.as_view(),     name='login'),
    path('logout/',                  CustomLogoutView.as_view(),    name='logout'),
    path('profile/',                 ProfileView.as_view(),         name='profile'),
    path('addresses/',               AddressListView.as_view(),     name='addresses'),
    path('addresses/add/',           AddressCreateView.as_view(),   name='address-add'),
    path('couriers/',                CourierListView.as_view(),     name='courier-list'),
    path('couriers/<int:pk>/',       CourierDetailView.as_view(),   name='courier-detail'),
    path('review/<int:order_pk>/',   LeaveReviewView.as_view(),     name='leave-review'),
]
