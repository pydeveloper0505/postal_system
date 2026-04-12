from django.urls import path
from .views import RegisterView, CustomLoginView, CustomLogoutView, ProfileView, AddressListView, AddressCreateView

app_name = 'users'

urlpatterns = [
    path('register/', RegisterView.as_view(),    name='register'),
    path('login/',    CustomLoginView.as_view(),  name='login'),
    path('logout/',   CustomLogoutView.as_view(), name='logout'),
    path('profile/',  ProfileView.as_view(),      name='profile'),
    path('addresses/',       AddressListView.as_view(),   name='addresses'),
    path('addresses/add/',   AddressCreateView.as_view(), name='address-add'),
]
