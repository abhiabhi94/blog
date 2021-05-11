from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import Http404
from django.utils.translation import gettext_lazy as _


class IsOwnerMixin(UserPassesTestMixin):
    """ensuring the author themselves is updating the post"""
    def test_func(self):
        post = self.get_object()

        if self.request.user == post.author:
            return True
        raise Http404(_('This post does not exist'))
