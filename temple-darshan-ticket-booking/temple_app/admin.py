# temple_app/admin.py
from django.contrib import admin
from .models import Temple, TicketType, Booking, Donation

@admin.register(Temple)
class TempleAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'established_date')
    search_fields = ('name', 'location')
    list_filter = ('location',)

@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'temple', 'price', 'available_tickets')
    list_filter = ('temple',)
    search_fields = ('name', 'temple__name')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'ticket_type', 'quantity', 'visit_date', 'total_price', 'booking_date', 'status') # <-- Add visit_date
    list_filter = ('status', 'booking_date', 'visit_date', 'ticket_type__temple') # <-- Add visit_date
    search_fields = ('user__username', 'ticket_type__name', 'id')
    readonly_fields = ('booking_date', 'total_price')

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('donor_name_display', 'amount', 'timestamp', 'is_anonymous', 'user')
    list_filter = ('is_anonymous', 'timestamp')
    search_fields = ('donor_name', 'message', 'user__username')
    readonly_fields = ('timestamp',)

    def donor_name_display(self, obj):
        return obj.donor_name if obj.donor_name and not obj.is_anonymous else 'Anonymous'
    donor_name_display.short_description = 'Donor'