# temple_app/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.core.mail import send_mail
from django.conf import settings 
from django.http import JsonResponse 
from django.db.models import Sum 
from django.views.decorators.http import require_POST
from django.forms.models import model_to_dict # To easily convert model instances to dicts
import json # To parse JSON for form errors

# Import all your models
from .models import Temple, TicketType, Booking, Donation

# Import all your forms
from .forms import BookingForm, ContactForm, CustomUserCreationForm, TempleForm, DonationForm 


# --- Core Temple & Booking Views ---

def home_view(request):
    """Displays the home page with a list of temples."""
    temples = Temple.objects.all() 
    return render(request, 'temple_app/home.html', {'temples': temples})

def temple_list_view(request):
    """Displays a comprehensive list of all temples."""
    temples = Temple.objects.all()
    return render(request, 'temple_app/temple_list.html', {'temples': temples})

def temple_detail_view(request, pk):
    """Displays details of a specific temple and its ticket types."""
    temple = get_object_or_404(Temple, pk=pk)
    ticket_types = temple.ticket_types.all()
    return render(request, 'temple_app/temple_detail.html', {'temple': temple, 'ticket_types': ticket_types})

@login_required
def create_booking(request, ticket_type_pk):
    """Handles the creation of a new booking for a specific ticket type."""
    ticket_type = get_object_or_404(TicketType, pk=ticket_type_pk)
    
    if request.method == 'POST':
        form = BookingForm(request.POST, ticket_type=ticket_type)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            # visit_date = form.cleaned_data['visit_date'] # Already handled by form.save()

            with transaction.atomic():
                ticket_type_for_update = TicketType.objects.select_for_update().get(pk=ticket_type_pk)

                if quantity > ticket_type_for_update.available_tickets:
                    messages.error(request, f"Sorry, only {ticket_type_for_update.available_tickets} tickets are now available for {ticket_type_for_update.name}.")
                    return render(request, 'temple_app/create_booking.html', {'form': form, 'ticket_type': ticket_type_for_update})

                booking = form.save(commit=False)
                booking.user = request.user
                booking.ticket_type = ticket_type_for_update
                booking.status = 'confirmed' 
                
                ticket_type_for_update.available_tickets -= quantity
                ticket_type_for_update.save()

                booking.save()
                messages.success(request, 'Your booking has been confirmed!')
                return redirect('booking_success', booking_pk=booking.pk)
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else: 
        form = BookingForm(ticket_type=ticket_type)
    
    return render(request, 'temple_app/create_booking.html', {'form': form, 'ticket_type': ticket_type})

@login_required
def booking_success_view(request, booking_pk):
    """Displays a success page after a booking is confirmed."""
    booking = get_object_or_404(Booking, pk=booking_pk, user=request.user)
    if booking.user != request.user:
        messages.error(request, "You are not authorized to view this booking.")
        return redirect('my_bookings')
    
    return render(request, 'temple_app/booking_success.html', {'booking': booking})

@login_required
def my_bookings_view(request):
    """Displays a list of all bookings made by the logged-in user."""
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    return render(request, 'temple_app/my_bookings.html', {'bookings': bookings})

@login_required
def add_temple_view(request):
    """Handles adding a new temple via a form (admin/staff only typically)."""
    if request.method == 'POST':
        form = TempleForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Temple added successfully!')
            return redirect('home')
    else:
        form = TempleForm()
    
    return render(request, 'temple_app/add_temple.html', {'form': form})

@login_required
def cancel_booking_view(request, booking_pk):
    """Allows a user to cancel their confirmed booking."""
    booking = get_object_or_404(Booking, pk=booking_pk, user=request.user)

    if booking.status == 'cancelled':
        messages.info(request, "This booking has already been cancelled.")
        return redirect('my_bookings')
    
    if request.method == 'POST':
        with transaction.atomic():
            booking_to_cancel = Booking.objects.select_for_update().get(pk=booking_pk)
            
            if booking_to_cancel.status == 'confirmed':
                booking_to_cancel.status = 'cancelled'
                booking_to_cancel.save()

                ticket_type = booking_to_cancel.ticket_type
                ticket_type.available_tickets += booking_to_cancel.quantity
                ticket_type.save()
                
                messages.success(request, f"Booking {booking_pk} has been cancelled successfully. Tickets refunded.")
            else:
                messages.error(request, f"Booking {booking_pk} cannot be cancelled as it's not in 'confirmed' status.")
        return redirect('my_bookings')

    return render(request, 'temple_app/cancel_booking_confirm.html', {'booking': booking})


