from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import ProducerProfile, CustomerProfile

#Load producer profiles
class ProducerProfileInline(admin.StackedInline):
    model = ProducerProfile
    can_delete = False
    extra = 0

#Load customer profiles
class CustomerProfileInline(admin.StackedInline):
    model = CustomerProfile
    can_delete = False
    extra = 0

#admin users
class UserAdmin(BaseUserAdmin):
    inlines = [ProducerProfileInline, CustomerProfileInline]


# Unregister original User admin
admin.site.unregister(User)

# Register new User admin
admin.site.register(User, UserAdmin)

#Register profile (producer)
@admin.register(ProducerProfile)
class ProducerProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "business_name", "postcode")

#Register profile (customer)
@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "full_name", "postcode")