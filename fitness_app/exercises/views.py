from urllib.parse import unquote

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_date

from fitness_app.exercises.forms import ExerciseAddForm, ExerciseEditForm
from fitness_app.exercises.models import Exercise, CompletedExercise


def exercises(request):
    selected_category = request.GET.get('category', None)
    categories = Exercise.objects.values_list('category', flat=True).distinct().order_by('category')

    if selected_category:
        all_exercises = Exercise.objects.filter(category=selected_category).order_by('name')
    else:
        all_exercises = Exercise.objects.all().order_by('name')

    return render(request, 'exercises/exercises-list.html', {
        'exercises': all_exercises,
        'categories': categories,
        'selected_category': selected_category
    })


@login_required
def complete_exercise(request, pk):
    client = request.user.client
    exercise = get_object_or_404(Exercise, pk=pk)

    # Вземи избраната дата от POST заявката
    date_str = request.POST.get('date')
    if date_str:
        date_obj = parse_date(date_str)
    else:
        date_obj = timezone.localdate()

    # Уникален запис по client, exercise и date
    CompletedExercise.objects.get_or_create(
        client=client,
        exercise=exercise,
        date=date_obj
    )

    return JsonResponse({'status': 'completed'})


@login_required
def uncomplete_exercise(request, pk):
    client = request.user.client
    exercise = get_object_or_404(Exercise, pk=pk)

    date_str = request.POST.get('date')
    if date_str:
        date_obj = parse_date(date_str)
    else:
        date_obj = timezone.localdate()

    CompletedExercise.objects.filter(
        client=client,
        exercise=exercise,
        date=date_obj
    ).delete()

    return JsonResponse({'status': 'uncompleted'})


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

    # Проверка дали потребителят е клиент
    has_client = hasattr(request.user, 'client')
    client = request.user.client if has_client else None

    # Вземи избраната дата от GET параметър или използвай текущата дата
    selected_date_str = request.GET.get('date')
    selected_date = parse_date(selected_date_str) if selected_date_str else timezone.localdate()

    # Валидирай дали selected_date е None (ако подадена дата е невалидна)
    if not selected_date:
        selected_date = timezone.localdate()

    # Вземи списък с изпълнени упражнения за конкретния клиент и дата
    completed_exercises = []
    if client:
        completed_exercises = CompletedExercise.objects.filter(
            client=client,
            exercise=exercise,
            date=selected_date
        ).values_list('exercise_id', flat=True)

    context = {
        'exercise': exercise,
        'has_client': has_client,
        'client': client,
        'completed_exercises': completed_exercises,
        'selected_date': selected_date
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
        messages.success(request, "Упражнението беше изтрито успешно.")
        return redirect('exercises')

    return render(request, 'exercises/exercise-delete.html', {'exercise': exercise})
