from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required

# Create your views here.


def register(request):
    template_name = 'Users/register.html'
    if(request.method == 'POST'):
        form = UserRegisterForm(request.POST)
        if(form.is_valid()):
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(
                request, f'Account created for {username}. You will now be able to Log In!')
            return redirect('Blog:home')
    else:
        context = {}
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
