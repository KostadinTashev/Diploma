from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from fitness_app.clients.forms import ClientForm, PersonalInfoForm
from fitness_app.clients.models import Client, TrainerReview, AppReview
from fitness_app.meals.models import Meal
from fitness_app.nutrition_plans.models import NutritionPlan
from fitness_app.program_exercises.models import ProgramExercise
from fitness_app.progress.forms import ProgressForm
from fitness_app.progress.models import Progress
from fitness_app.trainers.models import Trainer
from fitness_app.utils.body_fat_calculator import calculate_body_fat_percentage


@login_required
def set_client_data(request, client_id):
    client = get_object_or_404(Client, id=client_id)

    if client.user != request.user:
        return redirect('client profile', client_id=request.user.client.id)

    user = request.user

    if request.method == 'POST':
        personal_form = PersonalInfoForm(request.POST, request.FILES, instance=user)
        client_form = ClientForm(request.POST, instance=client)
        progress_form = ProgressForm(request.POST)

        if all([personal_form.is_valid(), client_form.is_valid(), progress_form.is_valid()]):
            personal_form.save()
            client_form.save()

            progress = progress_form.save(commit=False)
            progress.client = client
            progress.progress_date = timezone.now().date()  # Задаваме датата тук автоматично

            body_fat = calculate_body_fat_percentage(
                gender=user.gender,
                height=progress.height,
                neck=progress.neck,
                waist=progress.waist,
                hip=progress.hip
            )

            if body_fat is not None:
                progress.body_fat_percentage = Decimal(str(body_fat))
                progress.muscle_mass = progress.weight * (
                    Decimal('1') - (progress.body_fat_percentage / Decimal('100'))
                )
            else:
                progress.body_fat_percentage = Decimal('0')
                progress.muscle_mass = None

            progress.save()
            return redirect('suitable trainers')

    else:
        personal_form = PersonalInfoForm(instance=user)
        client_form = ClientForm(instance=client)
        progress_form = ProgressForm()

    context = {
        'personal_form': personal_form,
        'client_form': client_form,
        'progress_form': progress_form,
        'client': client,
    }
    return render(request, 'clients/set-client-data.html', context)


def client_details(request, pk, username):
    client = get_object_or_404(Client, pk=pk)
    latest_progress = client.progress_set.order_by('-progress_date').first()
    if client.user.username != username:
        return render(request, 'error.html', {'message': 'Невалидно потребителско име!'})

    return render(request, 'clients/client_details.html', {'client': client,
                                                           'latest_progress': latest_progress})


@login_required
def client_edit(request):
    user = request.user

    if request.method == 'POST':
        form = PersonalInfoForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('client details', pk=user.client.id, username=user.username)
    else:
        form = PersonalInfoForm(instance=user)

    return render(request, 'clients/edit-profile.html', {'form': form})


def client_delete(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        logout(request)
        messages.success(request, "Профилът беше успешно изтрит.")
        return redirect('index')

    return render(request, 'clients/confirm_delete.html')


def client_profile(request):
    return None


def dashboard(request, client_id, username):
    client = get_object_or_404(Client, pk=client_id)

    plan = NutritionPlan.objects.filter(client=client).first()
    meals = Meal.objects.filter(plan=plan).prefetch_related('food_items__product').order_by('date')

    meals_by_day = {}
    for meal in meals:
        date = meal.date
        meals_by_day.setdefault(date, []).append(meal)

    program_exercises = ProgramExercise.objects.filter(client=client).select_related('workout')

    workouts_by_day = {}
    for entry in program_exercises:
        day = entry.date
        workout = entry.workout
        workout_exercises = workout.exercises.select_related('exercise').all()
        workouts_by_day.setdefault(day, []).append({
            'workout': workout,
            'exercises': workout_exercises,
        })

    return render(request, 'clients/dashboard.html', {
        'client': client,
        'user': request.user,
        'workouts_by_day': workouts_by_day,
        'meals_by_day': meals_by_day,
    })


def client_workouts_view(request, client_id, username):
    client = get_object_or_404(Client, pk=client_id, user__username=username)
    program_by_day = {}

    for program in client.programexercise_set.select_related('workout').all():
        day = program.date
        if day not in program_by_day:
            program_by_day[day] = []
        program_by_day[day].append(program.workout)

    context = {
        'client': client,
        'program_by_day': program_by_day,
    }
    return render(request, 'clients/client_workouts_by_day.html', context)


@login_required
def submit_trainer_review(request, trainer_id):
    if request.method == 'POST':
        trainer = get_object_or_404(Trainer, id=trainer_id)
        client = get_object_or_404(Client, user=request.user)
        rating = int(request.POST.get('rating'))
        comment = request.POST.get('comment', '')

        if TrainerReview.objects.filter(trainer=trainer, client=client).exists():
            return redirect('my trainer')

        TrainerReview.objects.create(trainer=trainer, client=client, rating=rating, comment=comment)
    return redirect('my trainer')


@login_required
def add_trainer_comment(request, trainer_id):
    if request.method == 'POST':
        trainer = get_object_or_404(Trainer, id=trainer_id)
        client = get_object_or_404(Client, user=request.user)
        comment = request.POST.get('comment', '')
        existing_review = TrainerReview.objects.filter(trainer=trainer, client=client).order_by('-created_at').first()

        if existing_review:
            TrainerReview.objects.create(trainer=trainer, client=client, rating=existing_review.rating, comment=comment)
    return redirect('my trainer')


def submit_app_review(request):
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        AppReview.objects.create(client=request.user.client, rating=rating, comment=comment)
        return redirect('index')
    return redirect('index')


def client_settings(request, client_id, username):
    try:
        client = Client.objects.get(pk=client_id, user__username=username)
    except Client.DoesNotExist:
        messages.error(request, "Клиентът не е намерен!")
        return redirect("dashboard", client_id=client_id, username=username)

    if request.method == "POST":
        user = client.user
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.gender = request.POST.get("gender", user.gender)
        user.birth_date = request.POST.get("birth_date", user.birth_date)

        # ✅ Обработка на профилна снимка
        profile_image = request.FILES.get("profile_image")
        if profile_image:
            user.profile_picture = profile_image

        new_email = request.POST.get("email")
        if new_email and new_email != user.email:
            user.email = new_email

        new_password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if new_password:
            if new_password == confirm_password:
                user.set_password(new_password)
            else:
                messages.error(request, "Паролите не съвпадат.")
                return redirect("client settings", client_id=client_id, username=username)

        user.save()
        client.save()
        messages.success(request, "Настройките бяха успешно обновени!")
        return redirect("client settings", client_id=client_id, username=username)

    context = {
        "client": client
    }
    return render(request, "clients/client-settings.html", context=context)
