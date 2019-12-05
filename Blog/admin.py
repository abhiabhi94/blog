from django.contrib import admin
from .models import Post, Category
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
        tags_list = [post.get_tags_list()
                     for post in Post.objects.filter(publish=True)]
        all_tags = tuple({(item, item)
                          for outer in tags_list for item in outer})
        return all_tags

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # print (self.value())
        if self.value():
            post_list = Post.objects.filter(
                tags__contains=self.value()).order_by('-date_posted')
            return post_list
        else:
            return queryset.filter()


class CategoryListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('category')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'category'

    def lookups(self, request, model_admin):
        category_list = [category[0]
                         for category in Category.objects.values_list('name')]
        all_categories = tuple({(item, item) for item in category_list})
        return all_categories

    def queryset(self, request, queryset):
        print(self.value())
        if self.value():
            print(">>>>>>", Post.objects.all())
            post_list = Post.objects.filter(
                category__name=self.value()).order_by('-date_posted')
            return post_list
        else:
            return queryset.filter()


class PostAdmin(admin.ModelAdmin):
    readonly_fields = ('slug', 'last_updated',
                       '_content_rendered', 'date_published')
    tags_list = [post.get_tags_list()
                 for post in Post.objects.filter(publish=True)]
    all_tags = list({item for outer in tags_list for item in outer})
    list_filter = ['publish', TagListFilter, CategoryListFilter]


admin.site.register(Post, PostAdmin)
admin.site.register(Category)
