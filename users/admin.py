from django.contrib import admin

# Register your models here.
from .models import User, UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    ordering = ('email',)
    list_display = ('email', 'name' , 'role' , 'date_joined')
    search_fields = ('email', 'name', 'role')
    ordering = ('email',)
    inlines = (UserProfileInline, )

