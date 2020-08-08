import json

from django.shortcuts import reverse

from tests.base import TestBaseView, TestAJAXView
from Blog.tests.base import TestPostBase, Post


class TestAboutPage(TestBaseView):
    def test_about_page(self):
        """Test whether about page link is working"""
        response = self.client.get(reverse('Blog:about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Blog/about.html')


class TestImageLicensePage(TestBaseView):
    def test_content_policy_page(self):
        """Test whether content policy page link is working"""
        response = self.client.get(reverse('image-license'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Blog/image_license.html')


class TestPrivacyPolicyPage(TestBaseView):
    def test_privacy_policy_page(self):
        """Test whether privacy policy page link is working"""
        response = self.client.get(reverse('privacy-policy'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Blog/privacy_policy.html')


class TestRecommendedArticles(TestPostBase, TestAJAXView):

    def get_url(self):
        return reverse('Blog:recommended-posts')

    def test_get_recommended_articles(self):
        """
        Test that
        - all articles are unique
        - articles doesn't contain itself
        - length of the article received when similar objects are lesser than the number requested\
            trending articles fill in the space
        """

        post = self.post
        num = 6
        data = {
            'data': json.dumps({'slug': post.slug, 'top_n': num})
        }
        response = self.request(self.get_url(), data=data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'post_latest_home.html')

        context = response.context
        result = context['posts']

        # this is used for displaying card view in template
        self.assertEqual(context['recommend'], True)
        # test length of article received.
        self.assertEqual(len(result), num)
        # test uniqueness
        self.assertEqual(len(result), len(set(result)))
        # test aricle doesn't contain itself
        self.assertEqual(post in result, False)

    def test_bad_request(self):
        response = self.request(self.get_url(), data={'a': 'a'})
        self.assertEqual(response.status_code, 400,
                         msg='Wrong Request Format for post request')

    def test_get_popular_categories(self):
        pass

    def test_get_popular_tags(self):
        pass

    def test_get_trending_posts(self):
        pass


class TestLatestArticles(TestPostBase, TestAJAXView):

    def get_url(self):
        return reverse('Blog:latest-posts')

    def test_get_latest_posts(self):
        num = 5
        data = {'data': json.dumps({'top_n': num})}

        response = self.request(self.get_url(), data=data)
        result = response.context['posts']

        self.assertTemplateUsed(response, 'post_title.html')
        self.assertEqual(len(result), num)
        self.assertQuerysetEqual(result, Post.objects.get_published()[:num])

    def test_bad_request(self):
        response = self.request(self.get_url(), data={'a': 'a'})
        self.assertEqual(response.status_code, 400,
                         msg='Wrong Request Format for post request')


class TestBookmarkPosts(TestPostBase, TestAJAXView):
    def get_url(self):
        return reverse('Blog:bookmark-post')

    def test_bad_request(self):
        response = self.request(self.get_url(), data={'a': 'a'})
        self.assertEqual(response.status_code, 400,
                         msg='Wrong Request Format for post request')

    def test_bookmark_for_unauthenticated_user(self):
        self.client.logout()
        response = self.request(self.get_url(), format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], -1)

    def test_bookmark_and_unbookmark(self):
        post = self.post
        user = self.user
        data = json.dumps({
            'data': post.slug
        }).encode('utf-8')
        response = self.request(self.get_url(), data=data,
                                content_type='application/json', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), {
            'status': 0,
            'message': 'Post bookmarked'
        })
        # test database operation
        self.assertEqual(False, post in user.profile.get_bookmarked_posts())

        # test unbookmarking
        response = self.request(self.get_url(), data=data,
                                content_type='application/json', format='json')
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertDictEqual(response.json(), {
            'status': 1,
            'message': 'Post removed from bookmarks'
        })
        # test database operation
        self.assertEqual(False, post in user.profile.get_bookmarked_posts())


class TestUserPostView(TestPostBase, TestBaseView):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        from django.contrib.auth.models import Group
        cls.user.groups.add(Group.objects.create(name='editor'))

    def get_url(self, username=None, tab=None):
        if not username:
            username = self.user.username
        if not tab:
            tab = 'draft'
        return reverse('Blog:my-posts', kwargs={'username': username, 'tab': tab})

    def test_unauthenticated_user(self):
        self.client.logout()
        response = self.client.get(self.get_url())
        self.assertRedirects(response, expected_url=reverse('login'))

    def test_user_who_is_not_an_editor(self):
        user = self.user_1
        self.client.force_login(user)
        response = self.client.get(self.get_url(username=user.username))
        self.assertEqual(response.status_code, 302)

    def test_seeing_some_other_users_posts(self):
        response = self.client.get(self.get_url(username=self.user_1.username))
        self.assertEqual(response.status_code, 403)

    def test_draft_tab(self):
        response = self.client.get(self.get_url())

        self.assertEqual(response.status_code, 200)
        result = response.context

        self.assertEqual(result['tab_type'], 'draft')
        self.assertIsNotNone(result['meta'])
        self.assertQuerysetEqual(
            result['posts'], Post.objects.get_draft(author=self.user))

    def test_queued_tab(self):
        tab = 'queued'
        response = self.client.get(self.get_url(tab=tab))

        self.assertEqual(response.status_code, 200)
        result = response.context

        self.assertEqual(result['tab_type'], tab)
        self.assertIsNotNone(result['meta'])
        self.assertQuerysetEqual(
            result['posts'], Post.objects.get_queued(author=self.user))

    def test_published_tab(self):
        tab = 'published'
        response = self.client.get(self.get_url(tab=tab))

        self.assertEqual(response.status_code, 200)
        result = response.context

        self.assertEqual(result['tab_type'], tab)
        self.assertIsNotNone(result['meta'])
        self.assertEqual(result['is_paginated'], True)
        self.assertQuerysetEqual(
            result['posts'], Post.objects.get_published(author=self.user)[:result['paginator'].per_page])


class TestAuthorPostView(TestPostBase, TestBaseView):
    def get_url(self, username=None):
        if not username:
            username = self.user.username
        return reverse('Blog:author-posts', kwargs={'username': username})

    def test_view(self):
        user = self.user
        self.client.logout()
        response = self.client.get(self.get_url(user.username))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Blog/author_posts.html')
        result = response.context

        self.assertEqual(result['is_paginated'], True)
        self.assertQuerysetEqual(
            result['posts'], Post.objects.get_published().filter(author=user)[:result['paginator'].per_page])

        self.assertEqual(result['author'], user)
        self.assertEqual(result['profile'], user.profile)
        self.assertIsNotNone(result['meta'])

    def test_wrong_username(self):
        response = self.client.get(self.get_url('h'))
        self.assertEqual(response.status_code, 404)


class TestUserBookmarkView(TestPostBase, TestBaseView):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user.profile.bookmarked_posts.add(cls.post.pk)

    def get_url(self, username=None):
        if not username:
            username = self.user.username
        return reverse('Blog:user-bookmarks', kwargs={'username': username})

    def test_unauthenticated_users(self):
        self.client.logout()
        response = self.client.get(self.get_url())

        self.assertEqual(response.status_code, 302)

    def test_viewing_other_user_bookmarks(self):
        user = self.user_1
        response = self.client.get(self.get_url(user.username))

        self.assertEqual(response.status_code, 404,
                         msg=f'You should be logged in as {user} to view this page')

    def test_viewing_bookmark(self):
        user = self.user
        response = self.client.get(self.get_url())

        self.assertEqual(response.status_code, 200)
        result = response.context

        self.assertQuerysetEqual(
            result['posts'], user.profile.bookmarked_posts.all().order_by('-date_published'))
        self.assertEqual(result['profile'], user.profile)


class TestPostDetailView(TestPostBase, TestBaseView):
    def get_url(self, post=None):
        if not post:
            post = self.post

        return reverse('Blog:post-detail', kwargs={
            'slug': post.slug,
            'year': post.date_published.year,
            'month': post.date_published.month,
            'day': post.date_published.day
        })

    def test_detail_for_unauthenticated_users(self):
        self.client.logout()
        post = self.post
        initial_views = post.views
        response = self.client.get(self.get_url())
        result = response.context

        self.assertEqual(Post.objects.get(slug=post.slug), result['post'])
        self.assertEqual(result['post'].views, initial_views + 1)
        self.assertIsNotNone(result['meta'])

    def test_detail_for_authenticated_users(self):
        post = self.post
        initial_views = post.views
        response = self.client.get(self.get_url())
        result = response.context

        self.assertEqual(Post.objects.get(slug=post.slug), result['post'])
        self.assertEqual(result['post'].views, initial_views + 1)
        self.assertIsNotNone(result['meta'])
        self.assertEqual(result['profile'], self.user.profile)
