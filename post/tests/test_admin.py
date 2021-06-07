from django.contrib.admin import AdminSite

from post.admin import PostAdmin
from post.models import Post
from post.tests.base import TestPostBase


class TestPostAdmin(TestPostBase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.model_admin = PostAdmin(Post, AdminSite())

    def test_view_on_site_for_draft_post(self):
        url = self.model_admin.view_on_site(self.draft_post)

        self.assertEqual(url, self.draft_post.get_preview_url())
