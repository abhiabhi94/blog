from io import StringIO
from unittest.mock import patch

from django.core.management import call_command

from post.tests.base import TestPostBase


class TestSetTrendingScore(TestPostBase):
    command_name = 'set_trending_score'

    def setUp(self):
        super().setUp()
        self.original_score = self.post.trending_score
        self.client.get(self.post.get_detail_url())

    @patch('sys.stdout', new_callable=StringIO)
    def test_standard_output(self, mock_out):
        call_command(self.command_name, stdout=mock_out)

        self.assertIs(
            f'Successfully updated trending score for {self.posts} posts' in mock_out.getvalue(),
            True
        )

    def test_score_update(self):
        call_command(self.command_name)

        self.post.refresh_from_db()

        self.assertNotEqual(self.post.trending_score, self.original_score)
