from django.shortcuts import render, redirect
from .form import ProfileEditForm
from django.contrib.auth.decorators import login_required

@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=user)  # тут має бути instance
        if form.is_valid():
            form.save()
            return redirect('profile')  # або інший URL
    else:
        form = ProfileEditForm(instance=user)
    return render(request, 'users/edit.html', {'form': form})

@login_required
def profile_view(request):
    user = request.user  # текущий авторизованный пользователь
    return render(request, 'users/profile.html', {'user': user})