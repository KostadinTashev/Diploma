from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.templatetags.static import static
from django.urls import reverse_lazy, reverse

from django.views import generic as views
from django.contrib.auth import views as auth_views, logout, get_user_model, login

from fitness_app.accounts.forms import RegisterUserForm
from fitness_app.clients.models import Client
from fitness_app.exercises.models import User
from fitness_app.trainers.models import Trainer

UserModel = get_user_model()


class RegisterUserView(views.CreateView):
    template_name = "accounts/register-page.html"
    form_class = RegisterUserForm

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)

        goals = self.request.POST.get('goals')

        client = Client.objects.create(user=user, goals=goals)

        return redirect(reverse('set client data', kwargs={'client_id': client.id}))

    def get_success_url(self):
        return reverse('set client data', kwargs={'client_id': self.object.id})


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
