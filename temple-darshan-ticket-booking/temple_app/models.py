# temple_app/models.py

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator 
from datetime import date # Import date for validation later

class Temple(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='temple_images/', null=True, blank=True)
    established_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name

class TicketType(models.Model):
    temple = models.ForeignKey(Temple, on_delete=models.CASCADE, related_name='ticket_types')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    available_tickets = models.IntegerField(default=0)

    def __str__(self):
        # MODIFIED: Changed $ to ₹
        return f"{self.temple.name} - {self.name} (₹{self.price})"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    visit_date = models.DateField() # Date the user intends to visit
    booking_date = models.DateTimeField(auto_now_add=True) # When the booking was created in the system
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def save(self, *args, **kwargs):
        # This calculation remains currency-agnostic, simply multiplying price by quantity.
        self.total_price = self.ticket_type.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking {self.id} by {self.user.username} for {self.quantity} x {self.ticket_type.name} on {self.visit_date}"
    
class Donation(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='donations')
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)],
        # MODIFIED: Changed $ to ₹ in help_text
        help_text="Minimum donation amount is ₹0.01" 
    )
    donor_name = models.CharField(max_length=100, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_anonymous = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Donation"
        verbose_name_plural = "Donations"

    def __str__(self):
        name = self.donor_name if self.donor_name and not self.is_anonymous else 'Anonymous'
        # MODIFIED: Changed $ to ₹
        return f"{name} donated ₹{self.amount} on {self.timestamp.strftime('%Y-%m-%d %H:%M')}"