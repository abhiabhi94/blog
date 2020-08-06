from django.contrib.auth.models import User
from django.shortcuts import reverse

from Blog.tests.base import TestPostBase, Post


class TestPostModel(TestPostBase):

    @classmethod
    def setUpClass(cls):
        """
        Initialise data for all tests
        - Create an draft post
        - Create a user and associate them with a new post.
        """
        super().setUpClass()
        # Create a draft post
        cls.draft_post = cls.create_post(
            title='This is a draft post',
            tags='t1, draft',
            category=cls.category
        )
        # Create a published post
        cls.post = cls.create_post(
            title='This is published post',
            tags='test, published',
            category=cls.category,
            state=Post.Status.PUBLISH.value
        )

        # Create a queued post
        cls.queued_post = cls.create_post(
            title='This is queued post',
            tags='test, queued',
            category=cls.category,
            state=Post.Status.QUEUE.value
        )

    def test_max_length_title(self):
        """Test max length for title of an post is 60"""
        post = self.post
        max_length = post._meta.get_field('title').max_length
        self.assertEqual(max_length, 80)

    def test_max_length_slug(self):
        """Test max length for slug of an post is 80"""
        post = self.post
        max_length = post._meta.get_field('slug').max_length
        self.assertEqual(max_length, 80)

    def test_default_post_state(self):
        """Test whether posts will by default be a draft state"""
        post = self.draft_post
        self.assertEqual(post.state, Post.Status.DRAFT.value)

    def test_post_object_name(self):
        """Test that the title is returned when the object is printed"""
        post = self.post
        self.assertEqual(str(post), post.title)

    def test_get_absolute_url(self):
        """Test whether model returns correct url for detail view of an post"""
        post = self.post
        # We can't exactly test the exact url since there are random characters added to the slug
        self.assertEqual(post.get_detail_url(), reverse('Blog:post-detail', kwargs={
            'slug': post.slug,
            'year': post.date_published.year,
            'month': post.date_published.month,
            'day': post.date_published.day
        }))

    def test_meta_data_for_seo(self):
        """Test meta-information about the model that will be used for SEO functionalities"""
        post = self.post
        self.assertEqual(post._get_meta_author(), post.author.get_full_name())
        self.assertIsNotNone(post._get_meta_description())
        self.assertEqual(post._get_meta_image(), post.thumbnail.url)

    def test_slug_change(self):
        """Test slug changes only when asked"""
        post = self.post
        slug = post.slug

        self.assertIsNotNone(slug)

        post.title = 'new title'
        post.save()

        self.assertEqual(post.slug, slug)

        # change slug
        post.slug_change = True
        post.save()

        self.assertEqual(post.slug, 'new-title')

    def test_views(self):
        """"Test view property"""
        self.assertEqual(self.draft_post.views, 0)
        self.assertEqual(self.queued_post.views, 0)

        post = self.post
        post.refresh_from_db()
        self.assertEqual(post.views, 0)

        # test view increase when a url is visited
        self.client.logout()
        response = self.client.get(post.get_detail_url())
        self.assertEqual(response.context['post'].views, 1)
        post.refresh_from_db()
        # check the change in the database
        self.assertEqual(post.views, 1)

    def test_preview_url(self):
        post = self.draft_post
        self.assertEqual(post.get_preview_url(), reverse('Blog:post-preview', kwargs={
            'slug': post.slug
        }))

    def test_thumbnail_generation(self):
        """Test thumbnail is generated when image changes"""
        pass

    def test_image_compression(self):
        """Test GIF images aren't compressed, image size saved is smaller than the one uploaded"""
        pass


class TestPostManager(TestPostBase):
    """Test custom functions used for the manager object"""

    def test_get_queryset(self):
        total = self.num_published + self.num_drafts + self.num_queued
        self.assertEqual(total, len(Post.objects.all()))

    def test_get_published(self):
        result = Post.objects.get_published()
        self.assertEqual(self.num_published, len(result))
        self.assertEqual(['Published' in r['title'] for r in result.values('title')], [
                         True]*self.num_published)

    def test_get_draft(self):
        result = Post.objects.get_draft()
        self.assertEqual(self.num_drafts, len(result))
        self.assertEqual(['Draft' in r['title'] for r in result.values('title')], [
                         True]*self.num_drafts)

    def test_get_queued(self):
        result = Post.objects.get_queued()
        self.assertEqual(self.num_queued, len(result))
        self.assertEqual(['Queued' in r['title'] for r in result.values('title')], [
                         True]*self.num_queued)

    def test_latest_entry(self):
        self.assertEqual(Post.objects.get_published().first(
        ).date_published, Post.objects.latest_entry())