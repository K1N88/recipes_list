from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('id', 'email', 'username')
    list_filter = ('email', 'username')
    search_fields = ('email', 'username')
    ordering = ('username',)


admin.site.register(CustomUser, CustomUserAdmin)
