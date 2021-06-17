from post.models import Post
from post.tests.base import TestPostBase


class TestUserProfileModel(TestPostBase):
    def test_bookmarked_post(self):
        post_1 = Post.objects.first()
        post_2 = Post.objects.last()

        self.user.profile.bookmarked_posts.add(post_1)
        self.user.profile.bookmarked_posts.add(post_2)

        self.assertQuerysetEqual(
            self.user.profile.get_bookmarked_posts(),
            [post_1.id, post_2.id],
            transform=lambda x: x
        )
        self.assertNumQueries(1)
