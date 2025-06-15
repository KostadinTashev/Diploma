from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.generic import ListView, TemplateView

from fitness_app.clients.models import Client, ClientGoals, TrainerReview
from fitness_app.program_exercises.models import ProgramExercise
from fitness_app.progress.models import Progress
from fitness_app.trainers.forms import UserForm, TrainerForm
from fitness_app.trainers.models import Trainer

GOALS_TO_SPECIALTIES = {
    ClientGoals.ОТСЛАБВАНЕ: ["Аеробика", "Кросфит"],
    ClientGoals.МУСКУЛНА_МАСА: ["Силова тренировка", "Кросфит"],
    ClientGoals.ПОДДЪРЖАНЕ_НА_ТЕГЛО: ["Кросфит", "Йога"],
    ClientGoals.ЗДРАВОСЛОВНО_ХРАНЕНЕ: ["Йога", "Аеробика"],
}


@login_required
class AllTrainersView(ListView):
    model = Trainer
    template_name = 'trainers/all-trainers.html'
    context_object_name = 'trainers'


@login_required
def suitable_trainers(request):
    client = get_object_or_404(Client, user=request.user)
    specialties = GOALS_TO_SPECIALTIES.get(client.goals, [])
    trainers = Trainer.objects.filter(speciality__in=specialties)

    return render(request, 'trainers/suitable-trainers.html', {
        'suitable_trainers': trainers,
        'goal': client.goals
    })


@login_required
def choose_trainer(request, trainer_id):
    trainer = get_object_or_404(Trainer, id=trainer_id)
    client = get_object_or_404(Client, user=request.user)

    client.trainer = trainer
    client.save()

    messages.success(request, f"Успешно избра треньор: {trainer.user.full_name or trainer.user.username}")
    return redirect('dashboard', client_id=client.id, username=request.user.username)


@login_required
def trainer_details(request, pk, trainer_name):
    trainer = get_object_or_404(Trainer, pk=pk, user__username=trainer_name)
    return render(request, 'trainers/trainer_details.html', {'trainer': trainer})


@login_required
def trainer_edit(request, pk, trainer_name):
    trainer = get_object_or_404(Trainer, pk=pk, user__username=trainer_name)

    if request.method == 'POST':
        trainer_form = TrainerForm(request.POST, instance=trainer)
        user_form = UserForm(request.POST, request.FILES, instance=trainer.user)

        if trainer_form.is_valid() and user_form.is_valid():
            user_form.save()
            trainer_form.save()
            return redirect('trainer details', pk=trainer.pk, trainer_name=trainer.user.username)
    else:
        trainer_form = TrainerForm(instance=trainer)
        user_form = UserForm(instance=trainer.user)

    return render(request, 'trainers/trainer-edit.html', {
        'trainer_form': trainer_form,
        'user_form': user_form,
    })


@login_required
def trainer_delete(request, pk, trainer_name):
    trainer = get_object_or_404(Trainer, pk=pk, user__first_name=trainer_name)


class MyTrainerView(LoginRequiredMixin, TemplateView):
    template_name = 'trainers/my-trainer.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client = Client.objects.filter(user=self.request.user).first()
        trainer = client.trainer if client else None
        context['trainer'] = trainer

        if trainer:
            existing_review = TrainerReview.objects.filter(trainer=trainer, client=client).first()
            context['existing_review'] = existing_review

        return context


def clients_details(request, client_id, trainer_id=None):
    client = get_object_or_404(Client, id=client_id)
    progress_data = Progress.objects.filter(client=client).order_by('progress_date')

    return render(request, 'clients/client-details-page.html', {
        'client': client,
        'progress_data': progress_data
    })


def trainer_clients_view(request, trainer_id):
    clients = Client.objects.filter(trainer_id=trainer_id).select_related('user')

    for client in clients:
        client.has_program = ProgramExercise.objects.filter(client=client).exists()

    return render(request, 'trainers/my_clients.html', {'clients': clients})


def trainer_dashboard(request, trainer_id, username):
    trainer = get_object_or_404(Trainer, id=trainer_id, user__username=username)
    return render(request, 'trainers/trainer-dashboard.html', {'trainer': trainer})


@login_required
def trainer_nutrition_clients(request):
    try:
        trainer = request.user.trainer
    except Trainer.DoesNotExist:
        messages.error(request, "Нямаш профил като треньор.")
        return redirect('index')

    clients = Client.objects.filter(trainer=trainer)
    return render(request, 'trainers/nutrition_clients.html', {
        'clients': clients,
        'trainer': trainer,
    })
