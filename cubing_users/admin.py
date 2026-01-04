# cubing_users/admin.py
from django.contrib import admin
from .models import Cuber, Leader, Group, GroupMembership


@admin.register(Cuber)
class CuberAdmin(admin.ModelAdmin):
    list_display = ['get_identity', 'avatar_variant', 'created_date', 'last_active_date']
    list_filter = ['color', 'created_date', 'last_active_date']
    search_fields = ['color', 'adjective', 'superhero']
    readonly_fields = ['cuber_id', 'color_code_hash', 'created_date', 'last_active_date']
    
    def get_identity(self, obj):
        return f"{obj.color} {obj.adjective} {obj.superhero}"
    get_identity.short_description = 'Identité'
    
    fieldsets = (
        ('Identité', {
            'fields': ('cuber_id', 'color', 'adjective', 'superhero', 'avatar_variant')
        }),
        ('Sécurité', {
            'fields': ('color_code_hash',),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_date', 'last_active_date')
        }),
    )


@admin.register(Leader)
class LeaderAdmin(admin.ModelAdmin):
    list_display = ['get_name', 'role', 'organization', 'created_date']
    list_filter = ['role', 'created_date']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'organization']
    
    def get_name(self, obj):
        return obj.user.get_full_name()
    get_name.short_description = 'Nom'


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['group_name', 'group_code', 'group_type', 'get_member_count', 'created_date']
    list_filter = ['group_type', 'created_date']
    search_fields = ['group_name', 'group_code']
    readonly_fields = ['group_id', 'group_code', 'created_date']
    filter_horizontal = ['leaders']
    
    def get_member_count(self, obj):
        return obj.groupmembership_set.filter(status='active').count()
    get_member_count.short_description = 'Membres'


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ['get_cuber', 'get_group', 'status', 'joined_date']
    list_filter = ['status', 'joined_date', 'group']
    search_fields = ['cuber__color', 'cuber__adjective', 'cuber__superhero', 'group__group_name']
    date_hierarchy = 'joined_date'
    
    def get_cuber(self, obj):
        return f"{obj.cuber.color} {obj.cuber.adjective} {obj.cuber.superhero}"
    get_cuber.short_description = 'Cubeur'
    
    def get_group(self, obj):
        return obj.group.group_name
    get_group.short_description = 'Groupe'
