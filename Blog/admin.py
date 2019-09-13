from django.contrib import admin
from .models import Post

class RatingAdmin(admin.ModelAdmin):
    readonly_fields = ('last_updated',)

admin.site.register(Post, RatingAdmin)