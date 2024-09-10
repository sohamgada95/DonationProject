from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('donation_form/', views.donation_form_view, name='donation_form'),
    path('receipt_choice/', views.receipt_choice_view, name='receipt_choice'),
    path('generate_receipt/', views.generate_receipt_view, name='generate_receipt'),
    path('receipt/<str:receipt_token>', views.generate_receipt_by_token, name='generate_receipt_by_token'),
    path('donations/', views.donations_view, name='donations'),
    path('logout/', views.logout_view, name='logout'),
    path('webhook/', views.github_webhook, name='github_webhook'),
]