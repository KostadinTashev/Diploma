from collections import defaultdict
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST

from fitness_app.clients.forms import ClientForm, PersonalInfoForm, ChangeTrainerForm
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
            progress.progress_date = timezone.now().date()

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


@login_required
def client_details(request, client_id, username):
    client = get_object_or_404(Client, pk=client_id)

    latest_progress = client.progress_set.order_by('-progress_date').first()

    trainer_id = None
    if hasattr(request.user, 'trainer'):
        trainer_id = request.user.trainer.id

    return render(request, 'clients/client_details.html', {
        'client': client,
        'latest_progress': latest_progress,
        'trainer_id': trainer_id,
    })


@login_required
def client_edit(request):
    user = request.user

    if request.method == 'POST':
        form = PersonalInfoForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('client details', client_id=user.client.id, username=user.username)
    else:
        form = PersonalInfoForm(instance=user)

    return render(request, 'clients/edit-profile.html', {'form': form})


def client_delete(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        logout(request)
        return redirect('index')

    return render(request, 'clients/confirm_delete.html')


def client_profile(request):
    return None


def dashboard(request, client_id, username):
    client = get_object_or_404(Client, pk=client_id)

    plan = NutritionPlan.objects.filter(client=client).first()

    meals_by_day = {}

    if plan:
        meals = Meal.objects.filter(plan=plan).prefetch_related('food_items__product').order_by('date')

        for meal in meals:
            date = meal.date
            meals_by_day.setdefault(date, []).append(meal)

    program_exercises = ProgramExercise.objects.filter(client=client).select_related('workout').order_by('date')

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
        'has_plan': plan is not None,
    })


# @require_POST
# @login_required
# def change_trainer(request, trainer_id):
#     trainer = get_object_or_404(Trainer, id=trainer_id)
#     client = request.user.client
#
#     # директна смяна
#     client.trainer = trainer
#     client.save()
#
#     return redirect('dashboard', client_id=client.id, username=request.user.username)


@login_required
def request_trainer(request, trainer_id):
    client = request.user.client
    trainer = get_object_or_404(Trainer, id=trainer_id)

    if client.trainer:
        return redirect('dashboard', client.id, request.user.username)

    pending_requests = request.session.get('pending_requests', {})
    pending_requests[str(client.id)] = trainer.id
    request.session['pending_requests'] = pending_requests

    return redirect('dashboard', client.id, request.user.username)


def client_workouts_view(request, client_id, username):
    client = get_object_or_404(Client, pk=client_id, user__username=username)

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    start_date = parse_date(start_date) if start_date else None
    end_date = parse_date(end_date) if end_date else None

    workouts_qs = client.programexercise_set.select_related('workout').all()

    if start_date:
        workouts_qs = workouts_qs.filter(date__gte=start_date)
    if end_date:
        workouts_qs = workouts_qs.filter(date__lte=end_date)

    workouts_qs = workouts_qs.order_by('date')

    program_by_day = {}
    for program in workouts_qs:
        day = program.date
        program_by_day.setdefault(day, []).append(program.workout)

    context = {
        'client': client,
        'program_by_day': sorted(program_by_day.items()),
        'start_date': start_date,
        'end_date': end_date,
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


def submit_app_review(request, client_id=None, username=None):
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        client = request.user.client
        AppReview.objects.create(client=request.user.client, rating=rating, comment=comment, is_approved=False)
        return redirect('dashboard', client_id=client.id, username=request.user.username)
    return redirect('dashboard', client_id=request.user.client.id, username=request.user.username)


def client_settings(request, client_id, username):
    try:
        client = Client.objects.get(pk=client_id, user__username=username)
    except Client.DoesNotExist:
        return redirect("dashboard", client_id=client_id, username=username)

    if request.method == "POST":
        user = client.user
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.gender = request.POST.get("gender", user.gender)
        user.birth_date = request.POST.get("birth_date", user.birth_date)

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
                return redirect("client settings", client_id=client_id, username=username)

        user.save()
        client.save()
        return redirect("client settings", client_id=client_id, username=username)

    context = {
        "client": client
    }
    return render(request, "clients/client-settings.html", context=context)
