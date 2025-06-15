from datetime import datetime, date
from django.utils import timezone
from django.utils.timezone import now
from fitness_app.exercises.models import CompletedExercise
from fitness_app.program_exercises.forms import ProgramExerciseFormEditSet

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from fitness_app.clients.models import Client
from fitness_app.program_exercises.forms import ProgramExerciseFormSet
from fitness_app.program_exercises.models import ProgramExercise
from fitness_app.workouts.models import WorkoutExercise


@login_required
def assign_program_view(request, client_id):
    client = get_object_or_404(Client, pk=client_id)
    trainer = client.trainer

    if request.method == 'POST':
        future_workouts = ProgramExercise.objects.filter(
            client=client,
            date__gte=now().date()
        ).order_by('date')
        formset = ProgramExerciseFormSet(request.POST, instance=client, queryset=future_workouts)

        if formset.is_valid():
            formset.save()
            return redirect('trainer clients', trainer_id=trainer.pk)
        else:
            print("Formset errors:", formset.errors)
    else:
        formset = ProgramExerciseFormSet(instance=client)

    return render(request, 'program_exercises/assign_workouts.html', {
        'client': client,
        'formset': formset,
    })


@login_required
def edit_program(request, client_id):
    client = get_object_or_404(Client, pk=client_id)
    trainer = client.trainer
    today = now().date()

    future_workouts = ProgramExercise.objects.filter(
        client=client,
        date__gte=today
    ).order_by('date')

    if request.method == 'POST':
        print(request.POST)
        formset = ProgramExerciseFormEditSet(
            request.POST,
            instance=client,
            queryset=future_workouts
        )
        if formset.is_valid():
            formset.save()

            return redirect('trainer clients', trainer_id=trainer.pk)
    else:
        formset = ProgramExerciseFormEditSet(
            instance=client,
            queryset=future_workouts
        )

    return render(request, 'program_exercises/edit_program.html', {
        'client': client,
        'formset': formset
    })

def programs_dates_list(request, client_id):
    client = get_object_or_404(Client, pk=client_id)
    dates = ProgramExercise.objects.filter(client=client).order_by('date').values_list('date', flat=True).distinct()

    context = {
        'client': client,
        'dates': dates,
    }
    return render(request, 'trainers/programs_dates_list.html', context)


def programs_for_date(request, client_id, date):
    client = get_object_or_404(Client, pk=client_id)
    date_obj = datetime.date.fromisoformat(date)

    programs = ProgramExercise.objects.filter(client=client, date=date_obj)

    programs_with_exercises = []

    for program in programs:
        exercises = WorkoutExercise.objects.filter(workout=program.workout).select_related('exercise')
        completed_exercise_ids = CompletedExercise.objects.filter(
            client=client,
            exercise__in=[ex.exercise for ex in exercises]
        ).values_list('exercise_id', flat=True)

        programs_with_exercises.append({
            'program': program,
            'exercises': exercises,
            'completed_exercise_ids': completed_exercise_ids,
        })

    context = {
        'client': client,
        'programs_with_exercises': programs_with_exercises,
        'date': date_obj,
    }
    return render(request, 'trainers/programs_for_date.html', context)


@login_required
def client_program_view(request, client_id):
    client = get_object_or_404(Client, pk=client_id)

    selected_date_str = request.GET.get('date')
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = date.today()
    else:
        selected_date = date.today()

    workouts = ProgramExercise.objects.filter(client=client, date=selected_date).order_by('date')

    completed_exercises = CompletedExercise.objects.filter(
        client=client
    ).values_list('exercise_id', flat=True)

    return render(request, 'program_exercises/client_program.html', {
        'client': client,
        'workouts': workouts,
        'completed_exercises': completed_exercises,
        'selected_date': selected_date,
    })