from django.urls import path
from . import views

urlpatterns = [
    path('notifications/', views.NotificationListView.as_view(),name = 'notification-list'),
    path('notifications/count/', views.NotificationCountView.as_view(),name = 'notification-count'),
    path('notifications/read/', views.NotificationReadView.as_view(),name = 'notification-read')
]
