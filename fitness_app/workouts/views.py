from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.utils.dateparse import parse_date

from fitness_app.clients.models import Client
from fitness_app.exercises.models import CompletedExercise
from fitness_app.program_exercises.forms import ProgramExerciseForm
from fitness_app.program_exercises.models import ProgramExercise
from fitness_app.workouts.forms import WorkoutForm, WorkoutExerciseFormSet
from fitness_app.workouts.models import Workout, WorkoutExercise


# Create your views here.
def workout_list(request):
    selected_category = request.GET.get('category', None)
    categories = Workout.objects.values_list('category', flat=True).distinct().order_by('category')

    if selected_category:
        workouts = Workout.objects.filter(category=selected_category).order_by('program_name')
    else:
        workouts = Workout.objects.all().order_by('program_name')

    return render(request, 'training_programs/program-list.html', {
        'workouts': workouts,
        'categories': categories,
        'selected_category': selected_category
    })


@login_required
def workout_add(request):
    if request.method == "POST":
        form = WorkoutForm(request.POST)
        formset = WorkoutExerciseFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            workout = form.save()
            formset.instance = workout
            formset.save()
            return redirect('workout list')
    else:
        form = WorkoutForm()
        formset = WorkoutExerciseFormSet()

    return render(request, 'training_programs/program-add.html', {
        'form': form,
        'formset': formset,
    })


@login_required
def workout_details(request, pk, client_id=None, username=None):
    from django.utils.dateparse import parse_date
    from django.utils import timezone

    workout = get_object_or_404(Workout, pk=pk)
    exercises = WorkoutExercise.objects.filter(workout=workout)
    client = Client.objects.filter(user__username=username).first()

    if client_id is None and hasattr(request.user, 'client'):
        client = request.user.client
    elif client_id is not None:
        client = get_object_or_404(Client, id=client_id)
    else:
        client = None

    date_str = request.GET.get('date')
    if date_str:
        selected_date = parse_date(date_str)
    else:
        selected_date = timezone.now().date()

    completed_exercises = []
    if client:
        completed_exercises = CompletedExercise.objects.filter(
            client=client,
            exercise__in=[we.exercise for we in exercises],
            date=selected_date
        ).values_list('exercise_id', flat=True)

    has_client = hasattr(request.user, 'client')

    context = {
        'workout': workout,
        'exercises': exercises,
        'completed_exercises': completed_exercises,
        'viewed_client': client,
        'has_client': has_client,
        'client': client,
        'selected_date': selected_date,
    }
    return render(request, 'training_programs/program-detail.html', context)


def workout_edit(request, pk):
    workout = get_object_or_404(Workout, pk=pk)

    if request.method == "POST":
        form = WorkoutForm(request.POST, instance=workout)
        formset = WorkoutExerciseFormSet(request.POST, instance=workout)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            print("Form and formset saved!")
            return redirect('workout list')
        else:
            print(form.errors, formset.errors)
    else:
        form = WorkoutForm(instance=workout)
        formset = WorkoutExerciseFormSet(instance=workout)

    return render(request, 'training_programs/program-edit.html', {
        'form': form,
        'formset': formset,
        'workout': workout,
    })


@login_required
def workout_delete(request, pk):
    workout = get_object_or_404(Workout, pk=pk)

    if request.method == 'POST':
        workout.delete()
        return redirect('workout list')

    return render(request, 'training_programs/workout-delete.html', {
        'workout': workout,
    })
