from urllib.parse import unquote

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from fitness_app.exercises.forms import ExerciseAddForm, ExerciseEditForm
from fitness_app.exercises.models import Exercise, CompletedExercise
from fitness_app.workouts.models import WorkoutExercise

# @csrf_exempt
# def exercises_api(request):
#     if request.method == 'GET':
#         data = list(Exercise.objects.values())
#         return JsonResponse({'exercises': data})
#     return JsonResponse({'error': 'Only GET allowed'}, status=405)
@login_required
def exercises(request):
    selected_category = request.GET.get('category')
    search_query = request.GET.get('search', '')

    categories = Exercise.objects.values_list('category', flat=True).distinct().order_by('category')
    all_exercises = Exercise.objects.all()

    if selected_category:
        all_exercises = all_exercises.filter(category=selected_category)

    if search_query:
        all_exercises = all_exercises.filter(name__icontains=search_query)

    all_exercises = all_exercises.order_by('name')

    # Добавяме тези два флага за шаблона:
    is_client = hasattr(request.user, 'client')
    is_trainer = hasattr(request.user, 'trainer')

    return render(request, 'exercises/exercises-list.html', {
        'exercises': all_exercises,
        'categories': categories,
        'selected_category': selected_category,
        'search_query': search_query,
        'is_client': is_client,
        'is_trainer': is_trainer,
    })


@login_required
def complete_exercise(request, pk):
    if request.method == 'POST':
        client = getattr(request.user, 'client', None)
        if not client:
            return JsonResponse({'error': 'Нямате клиентски профил.'}, status=400)

        workout_exercise = get_object_or_404(WorkoutExercise, pk=pk)
        date_str = request.POST.get('date')
        date = parse_date(date_str) or timezone.localdate()

        CompletedExercise.objects.get_or_create(
            client=client,
            workout_exercise=workout_exercise,
            date=date
        )
        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Invalid method'}, status=405)


@login_required
def uncomplete_exercise(request, pk):
    if request.method == 'POST':
        client = getattr(request.user, 'client', None)
        if not client:
            return JsonResponse({'error': 'Нямате клиентски профил.'}, status=400)

        date_str = request.POST.get('date')
        date = parse_date(date_str) or timezone.localdate()

        CompletedExercise.objects.filter(
            client=client,
            workout_exercise_id=pk,
            date=date
        ).delete()
        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Invalid method'}, status=405)


def exercise_add(request):
    if request.method == 'POST':
        form = ExerciseAddForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('exercises')
    else:
        form = ExerciseAddForm()
    return render(request, 'exercises/exercise-add.html', {'form': form})


def exercise_details(request, pk, exercise_name):
    decoded_name = unquote(exercise_name)
    exercise = get_object_or_404(Exercise, pk=pk, name__iexact=decoded_name)

    has_client = hasattr(request.user, 'client')
    client = request.user.client if has_client else None

    selected_date_str = request.GET.get('date')
    selected_date = parse_date(selected_date_str) if selected_date_str else timezone.localdate()
    if not selected_date:
        selected_date = timezone.localdate()

    workout_exercise = None
    is_completed = False

    if client:
        from fitness_app.program_exercises.models import ProgramExercise
        program = ProgramExercise.objects.filter(client=client, date=selected_date).first()
        if program:
            workout_exercise = WorkoutExercise.objects.filter(
                workout=program.workout,
                exercise=exercise
            ).first()

            if workout_exercise:
                is_completed = CompletedExercise.objects.filter(
                    client=client,
                    workout_exercise=workout_exercise,
                    date=selected_date
                ).exists()

    context = {
        'exercise': exercise,
        'has_client': has_client,
        'client': client,
        'selected_date': selected_date,
        'is_completed': is_completed,
        'workout_exercise': workout_exercise,
    }

    return render(request, 'exercises/exercise-details.html', context)


def exercise_edit(request, pk, exercise_name):
    exercise = get_object_or_404(Exercise, pk=pk)

    if request.method == 'POST':
        form = ExerciseEditForm(request.POST, request.FILES, instance=exercise)
        if form.is_valid():
            form.save()
            return redirect('exercise details', pk=exercise.pk, exercise_name=exercise.name)
    else:
        form = ExerciseEditForm(instance=exercise)

    return render(request, 'exercises/exercise-edit.html', {'form': form, 'exercise': exercise})


@login_required
def exercise_delete(request, pk, exercise_name):
    exercise = get_object_or_404(Exercise, pk=pk)
    if request.method == 'POST':
        exercise.delete()
        return redirect('exercises')
    return redirect('exercise details', pk=pk, exercise_name=exercise_name)
