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
@login_required
def workout_list(request):
    selected_category = request.GET.get('category')
    search_query = request.GET.get('search', '')

    categories = Workout.objects.values_list('category', flat=True).distinct().order_by('category')
    workouts = Workout.objects.all()

    if selected_category:
        workouts = workouts.filter(category=selected_category)

    if search_query:
        workouts = workouts.filter(program_name__icontains=search_query)

    workouts = workouts.order_by('program_name')

    context = {
        'workouts': workouts,
        'categories': categories,
        'selected_category': selected_category,
        'search_query': search_query,
        'is_client': hasattr(request.user, 'client'),
        'is_trainer': hasattr(request.user, 'trainer'),
    }

    return render(request, 'training_programs/program-list.html', context)


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
def workout_details(request, pk):
    workout = get_object_or_404(Workout, pk=pk)
    exercises = WorkoutExercise.objects.filter(workout=workout)

    client = getattr(request.user, 'client', None)
    date_str = request.GET.get('date')
    selected_date = parse_date(date_str) if date_str else timezone.localdate()

    completed_ids = []
    if client:
        completed_ids = CompletedExercise.objects.filter(
            client=client,
            workout_exercise__in=exercises,
            date=selected_date
        ).values_list('workout_exercise_id', flat=True)

    context = {
        'workout': workout,
        'exercises': exercises,
        'completed_exercises': completed_ids,
        'selected_date': selected_date,
        'has_client': client is not None,
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
