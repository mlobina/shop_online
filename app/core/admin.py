from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _

from core import models


class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'name', 'company', 'position']
    fieldsets = (
        (None, {'fields': ('email', 'password', 'type',)}),
        (_('Personal Info'), {'fields': ('name', 'company', 'position',)}),
        (
            _('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser')}
        ),
        (_('Important dates'), {'fields': ('last_login',)})
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )


class ContactAdmin(admin.ModelAdmin):
    list_display = ['city', 'street', 'house', 'structure', 'building', 'apartment', 'phone']


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Contact, ContactAdmin)