# --- User Authentication Views ---
class RegisterView(CreateView):
    """View for user registration using a custom form."""
    form_class = CustomUserCreationForm 
    success_url = reverse_lazy('login') 
    template_name = 'registration/register.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Registration successful! Please log in.')
        return response


# --- Static Content & Contact Views ---

def about_us_view(request):
    """Renders the about us page."""
    return render(request, 'temple_app/about.html')

def contact_us_view(request):
    """Handles the contact us form submission and renders the page."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            from_email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            full_message = f"Message from: {name} ({from_email})\n\nSubject: {subject}\n\n{message}"
            
            try:
                send_mail(
                    subject=f"Feedback: {subject}", 
                    message=full_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['your_email@example.com'], # <--- REMEMBER TO REPLACE THIS WITH YOUR ACTUAL EMAIL
                    fail_silently=False,
                )
                messages.success(request, 'Your message has been sent successfully!')
                return redirect('contact_us')
            except Exception as e:
                messages.error(request, f'There was an error sending your message. Please try again later. Error: {e}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactForm()
    
    return render(request, 'temple_app/contact_us.html', {'form': form})

def faq_view(request):
    """Renders the FAQ page."""
    return render(request, 'temple_app/faq.html')


# --- Donation Views (Modified/New) ---

def donations_view(request):
    """
    Renders the donation page with the form and initial donation statistics.
    Uses the 'donations.html' template.
    """
    form = DonationForm() # No 'user' argument here, it's handled in create_donation_ajax
    
    total_donations_amount = Donation.objects.aggregate(Sum('amount'))['amount__sum'] or 0.00
    recent_donations = Donation.objects.all().order_by('-timestamp')[:5] 

    context = {
        'form': form,
        'total_donations': total_donations_amount,
        'recent_donations': recent_donations,
    }
    # Pointing to the new donations.html
    return render(request, 'temple_app/donations.html', context)


@require_POST # Ensures only POST requests are processed
def create_donation_ajax(request):
    """
    API endpoint to handle AJAX submission of donation form data.
    Uses FormData, so data is in request.POST.
    """
    form = DonationForm(request.POST) 

    if form.is_valid():
        donation = form.save(commit=False)
        
        # If user is authenticated, link the donation to them
        if request.user.is_authenticated:
            donation.user = request.user
            # If donor_name is not explicitly provided, default to user's name
            if not donation.donor_name:
                donation.donor_name = request.user.get_full_name() or request.user.username

        # If anonymous is checked, ensure donor_name is null regardless of user
        if donation.is_anonymous:
            donation.donor_name = None 

        donation.save()
        
        return JsonResponse({'status': 'success', 'message': 'Thank you for your generous donation!'})
    else:
        # Form is not valid, return errors in a format the JS can parse
        return JsonResponse({
            'status': 'error', 
            'message': 'Please correct the errors in the form.', 
            'errors': form.errors.as_json() # Returns a JSON string of errors
        }, status=400)


def api_donations_data(request):
    """
    API endpoint to provide total and recent donation data for AJAX updates.
    """
    total_donations_amount = Donation.objects.aggregate(Sum('amount'))['amount__sum'] or 0.00
    recent_donations_queryset = Donation.objects.all().order_by('-timestamp')[:5]

    recent_donations_list = []
    for donation in recent_donations_queryset:
        # Convert model instance to dictionary for easy JSON serialization
        data = model_to_dict(donation, fields=['amount', 'is_anonymous', 'message'])
        
        # Override donor_name logic for display based on template's needs
        if donation.is_anonymous:
            data['donor_name'] = 'Anonymous'
        elif donation.donor_name:
            data['donor_name'] = donation.donor_name
        elif donation.user and donation.user.username:
            data['donor_name'] = donation.user.get_full_name() or donation.user.username
        else:
            data['donor_name'] = 'N/A' # Fallback if no name or user

        # Format timestamp for display in JS
        data['timestamp'] = donation.timestamp.strftime("%b %d, %Y %H:%M") 
        recent_donations_list.append(data)
            
    return JsonResponse({
        'total_donations': total_donations_amount,
        'recent_donations': recent_donations_list
    })