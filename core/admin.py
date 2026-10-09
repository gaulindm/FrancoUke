from django.contrib import admin
from .models import Group, GroupMembership, GroupContact


class GroupMembershipInline(admin.TabularInline):
    model = GroupMembership
    extra = 1
    autocomplete_fields = ["user"]


class GroupContactInline(admin.TabularInline):
    model = GroupContact
    extra = 1
    max_num = GroupContact.MAX_PER_GROUP


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent", "is_active", "created_at")
    list_filter = ("parent", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [GroupContactInline, GroupMembershipInline]


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "group", "role", "joined_at")
    list_filter = ("group", "role")
    autocomplete_fields = ["user"]