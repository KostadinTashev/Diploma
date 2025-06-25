from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.templatetags.static import static
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from django.views import generic as views, View
from django.contrib.auth import views as auth_views, logout, get_user_model, login
from django.views.generic import CreateView

from fitness_app.accounts.forms import RegisterUserForm, CustomUserCreationForm, TrainerForm, UserProfilePictureForm, \
    ClientForm, MealAdminForm, CustomUserEditForm
from fitness_app.accounts.models import FitnessUser
from fitness_app.clients.models import Client, AppReview
from fitness_app.exercises.forms import ExerciseAddForm
from fitness_app.exercises.models import User, Exercise, ExerciseCategory
from fitness_app.meals.models import Meal, MealType
from fitness_app.nutrition_plans.models import NutritionPlan
from fitness_app.progress.forms import ProgressForm
from fitness_app.progress.models import Progress
from fitness_app.trainers.models import Trainer

UserModel = get_user_model()


class RegisterUserView(CreateView):
    template_name = "accounts/register-page.html"
    form_class = RegisterUserForm

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        goals = self.request.POST.get('goals')
        Client.objects.create(user=user, goals=goals)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        activation_link = self.request.build_absolute_uri(
            reverse('confirm_email', kwargs={'uidb64': uid, 'token': token})
        )

        send_mail(
            'Потвърждение на регистрация',
            f'Здравей! Моля потвърди имейла си като последваш този линк: {activation_link}',
            'noreply@silaplus.bg',
            [user.email],
            fail_silently=False,
        )

        return render(self.request, 'accounts/email_sent.html')


class ConfirmEmailView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = UserModel.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            return render(request, 'accounts/activation_success.html', {
                'client_id': user.client.id
            })
        else:
            return HttpResponse('Линкът е невалиден или е изтекъл.')


class LoginUserView(auth_views.LoginView):
    template_name = "accounts/login-page.html"

    def get_success_url(self):
        user = self.request.user
        if user.is_superuser:
            return reverse('admin dashboard')
        try:
            client = Client.objects.get(user=user)
            return reverse('dashboard', args=[client.id, client.user.username])
        except Client.DoesNotExist:
            try:
                trainer = user.trainer
                if trainer:
                    return reverse('trainer dashboard', args=[trainer.id, user.username])
                else:
                    return reverse('all trainers')
            except AttributeError:
                return reverse('index')


def logout_user(request):
    logout(request)
    return redirect('index')


def profile(request):
    client = get_object_or_404(Client, user=request.user)
    return render(request, 'profile.html', {'client': client})


@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    users = User.objects.all()
    trainers = Trainer.objects.all()
    clients = Client.objects.all()
    context = {
        'users': users,
        'total_users': users.count(),
        'total_trainers': trainers.count(),
        'total_clients': clients.count(),
    }
    return render(request, 'accounts/admin_dashboard.html', context=context)


@user_passes_test(lambda u: u.is_superuser)
def admin_users_list(request):
    users = FitnessUser.objects.all().order_by('id')

    return render(request, 'admin/users/users_list.html', {
        'title': 'Потребители',
        'columns': ['ID', 'Потребителско име', 'Имейл', 'Тип профил'],
        'users': users,
    })


