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
        self.assertQuerysetEqual(result, Post.objects.get_published()[
                                 :num], transform=lambda x: x)

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


class TestUserPost(TestPostBase, TestBaseView):
    def get_url(self, user=None, tab=None):
        if not user:
            user = self.user
        if not tab:
            tab = 'draft'
        reverse('Blog:author-posts', kwargs={'user': user, 'draft': draft})

    def test_draft_tab(self):
        pass

    def test_queued_tab(self):
        pass

    def test_published_tab(self):
        pass
