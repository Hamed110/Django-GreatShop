from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Account

class AccountAdmin(UserAdmin):
    list_display = ['email', 'first_name', 'last_name']
    list_display_links = ['email',]
    list_filter = ['is_admin', 'is_staff', 'is_active']
    exclude = []
    readonly_fields = ['password','date_joined', 'last_login']
    ordering = ['-date_joined',]
    search_fields = ['email',]
    fieldsets = [
        ('Personal information', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Account information', {'fields': ('email', 'username', 'password', 'is_active')}),
        ('Permissions', {'fields': ('is_superadmin', 'is_admin', 'is_staff')}),
        ('Join and login information',{'fields': ('date_joined', 'last_login')})
    ]
    add_fieldsets = []
    filter_horizontal = []

admin.site.register(Account, AccountAdmin)