@user_passes_test(lambda u: u.is_superuser)
def admin_user_create(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('admin user details', user_id=user.id)
    else:
        form = CustomUserCreationForm()

    return render(request, 'admin/users/user_create.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
def admin_user_details(request, user_id):
    user = get_object_or_404(FitnessUser, pk=user_id)
    return render(request, 'admin/users/user_details.html', {'user': user})


@user_passes_test(lambda u: u.is_superuser)
def admin_user_edit(request, user_id):
    user = get_object_or_404(FitnessUser, pk=user_id)

    if request.method == 'POST':
        form = CustomUserEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('admin user details', user_id=user.id)
    else:
        form = CustomUserCreationForm(instance=user)

    return render(request, 'admin/users/user_edit.html', {'form': form, 'user': user})


@user_passes_test(lambda u: u.is_superuser)
def delete_user(request, user_id):
    user = get_object_or_404(FitnessUser, pk=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('admin users list')
    return render(request, 'admin/users/user_confirm_delete.html', {'user': user})


@user_passes_test(lambda u: u.is_superuser)
@login_required
def toggle_user_active_status(request, pk):
    user = get_object_or_404(FitnessUser, id=pk)

    if user == request.user:
        return redirect('admin users list')

    user.is_active = not user.is_active
    user.save()
    return redirect('admin users list')


@user_passes_test(lambda u: u.is_superuser)
def admin_trainers_list(request):
    trainers = Trainer.objects.select_related('user').order_by('id')
    return render(request, 'admin/trainers/list.html', {'trainers': trainers})


@user_passes_test(lambda u: u.is_superuser)
def admin_trainer_details(request, trainer_id):
    trainer = get_object_or_404(Trainer, pk=trainer_id)
    return render(request, 'admin/trainers/details.html', {
        'trainer': trainer,
        'profile_picture_url': trainer.user.profile_picture.url if trainer.user.profile_picture else None
    })


@user_passes_test(lambda u: u.is_superuser)
def admin_trainer_create(request):
    if request.method == 'POST':
        form = TrainerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin trainers list')
    else:
        form = TrainerForm()
    return render(request, 'admin/trainers/create.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
def admin_trainer_edit(request, trainer_id):
    trainer = get_object_or_404(Trainer, pk=trainer_id)
    user = trainer.user

    if request.method == 'POST':
        trainer_form = TrainerForm(request.POST, instance=trainer)
        user_form = UserProfilePictureForm(request.POST, request.FILES, instance=user)

        if trainer_form.is_valid() and user_form.is_valid():
            trainer_form.save()
            user_form.save()
            return redirect('admin trainer details', trainer_id=trainer.id)
    else:
        trainer_form = TrainerForm(instance=trainer)
        user_form = UserProfilePictureForm(instance=user)

    return render(request, 'admin/trainers/edit.html', {
        'trainer_form': trainer_form,
        'user_form': user_form,
        'trainer': trainer,
    })


@user_passes_test(lambda u: u.is_superuser)
def admin_trainer_delete(request, trainer_id):
    trainer = get_object_or_404(Trainer, pk=trainer_id)
    if request.method == 'POST':
        trainer.delete()
        return redirect('admin trainers list')
    return render(request, 'admin/trainers/delete_confirm.html', {'trainer': trainer})


@user_passes_test(lambda u: u.is_superuser)
def admin_clients_list(request):
    clients = Client.objects.select_related('user', 'trainer').order_by('id')
    return render(request, 'admin/clients/list.html', {'clients': clients})


@user_passes_test(lambda u: u.is_superuser)
def admin_client_details(request, client_id):
    client = get_object_or_404(Client, pk=client_id)
    return render(request, 'admin/clients/details.html', {'client': client})


@user_passes_test(lambda u: u.is_superuser)
def admin_client_edit(request, client_id):
    client = get_object_or_404(Client, pk=client_id)
    user = client.user

    if request.method == 'POST':
        client_form = ClientForm(request.POST, instance=client)
        user_form = UserProfilePictureForm(request.POST, request.FILES, instance=user)

        if client_form.is_valid() and user_form.is_valid():
            client_form.save()
            user_form.save()
            return redirect('admin client details', client_id=client.id)
    else:
        client_form = ClientForm(instance=client)
        user_form = UserProfilePictureForm(instance=user)

    return render(request, 'admin/clients/edit.html', {
        'client_form': client_form,
        'user_form': user_form,
        'client': client,
    })


@user_passes_test(lambda u: u.is_superuser)
def admin_client_create(request):
    if request.method == 'POST':
        client_form = ClientForm(request.POST)
        if client_form.is_valid():
            client = client_form.save()
            return redirect('admin client details', client_id=client.id)
    else:
        client_form = ClientForm()

    return render(request, 'admin/clients/create.html', {'client_form': client_form})


@user_passes_test(lambda u: u.is_superuser)
def admin_client_delete(request, client_id):
    client = get_object_or_404(Client, pk=client_id)
    if request.method == 'POST':
        client.delete()
        return redirect('admin clients list')
    return render(request, 'admin/clients/delete.html', {'client': client})


@user_passes_test(lambda u: u.is_superuser)
def admin_progress_list(request):
    progress_entries = Progress.objects.select_related('client').order_by('-progress_date')
    return render(request, 'admin/progress/list.html', {'progress_entries': progress_entries})


@user_passes_test(lambda u: u.is_superuser)
def admin_progress_details(request, progress_id):
    progress = get_object_or_404(Progress, pk=progress_id)
    return render(request, 'admin/progress/details.html', {'progress': progress})


@user_passes_test(lambda u: u.is_superuser)
def admin_progress_edit(request, progress_id):
    progress = get_object_or_404(Progress, pk=progress_id)
    if request.method == 'POST':
        form = ProgressForm(request.POST, instance=progress)
        if form.is_valid():
            form.save()
            return redirect('admin progress details', progress_id=progress.id)
    else:
        form = ProgressForm(instance=progress)

    return render(request, 'admin/progress/edit.html', {'form': form, 'progress': progress})


@user_passes_test(lambda u: u.is_superuser)
def admin_progress_create(request):
    if request.method == 'POST':
        form = ProgressForm(request.POST)
        if form.is_valid():
            progress = form.save()
            return redirect('admin progress details', progress_id=progress.id)
    else:
        form = ProgressForm()

    return render(request, 'admin/progress/create.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
def admin_progress_delete(request, progress_id):
    progress = get_object_or_404(Progress, pk=progress_id)
    if request.method == 'POST':
        progress.delete()
        return redirect('admin progress list')
    return render(request, 'admin/progress/delete_confirm.html', {'progress': progress})


@user_passes_test(lambda u: u.is_superuser)
def admin_exercises_list(request):
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()

    exercises = Exercise.objects.all()

    if query:
        exercises = exercises.filter(name__icontains=query)

    if category:
        exercises = exercises.filter(category=category)

    exercises = exercises.order_by('name')
    categories = Exercise.ExerciseCategory.choices() if hasattr(Exercise,
                                                                'ExerciseCategory') else ExerciseCategory.choices()

    return render(request, 'admin/exercises/list.html', {
        'exercises': exercises,
        'query': query,
        'category': category,
        'categories': categories,
    })


@user_passes_test(lambda u: u.is_superuser)
def admin_exercise_details(request, exercise_id):
    exercise = get_object_or_404(Exercise, pk=exercise_id)
    return render(request, 'admin/exercises/details.html', {'exercise': exercise})


@user_passes_test(lambda u: u.is_superuser)
def admin_exercise_create(request):
    if request.method == 'POST':
        form = ExerciseAddForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin exercises list')
    else:
        form = ExerciseAddForm()
    return render(request, 'admin/exercises/create.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
def admin_exercise_edit(request, exercise_id):
    exercise = get_object_or_404(Exercise, pk=exercise_id)
    if request.method == 'POST':
        form = ExerciseAddForm(request.POST, request.FILES, instance=exercise)
        if form.is_valid():
            form.save()
            return redirect('admin exercise details', exercise_id=exercise.id)
    else:
        form = ExerciseAddForm(instance=exercise)
    return render(request, 'admin/exercises/edit.html', {'form': form, 'exercise': exercise})


@user_passes_test(lambda u: u.is_superuser)
def admin_exercise_delete(request, exercise_id):
    exercise = get_object_or_404(Exercise, pk=exercise_id)
    if request.method == 'POST':
        exercise.delete()
        return redirect('admin exercises list')
    return render(request, 'admin/exercises/delete.html', {'exercise': exercise})


@user_passes_test(lambda u: u.is_superuser)
def admin_meals_list(request):
    query = request.GET.get('q', '')
    meal_type = request.GET.get('meal_type', '')

    meals = Meal.objects.select_related('client__user').order_by('-date')

    if query:
        meals = meals.filter(
            Q(client__user__first_name__icontains=query) |
            Q(client__user__last_name__icontains=query) |
            Q(client__user__email__icontains=query)
        )

    if meal_type:
        meals = meals.filter(meal=meal_type)

    meal_type_choices = Meal.meal_type_choices() if hasattr(Meal, 'meal_type_choices') else MealType.choices()

    return render(request, 'admin/meals/list.html', {
        'meals': meals,
        'query': query,
        'meal_type': meal_type,
        'meal_type_choices': meal_type_choices,
    })


def admin_meal_create(request):
    if request.method == 'POST':
        form = MealAdminForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin meals list')
    else:
        form = MealAdminForm()

    return render(request, 'admin/meals/create.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
def admin_meal_details(request, meal_id):
    meal = get_object_or_404(Meal, pk=meal_id)
    return render(request, 'admin/meals/details.html', {'meal': meal})


@user_passes_test(lambda u: u.is_superuser)
def admin_meal_edit(request, meal_id):
    meal = get_object_or_404(Meal, pk=meal_id)
    if request.method == 'POST':
        form = MealAdminForm(request.POST, instance=meal)
        if form.is_valid():
            form.save()
            return redirect('admin meal details', meal_id=meal.id)
    else:
        form = MealAdminForm(instance=meal)
    return render(request, 'admin/meals/edit.html', {'form': form, 'meal': meal})


@user_passes_test(lambda u: u.is_superuser)
def admin_meal_delete(request, meal_id):
    meal = get_object_or_404(Meal, pk=meal_id)
    if request.method == 'POST':
        meal.delete()
        return redirect('admin meals list')
    return render(request, 'admin/meals/delete.html', {'meal': meal})


@user_passes_test(lambda u: u.is_superuser)
def admin_reviews_list(request):
    if request.GET.get('pending') == 'true':
        reviews = AppReview.objects.filter(is_approved=False).select_related('client__user').order_by('-created_at')
    else:
        reviews = AppReview.objects.select_related('client__user').order_by('-is_approved', '-created_at')

    return render(request, 'admin/reviews/review_list.html', {
        'title': 'Отзиви от потребители',
        'columns': ['ID', 'Потребител', 'Оценка', 'Коментар', 'Дата', 'Статус', 'Действия'],
        'reviews': reviews,
    })


@user_passes_test(lambda u: u.is_superuser)
def approve_review(request, review_id):
    review = get_object_or_404(AppReview, pk=review_id)
    review.is_approved = True
    review.save()
    return redirect('admin reviews list')


@user_passes_test(lambda u: u.is_superuser)
def reject_review(request, review_id):
    review = get_object_or_404(AppReview, pk=review_id)
    review.delete()
    return redirect('admin reviews list')


@user_passes_test(lambda u: u.is_superuser)
def admin_plans_list(request):
    plans = NutritionPlan.objects.select_related('client', 'client__user').all()
    return render(request, 'admin/plans_list.html', {'plans': plans})
