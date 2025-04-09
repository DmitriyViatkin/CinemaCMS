from django.shortcuts import render
from .form import ProfileEditForm
from django.contrib.auth.decorators import login_required

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileEditForm(initial=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'users/edit_done.html')
    else:
        form = ProfileEditForm(instance= request.user)
    return render(request, 'users/edit.html', {'form':form})

@login_required
def profile_view(request):
    user = request.user  # текущий авторизованный пользователь
    return render(request, 'users/profile.html', {'user': user})