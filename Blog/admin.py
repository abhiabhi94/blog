from django.contrib import admin
from .models import Post
from datetime import date

from django.utils.translation import gettext_lazy as _

class TagListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('tag')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'tags'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        # return (
        #     ('80s', _('in the eighties')),
        #     ('90s', _('in the nineties')),
        # )
        tags_list = [post.get_tags_list()
                     for post in Post.objects.filter(publish=True)]
        all_tags = tuple({(item, item) for outer in tags_list for item in outer})
        return all_tags

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        # if self.value() == '80s':
        #     return queryset.filter()
        print (self.value())
        if self.value():
            post_list = Post.objects.filter(
                tags__contains=self.value()).order_by('-date_posted')
            return post_list
        else:
            return queryset.filter()

class RatingAdmin(admin.ModelAdmin):
    readonly_fields = ('last_updated', '_content_rendered')
    tags_list = [post.get_tags_list()
                    for post in Post.objects.filter(publish=True)]
    all_tags = list({item for outer in tags_list for item in outer})
    list_filter = ['publish', TagListFilter,]

admin.site.register(Post, RatingAdmin)
