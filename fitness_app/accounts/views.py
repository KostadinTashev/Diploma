from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.templatetags.static import static
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.paginator import Paginator

from django.views import generic as views, View
from django.contrib.auth import views as auth_views, logout, get_user_model, login
from django.views.generic import CreateView

from fitness_app.accounts.forms import RegisterUserForm, CustomUserCreationForm, TrainerForm, UserProfilePictureForm, \
    ClientForm, MealAdminForm, CustomUserEditForm, WorkoutAdminForm, WorkoutExerciseFormAdminSet, \
    ProgramExerciseAdminForm, ProductForm, TrainerAdminEditForm
from fitness_app.accounts.models import FitnessUser
from fitness_app.clients.models import Client, AppReview
from fitness_app.exercises.forms import ExerciseAddForm
from fitness_app.exercises.models import User, Exercise, ExerciseCategory
from fitness_app.meals.models import Meal, MealType, Product, FoodItem
from fitness_app.nutrition_plans.forms import NutritionPlanForm, MealFormAddSet, NutritionPlanEditForm, MealFormEditSet, \
    FoodItemFormAddSet, FoodFormEditSet
from fitness_app.nutrition_plans.models import NutritionPlan
from fitness_app.program_exercises.models import ProgramExercise
from fitness_app.progress.forms import ProgressForm
from fitness_app.progress.models import Progress
from fitness_app.trainers.models import Trainer
from fitness_app.workouts.forms import WorkoutExerciseFormSet, WorkoutForm
from fitness_app.workouts.models import Workout

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
        form = CustomUserEditForm(instance=user)

    return render(request, 'admin/users/user_edit.html', {
        'form': form,
        'user': user,
    })


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
    if request.method == "POST":
        form = TrainerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("admin trainers list")
    else:
        form = TrainerForm()
    return render(request, "admin/trainers/create.html", {"form": form})


