from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone', 'email', 'is_superuser', 'is_staff', )
    search_fields = ["username"]
