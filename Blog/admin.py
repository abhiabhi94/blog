from django.contrib import admin
from .models import Post

class RatingAdmin(admin.ModelAdmin):
    readonly_fields = ('last_updated', '_content_rendered')
    list_filter = ['publish']

admin.site.register(Post, RatingAdmin)