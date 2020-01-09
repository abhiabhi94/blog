from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required
from meta.views import Meta

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


def register(request):
    # Redirect to the homepage in case user is logged in.
    if request.user.is_authenticated:
        messages.error(
            request, 'You are already logged in!'
        )
        return redirect('Blog:home')

    template_name = 'Users/register.html'
    context = {}
    if(request.method == 'POST'):
        context['form'] = form = UserRegisterForm(request.POST)
        if(form.is_valid()):
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(
                request, f'Account created for {username}. You will now be able to Log In!')
            return redirect('Blog:home')
    else:  # On GET request return a new form
        context['form'] = UserRegisterForm()

    context['meta'] = Meta(title=f'Register | HackAdda',
                           description=f'Register on HackAdda',
                           keywords=meta_home.keywords + ['register'])
    return render(request, template_name, context)


@login_required
def profile(request):
    template_name = 'Users/profile.html'
    if(request.method == 'POST'):
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile)
        if(u_form.is_valid() and p_form.is_valid()):
            u_form.save()
            p_form.save()
            messages.success(request, f'Your profile has been updated!')
            return redirect('profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    context['meta'] = Meta(title=f'Profile | HackAdda',
                           description=f'Profile of {request.user.get_full_name().title()} on HackAdda',
                           )
    return render(request, template_name, context)
