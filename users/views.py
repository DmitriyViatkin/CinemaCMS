from django.shortcuts import render, redirect, get_object_or_404
from .form import ProfileEditForm
from core.models import  Sessions, Tickets
from django.contrib.auth.decorators import login_required
from admins.forms import TicketForm

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
    user = request.user
    user_tickets = user.tickets.all().select_related('session__movie', 'session__cinema', 'session__hall_id', 'seat')


    context = {
        'user': user,
        'user_tickets': user_tickets,
    }
    return render(request, 'users/profile.html', context)

@login_required
def buy_tiсket(request, session_id=None):
        session_instance = get_object_or_404(Sessions, id=session_id)  # Получаем сеанс
        ticket_instance = None

        # Если билета нет для этого сеанса, создаем новый
        try:
            ticket_instance = Tickets.objects.get(session=session_instance)
        except Tickets.DoesNotExist:
            ticket_instance = Tickets(session=session_instance)  # Создаем новый билет для сеанса

        if request.method == 'POST':
            form = TicketForm(request.POST, instance=ticket_instance)
            if form.is_valid():
                saved_ticket = form.save()
                seat_to_update = saved_ticket.seat
                if seat_to_update:
                    seat_to_update.status = 'S'  # Обновляем статус места
                    seat_to_update.save()
                return redirect('movies_list')  # Переходим на страницу с билетами

        else:
            form = TicketForm(instance=ticket_instance)

        context = {
            'form': form,
            'session': session_instance,  # Передаем сеанс в контекст
        }
        return render(request, 'users/ticket/buy_tickets.html', context)