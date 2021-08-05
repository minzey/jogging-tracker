from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import FitnessUser

class FitnessUserAdmin(UserAdmin):
    model = FitnessUser
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )

admin.site.register(FitnessUser, FitnessUserAdmin)
