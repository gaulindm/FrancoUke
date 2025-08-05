from django.contrib import admin
from .models import Venue, Gig, Availability  # ✅ Removed Player

class AvailabilityInline(admin.TabularInline):
    model = Availability
    extra = 0



@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("name", "location")
    search_fields = ("name", "location")


@admin.register(Gig)
class GigAdmin(admin.ModelAdmin):
    list_display = ("title", "venue", "date", "start_time", "end_time", "arrive_by")
    list_filter = ("venue", "date")
    search_fields = ("title", "venue__name")
    ordering = ("venue", "date", "start_time")

    actions = ["duplicate_gigs"]

    @admin.action(description="Duplicate selected gigs")
    def duplicate_gigs(self, request, queryset):
        for gig in queryset:
            gig.pk = None        # Remove primary key to create a new object
            gig.title = f"{gig.title} (copy)"  # Optional: mark as copy
            gig.save()