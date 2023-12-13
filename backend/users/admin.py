from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    search_fields = ('username',)
    list_display_links = ('username',)
    list_filter = ('username', 'email')


admin.site.empty_value_display = 'Не задано'
