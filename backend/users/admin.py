from django.contrib import admin
from django.contrib.admin import display
from django.contrib.auth.admin import UserAdmin

from users.models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'subscribers',
        'recipes'
    )
    search_fields = ('username',)
    list_display_links = ('username',)
    list_filter = ('username', 'email')

    @display(description='Подписчиков')
    def subscribers(self, obj):
        return obj.subscribing.count()

    @display(description='Рецепты')
    def recipes(self, obj):
        return obj.recipe.count()


admin.site.empty_value_display = 'Не задано'
