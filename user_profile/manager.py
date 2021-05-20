"""
Module contains functions that will be re-usable inside applications.
Ideally, the logical part (apart from that written in models) in views should be placed here.
"""
from django.contrib import messages
from django.contrib.auth import login


def log_in_user(request, user):
    """
    Log in a user

    Returns:
        bool
            True or False indicating whether login was successfull or not

    Params:
        request: WSGIRequest
            The incoming request object
        user: The current user
    """
    if user is not None:
        login(request, user,
              backend='django.contrib.auth.backends.ModelBackend')
        return True
    else:
        messages.info(request, 'Unable to log you in automatically.\
            Please try going through the login page')
        return False