@user_passes_test(lambda u: u.is_superuser)
def admin_trainer_edit(request, trainer_id):
    trainer = get_object_or_404(Trainer, pk=trainer_id)

    if request.method == "POST":
        form = TrainerAdminEditForm(request.POST, request.FILES, instance=trainer)
        if form.is_valid():
            form.save()
            return redirect("admin trainer details", trainer_id=trainer.id)
    else:
        form = TrainerAdminEditForm(instance=trainer)

    return render(request, "admin/trainers/edit.html", {
        "form": form,
        "trainer": trainer,
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
def admin_workouts_list(request):
    workouts = Workout.objects.all()
    return render(request, 'admin/workouts/list.html', {
        'workouts': workouts
    })


@user_passes_test(lambda u: u.is_superuser)
def admin_workout_details(request, workout_id):
    workout = get_object_or_404(
        Workout.objects.prefetch_related('exercises__exercise'),
        pk=workout_id
    )

    assigned_clients = Client.objects.filter(
        programexercise__workout=workout
    ).select_related('user').distinct()

    return render(request, 'admin/workouts/details.html', {
        'workout': workout,
        'assigned_clients': assigned_clients,
    })


@user_passes_test(lambda u: u.is_superuser)
@transaction.atomic
def admin_workout_create(request):
    if request.method == "POST":
        w_form = WorkoutAdminForm(request.POST)
        ex_fset = WorkoutExerciseFormAdminSet(request.POST)

        if w_form.is_valid() and ex_fset.is_valid():
            workout = w_form.save()
            ex_fset.instance = workout
            ex_fset.save()
            return redirect(
                "admin workout details",
                workout_id=workout.id,
            )
    else:
        w_form = WorkoutAdminForm()
        ex_fset = WorkoutExerciseFormAdminSet()

    return render(
        request,
        "admin/workouts/create.html",
        {"form": w_form, "formset": ex_fset},
    )


@user_passes_test(lambda u: u.is_superuser)
@transaction.atomic
def admin_workout_edit(request, workout_id):
    workout = get_object_or_404(Workout, pk=workout_id)

    if request.method == "POST":
        w_form = WorkoutAdminForm(request.POST, instance=workout)
        ex_fset = WorkoutExerciseFormAdminSet(request.POST, instance=workout)

        if w_form.is_valid() and ex_fset.is_valid():
            w_form.save()
            ex_fset.save()
            return redirect(
                "admin workout details",
                workout_id=workout.id,
            )
    else:
        w_form = WorkoutAdminForm(instance=workout)
        ex_fset = WorkoutExerciseFormAdminSet(instance=workout)

    return render(
        request,
        "admin/workouts/edit.html",
        {"form": w_form, "formset": ex_fset, "workout": workout},
    )


@user_passes_test(lambda u: u.is_superuser)
@transaction.atomic()
def admin_workout_create(request):
    if request.method == "POST":
        w_form = WorkoutForm(request.POST)
        ex_fset = WorkoutExerciseFormSet(request.POST)

        if w_form.is_valid() and ex_fset.is_valid():
            workout = w_form.save()
            ex_fset.instance = workout
            ex_fset.save()
            return redirect("admin workout details", workout_id=workout.id)
    else:
        w_form = WorkoutAdminForm()
        ex_fset = WorkoutExerciseFormAdminSet()

    return render(
        request,
        "admin/workouts/create.html",
        {"form": w_form, "formset": ex_fset},
    )


@user_passes_test(lambda u: u.is_superuser)
def admin_workout_delete(request, workout_id):
    workout = get_object_or_404(Workout, pk=workout_id)
    if request.method == 'POST':
        workout.delete()
        return redirect('admin workouts list')
    return render(request, 'admin/workouts/delete.html', {'workout': workout})


@user_passes_test(lambda u: u.is_superuser)
def admin_program_list(request):
    programs = (ProgramExercise.objects
                .select_related("client__user", "workout")
                .order_by("-date", "client__user__last_name"))
    return render(request, "admin/programs/list.html", {"programs": programs})


@user_passes_test(lambda u: u.is_superuser)
@transaction.atomic
def admin_program_create(request):
    if request.method == "POST":
        form = ProgramExerciseAdminForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("admin program list")
    else:
        form = ProgramExerciseAdminForm()
    return render(request, "admin/programs/form.html",
                  {"form": form, "title": "Създай назначение"})


@user_passes_test(lambda u: u.is_superuser)
def admin_program_details(request, pk):
    program = get_object_or_404(
        ProgramExercise.objects.select_related(
            "client__user", "workout"), pk=pk)
    return render(request, "admin/programs/details.html",
                  {"program": program})


@user_passes_test(lambda u: u.is_superuser)
@transaction.atomic
def admin_program_edit(request, pk):
    program = get_object_or_404(ProgramExercise, pk=pk)
    if request.method == "POST":
        form = ProgramExerciseAdminForm(request.POST, instance=program)
        if form.is_valid():
            form.save()
            return redirect("admin program details", pk=pk)
    else:
        form = ProgramExerciseAdminForm(instance=program)
    return render(request, "admin/programs/form.html",
                  {"form": form, "title": "Редакция на назначение"})


@user_passes_test(lambda u: u.is_superuser)
@transaction.atomic
def admin_program_delete(request, pk):
    program = get_object_or_404(ProgramExercise, pk=pk)
    if request.method == "POST":
        program.delete()
        return redirect("admin program list")
    return render(request, "admin/programs/delete.html",
                  {"program": program})


@user_passes_test(lambda u: u.is_superuser)
def admin_products_list(request):
    sort = request.GET.get("sort", "name")

    allowed = {
        "name": "name",
        "-name": "-name",
        "cal": "calories_per_100g",
        "-cal": "-calories_per_100g",
        "pro": "proteins_per_100g",
        "-pro": "-proteins_per_100g",
        "carb": "carbohydrates_per_100g",
        "-carb": "-carbohydrates_per_100g",
        "fat": "fats_per_100g",
        "-fat": "-fats_per_100g",
    }
    order_clause = allowed.get(sort, "name")

    products_qs = Product.objects.order_by(order_clause)

    base_cols = [
        ("name", "Име", "start"),
        ("cal", "Ккал", "end"),
        ("pro", "Протеини", "end"),
        ("carb", "Въглехидрати", "end"),
        ("fat", "Мазнини", "end"),
    ]

    cols = []
    for code, label, align in base_cols:
        if sort == code:
            next_code, arrow = f"-{code}", "▲"
        elif sort == f"-{code}":
            next_code, arrow = code, "▼"
        else:
            next_code, arrow = code, ""
        cols.append({
            "label": label,
            "arrow": arrow,
            "next": next_code,
            "align": f"text-{align}",
        })

    q = request.GET.get("q", "").strip()
    if q:
        products_qs = products_qs.filter(name__icontains=q)

    from django.core.paginator import Paginator
    page_obj = Paginator(products_qs, 100).get_page(request.GET.get("page"))

    context = {
        "products": page_obj,
        "page_obj": page_obj,
        "cols": cols,
        "sort": sort,
        "q": q,
    }
    return render(request, "admin/products/list.html", context)


@user_passes_test(lambda u: u.is_superuser)
def admin_product_create(request):
    form = ProductForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        product = form.save()
        messages.success(request, f"Продукт „{product.name}“ създаден успешно.")
        return redirect("admin product detail", pk=product.pk)
    return render(request, "admin/products/create.html", {"form": form})


@user_passes_test(lambda u: u.is_superuser)
def admin_product_details(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "admin/products/detail.html", {"product": product})


@user_passes_test(lambda u: u.is_superuser)
def admin_product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=product)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Данните са обновени.")
        return redirect("admin product detail", pk=pk)
    return render(request, "admin/products/edit.html", {"form": form, "product": product})


@user_passes_test(lambda u: u.is_superuser)
def admin_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.delete()
        messages.success(request, "Продуктът беше изтрит.")
        return redirect("admin products list")
    return render(request, "admin/products/delete.html", {"product": product})


@user_passes_test(lambda u: u.is_superuser)
def admin_plans_list(request):
    clients = Client.objects.select_related("user").prefetch_related("nutrition_plans")
    return render(request, "admin/plans/list.html", {"clients": clients})


@user_passes_test(lambda u: u.is_superuser)
@transaction.atomic
def admin_plan_create(request):
    client_id = request.GET.get("client")
    preselected_client = (
        get_object_or_404(Client, pk=client_id) if client_id else None
    )

    if request.method == "POST":
        plan_form = NutritionPlanForm(request.POST)
        meal_fset = MealFormAddSet(request.POST, prefix="meals")

        food_fsets, valid = [], plan_form.is_valid() and meal_fset.is_valid()
        for i, meal_form in enumerate(meal_fset):
            prefix = f"foods-{i}"
            fs = FoodItemFormAddSet(
                request.POST,
                prefix=prefix,
                instance=meal_form.instance if meal_form.instance.pk else None,
            )
            food_fsets.append(fs)
            if not fs.is_valid():
                valid = False

        if valid:
            plan = plan_form.save(commit=False)
            if preselected_client:
                plan.client = preselected_client
            plan.save()

            meals = meal_fset.save(commit=False)
            for i, meal in enumerate(meals):
                meal.plan = plan
                meal.save()
                food_fsets[i].instance = meal
                food_fsets[i].save()

            return redirect("admin plan detail", pk=plan.pk)

    else:
        initial = {"client": preselected_client} if preselected_client else None
        plan_form = NutritionPlanForm(initial=initial)

        meal_fset = MealFormAddSet(queryset=Meal.objects.none(), prefix="meals")
        food_fsets = [
            FoodItemFormAddSet(prefix="foods-0", queryset=FoodItem.objects.none())
        ]

    context = {
        "is_edit": False,
        "plan_form": plan_form,
        "meal_formset": meal_fset,
        "food_formsets": food_fsets,
        "empty_meal_form": MealFormAddSet(
            queryset=Meal.objects.none(), prefix="meals"
        ).empty_form,
        "empty_food_formset": FoodItemFormAddSet(
            prefix="foods-__prefix__", queryset=FoodItem.objects.none()
        ),
        "preselected_client": preselected_client,
    }
    return render(request, "admin/plans/create.html", context)


@user_passes_test(lambda u: u.is_superuser)
def admin_plan_details(request, pk):
    plan = (
        NutritionPlan.objects
        .select_related("client__user")
        .prefetch_related("meals__food_items__product")
        .get(pk=pk)
    )

    meals_by_day: dict[str, list] = {}
    for meal in plan.meals.all().order_by("date"):
        formatted = meal.date.strftime("%d %B %Y")
        meals_by_day.setdefault(formatted, []).append({
            "meal": meal.meal,
            "description": meal.description,
            "calories": meal.calories,
            "carbohydrate": meal.carbohydrate,
            "fats": meal.fats,
            "proteins": meal.proteins,
            "products": meal.food_items.all(),
        })

    return render(
        request,
        "admin/plans/details.html",
        {"plan": plan, "meals_by_day": meals_by_day},
    )


@user_passes_test(lambda u: u.is_superuser)
@transaction.atomic
def admin_plan_edit(request, pk):
    plan = get_object_or_404(
        NutritionPlan.objects.select_related("client__user"), pk=pk
    )

    if request.method == "POST":
        print("\n==========  PLAN EDIT DEBUG  ==========")

        plan_form = NutritionPlanForm(request.POST, instance=plan)
        meal_fset = MealFormEditSet(request.POST, instance=plan, prefix="meals")

        food_fsets = []
        for m_form in meal_fset.forms:
            idx = m_form.prefix.split("-")[-1]
            food_fsets.append(
                FoodFormEditSet(
                    request.POST,
                    instance=m_form.instance,
                    prefix=f"foods-{idx}",
                )
            )

        forms_valid = (
                plan_form.is_valid()
                and meal_fset.is_valid()
                and all(fs.is_valid() for fs in food_fsets)
        )

        print(f"✔ plan_form.valid? {plan_form.is_valid()}")
        print(f"✔ meal_fset.valid?  {meal_fset.is_valid()}")
        for i, fs in enumerate(food_fsets):
            print(f"✔ food_fsets[{i}].valid? {fs.is_valid()}")

        if forms_valid:
            print("ALL forms valid – committing to DB.")
            with transaction.atomic():
                plan = plan_form.save()

                meal_fset.save()

                for m_form, fs in zip(meal_fset.forms, food_fsets):
                    if m_form.cleaned_data.get("DELETE"):
                        continue
                    fs.instance = m_form.instance
                    fs.save()

            print("==========  END DEBUG (valid) ==========\n")
            messages.success(request, "Режимът беше обновен успешно.")
            return redirect("admin plan detail", pk=plan.pk)

        print("==========  END DEBUG (invalid)  ==========\n")
        messages.error(request, "Моля, коригирай грешките във формата.")

    else:
        plan_form = NutritionPlanForm(instance=plan)
        meal_fset = MealFormEditSet(instance=plan, prefix="meals")
        food_fsets = [
            FoodFormEditSet(instance=m.instance, prefix=f"foods-{i}")
            for i, m in enumerate(meal_fset.forms)
        ]

    context = {
        "is_edit": True,
        "plan": plan,
        "plan_form": plan_form,
        "meal_formset": meal_fset,
        "food_formsets": food_fsets,
        "empty_meal_form": MealFormAddSet(
            queryset=Meal.objects.none(), prefix="meals"
        ).empty_form,
        "empty_food_formset": FoodItemFormAddSet(
            prefix="foods-__prefix__", queryset=FoodItem.objects.none()
        ),
    }
    return render(request, "admin/plans/create.html", context)


@user_passes_test(lambda u: u.is_superuser)
def admin_plan_delete(request, pk):
    plan = get_object_or_404(NutritionPlan, pk=pk)
    if request.method == "POST":
        plan.delete()
        messages.success(request, "Планът беше изтрит.")
        return redirect("admin plans list")
    return render(request, "admin/plans/delete.html", {"plan": plan})
