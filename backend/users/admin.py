from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import FoodgramUser, Subscribe


class UserAdmin(UserAdmin):
    model = FoodgramUser
    list_display = ('id', 'email', 'username')
    list_filter = ('email', 'username')
    search_fields = ('email', 'username')
    ordering = ('username',)


admin.site.register(FoodgramUser, UserAdmin)
admin.site.register(Subscribe)
