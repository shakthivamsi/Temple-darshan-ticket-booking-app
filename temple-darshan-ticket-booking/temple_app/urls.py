# temple_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('temples/', views.temple_list_view, name='temple_list'),
    path('temple/<int:pk>/', views.temple_detail_view, name='temple_detail'),
    path('book/<int:ticket_type_pk>/', views.create_booking, name='create_booking'),
    path('booking_success/<int:booking_pk>/', views.booking_success_view, name='booking_success'),
    path('my_bookings/', views.my_bookings_view, name='my_bookings'),
    path('add_temple/', views.add_temple_view, name='add_temple'),
    path('cancel_booking/<int:booking_pk>/', views.cancel_booking_view, name='cancel_booking'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('about/', views.about_us_view, name='about_us'),
    path('contact/', views.contact_us_view, name='contact_us'),
    path('faq/', views.faq_view, name='faq'),
    path('donate/', views.donations_view, name='donations'), 
    path('api/donate/', views.create_donation_ajax, name='api_create_donation'),
    
    # THIS IS THE LINE THAT NEEDS TO BE MODIFIED:
    # Change 'views.get_donations_data' to 'views.api_donations_data'
    path('api/donations-data/', views.api_donations_data, name='api_donations_data'),
]