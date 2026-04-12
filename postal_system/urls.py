from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from orders.views import HomeView

urlpatterns = [
    path('admin/',         admin.site.urls),
    path('',               HomeView.as_view(),        name='home'),
    path('users/',         include('users.urls',        namespace='users')),
    path('orders/',        include('orders.urls',       namespace='orders')),
    path('couriers/',      include('couriers.urls',     namespace='couriers')),
    path('notifications/', include('notifications.urls',namespace='notifications')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
