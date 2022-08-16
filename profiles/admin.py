from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'date_birth', 'avatar_img', )
    search_fields = ["first_name"]

    def avatar_img(self, model):
        if model.avatar_thumb:
            html = '<div style="text-align:center;"><img src="%s" width = "100px;"/></div>' % model.avatar_thumb.url
        else:
            html = '<p style="text-align:center;color:red;">Аватар не загружен</p>'
        return mark_safe(html)

    avatar_img.short_description = 'Аватар'
    avatar_img.allow_tags = True
    readonly_fields = ['avatar_img']
