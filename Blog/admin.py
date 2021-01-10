from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from taggit.models import Tag

from Blog.models import Category, Post


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

        tags_list = Tag.objects.values_list('slug', flat=True)
        all_tags = [(tag, tag) for tag in tags_list]
        return all_tags

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            post_list = Post.objects.filter(
                tags__slug=self.value()).order_by('-date_published')
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
                         for category in Category.objects.values_list('name').order_by('name')]
        all_categories = tuple({(item, item) for item in category_list})
        return all_categories

    def queryset(self, request, queryset):
        # print(self.value())
        if self.value():
            # print(">>>>>>", Post.objects.all())
            post_list = Post.objects.filter(
                category__name=self.value()).order_by('-date_published')
            return post_list
        else:
            return queryset.filter()


class AuthorListFilter(admin.SimpleListFilter):
    title = _('Authors')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'author'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        author_list = User.objects.filter(
            groups__name='editor').values('id', 'username')
        authors = tuple((author['id'], author['username'])
                        for author in author_list)
        return authors

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            post_list = Post.objects.filter(
                author=self.value()).order_by('-date_created')
            return post_list
        else:
            return queryset.filter()


class PostAdmin(admin.ModelAdmin):
    readonly_fields = ('slug', 'last_updated', 'views',
                       'date_published', 'thumbnail', 'trending_score')
    list_display = ('title', 'author', 'views', 'date_created',
                    'date_published', 'state', 'featured', 'tag_list',
                    'trending_score')
    autocomplete_fields = ('category',)
    search_fields = ['author__username', 'slug', 'tags__name']

    actions = [
        # 'make_published',
        'make_featured'
    ]

    def view_on_site(self, obj):
        """
        This function is overriden because we don't have a get_absolute_url method in the model
        It will return the preview url
        """
        url = str(obj.get_preview_url())
        if settings.DEBUG:
            return 'http://localhost:8000' + url
        return settings.META_SITE_PROTOCOL + '://' + settings.META_SITE_DOMAIN + url

    # This function {make_published} is commented as:
    # -> This can be misused hence you want the admins to publish\
    #     articles after they have read
    # -> The implementation is tough. When an article is set to Publish\
    #     i.e its state is set to 1, a couple of stuff has to be done and and insured\
    #         which even applied to n number of articles would also raise issue about raising\
    #             appropriate errors for corresponding articles.
    # -> Even you want to use this function, use it only in cases of emergency.

    # def make_published(self, request, queryset):
    #     """Add action to publish many articles in 1 go"""
    #     rows_updated = queryset.update(state=1)
    #     if rows_updated == 1:
    #         message_bit = '1 article was'
    #     else:
    #         message_bit = f'{rows_updated} articles were'

    #     self.message_user(
    #         request, f'{message_bit} were successfully marked as published')

    # make_published.short_description = 'Mark selected articles as published'

    def make_featured(self, request, queryset):
        """Add action to set article as featured for many articles in 1 go"""
        rows_updated = queryset.update(featured=True)
        if rows_updated == 1:
            message_bit = '1 article was'
        else:
            message_bit = f'{rows_updated} articles were'

        self.message_user(
            request, f'{message_bit} were successfully marked as featured')

    make_featured.short_description = 'Mark selected articles as featured'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    def tag_list(self, obj):
        return ", ".join(o.name for o in obj.tags.all())

    list_filter = [AuthorListFilter, 'state', 'featured',
                   TagListFilter, CategoryListFilter]


class CategoryAdmin(admin.ModelAdmin):
    readonly_fields = ['slug']
    list_display = ('name', 'author', 'date_created', 'slug')
    search_fields = ('name', )


admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
