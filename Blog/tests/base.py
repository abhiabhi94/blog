from tests.base import Post, TestBase


class TestPostBase(TestBase):

    @classmethod
    def setUpClass(cls):
        """
        Create
        - 2 users
            - 1 will be used to associate posts
            - 2nd will be used for checking unauthorised access during tests
        - 24 posts to test pagination\
            ( text inside brackets indicate pattern used for generating id)
            - 6 draft posts (x % 4 == 0)
            - 1 queued post(x % 4 != 0 && x % 10 == 0)
            - 17 published posts (x % 4 != 0 && x % 10 != 0)
        """
        super().setUpClass()
        # Create 24 posts to test pagination
        num_posts = 25
        cls.num_published, cls.num_drafts, cls.num_queued = 0, 0, 0

        cls.dummy_user = cls.create_user(
            username='tester3',
            email='jach.kar.ta@gmail.com',
            password='user123#'
        )
        cls.category = cls.create_category(name='category')
        for post_id in range(1, num_posts):
            title = f'Draft Post: post number {post_id}'
            category = cls.create_category(name=f'category {post_id}')
            tags = [f'tag_{post_id}, tag_{post_id+1}']
            if post_id % 4 == 0:
                cls.create_post(
                    title=title,
                    category=category,
                    tags=tags,
                    content=title
                )
                cls.num_drafts += 1
            else:
                if post_id % 10 == 0:
                    title = f'Queued Post: post number {post_id}'
                    state = Post.Status.QUEUE.value
                    cls.num_queued += 1
                else:
                    title = f'Published Post: post number {post_id}'
                    state = Post.Status.PUBLISH.value
                    cls.num_published += 1

                cls.create_post(
                    title=title,
                    category=category,
                    tags=tags,
                    state=state,
                    content=title
                )

            cls.post = Post.objects.filter(
                state=Post.Status.PUBLISH).first()

    def get_url(self):
        """A utility function that returns URL for the view"""
        raise NotImplementedError
