# temple_app/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from datetime import date # Import date for validation of visit_date

from django.core.validators import MinValueValidator # Make sure this import is there!
from .models import Booking, TicketType, Temple, Donation # Import all necessary models


# --- 1. Booking Form ---
class BookingForm(forms.ModelForm):
    """
    Form for creating new bookings, including quantity and visit date.
    Handles validation for available tickets and past dates.
    """
    class Meta:
        model = Booking
        fields = ['quantity', 'visit_date']
        widgets = {
            'visit_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.ticket_type = kwargs.pop('ticket_type', None)
        super().__init__(*args, **kwargs)
        
        if self.ticket_type:
            # Set min/max attributes for the quantity field based on available tickets
            self.fields['quantity'].widget.attrs['min'] = 1
            self.fields['quantity'].widget.attrs['max'] = self.ticket_type.available_tickets
        
        # Optionally set a default initial value for the date picker (e.g., today)
        if not self.instance.pk: # Only for new forms (not for editing existing bookings)
            self.fields['visit_date'].initial = date.today()

    def clean_quantity(self):
        """Validates that the requested quantity does not exceed available tickets."""
        quantity = self.cleaned_data['quantity']
        if self.ticket_type and quantity > self.ticket_type.available_tickets:
            raise forms.ValidationError(f"Only {self.ticket_type.available_tickets} tickets available for this type.")
        return quantity

    def clean_visit_date(self):
        """Validates that the visit date is not in the past."""
        visit_date = self.cleaned_data['visit_date']
        if visit_date < date.today():
            raise forms.ValidationError("The visit date cannot be in the past.")
        return visit_date


# --- 2. Custom User Registration Form ---
class CustomUserCreationForm(UserCreationForm):
    """
    Custom form for user registration, extending Django's UserCreationForm
    to include first name, last name, and email.
    """
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional')
    last_name = forms.CharField(max_length=150, required=False, help_text='Optional')
    email = forms.EmailField(max_length=254, help_text='Required. Your email address.')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email',)

    def clean_email(self):
        """Validates that the email address is not already in use."""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email


# --- 3. Temple Form ---
class TempleForm(forms.ModelForm):
    """
    Form for adding or editing Temple details.
    """
    class Meta:
        model = Temple
        fields = ['name', 'location', 'description', 'image', 'established_date']
        widgets = {
            'established_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }


# --- 4. Contact Form ---
class ContactForm(forms.Form):
    """
    Form for general contact inquiries.
    """
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Your Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Your Email'}))
    subject = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'placeholder': 'Subject'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Your Message', 'rows': 5}))
    

# --- 5. Donation Form ---
class DonationForm(forms.ModelForm):
    """
    Form for making donations.
    Includes validation for amount and optional fields for donor name and message.
    """
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)], # Ensures amount is at least 0.01
        widget=forms.NumberInput(attrs={'min': '0.01', 'step': '0.01'}),
        help_text="Enter the amount you wish to donate (e.g., 500.00)."
    )

    class Meta:
        model = Donation # Ensure Donation model is imported
        fields = ['amount', 'donor_name', 'message', 'is_anonymous']
        widgets = {
            'donor_name': forms.TextInput(attrs={'placeholder': 'Your Name (optional)'}),
            'message': forms.Textarea(attrs={'placeholder': 'A short message (optional)', 'rows': 3}),
        }
        labels = {
            'amount': 'Donation Amount (₹)', # Updated label to show Indian Rupee symbol
            'is_anonymous': 'Donate Anonymously',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None) # Pop the 'user' from kwargs if passed
        super().__init__(*args, **kwargs)

        # Set initial donor_name if user is authenticated and hasn't provided one
        if self.user and self.user.is_authenticated and not self.initial.get('donor_name'):
            # Use get_full_name() first, fallback to username
            self.fields['donor_name'].initial = self.user.get_full_name() or self.user.username

        # Make donor_name, message, and is_anonymous fields not required by default
        # The 'required' attribute on the model field defaults to True for CharField etc.
        # This explicitly overrides that for these optional fields.
        for field_name in ['donor_name', 'message', 'is_anonymous']:
            if field_name in self.fields: # Check if the field exists in the form
                self.fields[field_name].required = False

    def clean(self):
        """Custom clean method for additional form-wide validation if needed."""
        cleaned_data = super().clean()
        # You could add logic here, e.g., if is_anonymous is checked, ensure donor_name is empty
        # However, the view already handles setting donor_name to None based on is_anonymous,
        # so often no form-level validation is needed for this specific case.
        return cleaned_data