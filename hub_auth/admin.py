from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from hub_auth.models import Account, GroupProxy, APIKey

admin.site.unregister(Group)
# Register our Proxy with GroupAdmin from Django
admin.site.register(GroupProxy, GroupAdmin)


@admin.register(Account)
class AccountAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('organization', 'username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    list_display = ('username', 'organization', 'email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'organization')


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'account', 'api_key')