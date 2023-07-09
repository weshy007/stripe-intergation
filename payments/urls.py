from django.urls import path

from . import views

urlpatterns = [
    path('', views.product_create, name='create'),
    path('edit/<id>/', views.product_edit, name='edit'),
    path('detail/<id>/', views.PaymentConfirmation.as_view(), name='detail'),
    path('success/', views.payment_success, name='success'),
    path('failed/', views.PaymentFailedView.as_view(), name='failed'),
    path('history/', views.OrderHistoryListView.as_view(), name='history'),
    path('api/checkout-session/<id>/', views.create_checkout_session, name='api_checkout_session'),
]