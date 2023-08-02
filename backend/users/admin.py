from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import FoodGramUser, Subscribe


@admin.register(FoodGramUser)
class FoodGramUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (
            'Персональная информация',
            {'fields': ('first_name', 'last_name', 'email')},
        ),
        (
            'Разрешения',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                ),
            },
        ),
        ('Даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'username',
                    'first_name',
                    'last_name',
                    'email',
                    'password1',
                    'password2',
                ),
            },
        ),
    )

    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('id',)


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('user', 'author')
    ordering = ('user',)


admin.site.site_header = 'Администрирование FOODGRAM Project'
admin.site.site_title = 'FOODGRAM Project'
admin.site.index_title = 'FOODGRAM Project'
