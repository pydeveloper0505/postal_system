from django.views.generic import ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from .models import Notification


class NotificationListView(LoginRequiredMixin, ListView):
    model               = Notification
    template_name       = 'notifications/list.html'
    context_object_name = 'notifications'
    paginate_by         = 20

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class MarkAllReadView(LoginRequiredMixin, View):
    def post(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return redirect('notifications:list')


class MarkReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        Notification.objects.filter(pk=pk, user=request.user).update(is_read=True)
        return redirect('notifications:list')
