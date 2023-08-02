from django.contrib import admin

from tags.models import Tag


@admin.register(Tag)
class TagsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name', 'slug')
