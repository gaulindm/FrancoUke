from django.contrib import admin
from .models import Gig, Availability  # ✅ Removed Player

class AvailabilityInline(admin.TabularInline):
    model = Availability
    extra = 0

@admin.register(Gig)
class GigAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'location')
    inlines = [AvailabilityInline]

@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ('gig', 'player', 'status')
    list_filter = ('gig', 'status')
