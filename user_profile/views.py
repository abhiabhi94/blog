from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from meta.views import Meta

from user_profile.forms import (ProfileUpdateForm, UserRegisterForm,
                                UserUpdateForm)
from user_profile.manager import log_in_user

# Create your views here.
global meta_home
meta_home = Meta(title='HackAdda | Never stop hacking!',
                 description='Stay updated with latest technology news, articles and tutorials.',
                 keywords=[
                     'Hack', 'Robotics', 'Coding',
                     'STEM', 'STEAM', 'Education',
                     'Blog', 'Tinker', 'Kids',
                     'Technology', 'Curiousity'
                 ],
                 url='https://hackadda.com',
                 #  image='',
                 og_type='website',
                 locale='en_US',
                 site_name='HackAdda',
                 twitter_creator='@thehackadda',
                 twitter_site='@thehackadda',
                 og_publisher='https://www.facebook.com/thehackadda',
                 )


@require_http_methods(['GET', 'POST'])
def register(request):
    # Redirect to the homepage in case user is logged in.
    if request.user.is_authenticated:
        messages.warning(
            request, 'You are already logged in!'
        )
        return redirect('post:home')

    template_name = 'user_profile/register.html'
    context = {}
    if(request.method == 'POST'):
        context['form'] = form = UserRegisterForm(request.POST)
        if(form.is_valid()):
            user = form.save()
            username = form.cleaned_data.get('username')
            log_in_user(request, user)
            messages.success(
                request, f'Account created for {username}. You will now be able to Log In!')

            return redirect('post:home')
    else:  # On GET request return a new form
        context['form'] = UserRegisterForm()

    context['meta'] = Meta(title='Register | HackAdda',
                           description='Register on HackAdda',
                           keywords=meta_home.keywords + ['register'])
    return render(request, template_name, context)


@require_http_methods(['GET', 'POST'])
@login_required
def profile(request):
    template_name = 'user_profile/profile.html'
    if(request.method == 'POST'):
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile)
        if(u_form.is_valid() and p_form.is_valid()):
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    context['meta'] = Meta(title='Profile | HackAdda',
                           description=f'Profile of {request.user.get_full_name().title()} on HackAdda',
                           )
    return render(request, template_name, context)


@require_http_methods(['GET', 'POST'])
@login_required
def password_change(request):
    """Change users password and log them back in"""
    template_name = 'user_profile/profile.html'
    if(request.method == 'POST'):
        u_form = PasswordChangeForm(data=request.POST, user=request.user)
        if u_form.is_valid():
            user = u_form.save()
            messages.success(
                request, 'Password updated. You have now be logged out of all other sessions')
            log_in_user(request, user)
            return redirect('post:home')
    else:
        u_form = PasswordChangeForm(user=request.user)

    context = {
        'u_form': u_form
    }
    context['meta'] = Meta(title='Change Password | HackAdda',
                           description=f"""Password change for {request.user.get_full_name().title()}
                            on HackAdda""",
                           )
    return render(request, template_name, context=context)


@require_http_methods(['GET'])
def privacy_policy(request):
    context = {}
    template_name = 'post/privacy_policy.html'
    context['meta'] = Meta(title='Privacy Policy | HackAdda',
                           description='Privacy Policy by HackAdda',
                           keywords=meta_home.keywords + ['privacy policy'])
    return render(request, template_name, context)


@require_http_methods(['GET'])
def image_license(request):
    context = {}
    template_name = 'post/image_license.html'
    context['meta'] = Meta(title='Image License | HackAdda',
                           description='Image License by HackAdda',
                           keywords=meta_home.keywords + ['image license'])
    return render(request, template_name, context)
