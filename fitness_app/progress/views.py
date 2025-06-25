import json
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.generic import TemplateView

from fitness_app.clients.forms import ClientForm
from fitness_app.clients.models import Client, ClientGoals
from fitness_app.progress.forms import ProgressForm
from fitness_app.progress.models import Progress
from fitness_app.utils.body_fat_calculator import calculate_body_fat_percentage


@login_required
def add_progress(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    progress_entries = Progress.objects.filter(client=client).order_by('-progress_date')

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        start_date_parsed = parse_date(start_date)
        end_date_parsed = parse_date(end_date)
        if start_date_parsed and end_date_parsed:
            progress_entries = progress_entries.filter(progress_date__range=[start_date_parsed, end_date_parsed])

    if request.method == 'POST':
        progress_form = ProgressForm(request.POST)
        new_goal = request.POST.get('goals')
        keep_same_trainer = request.POST.get('keep_same_trainer')

        if progress_form.is_valid():
            progress = progress_form.save(commit=False)
            progress.client = client

            body_fat = calculate_body_fat_percentage(
                gender=client.user.gender,
                height=progress.height,
                neck=progress.neck,
                waist=progress.waist,
                hip=progress.hip
            )
            if body_fat is not None:
                body_fat_decimal = Decimal(str(body_fat))
                progress.body_fat_percentage = body_fat_decimal
                progress.muscle_mass = progress.weight * (Decimal('1') - (body_fat_decimal / Decimal('100')))
            else:
                progress.body_fat_percentage = Decimal('0')
                progress.muscle_mass = None

            progress.save()

            if new_goal and new_goal != client.goals:
                client.goals = new_goal
                if keep_same_trainer == 'yes':
                    client.save()
                    return redirect('current progress', client_id=client.pk)
                else:
                    client.save()
                    return redirect('suitable trainers')

            return redirect('current progress', client_id=client.pk)

    else:
        last_progress = progress_entries.first()
        if last_progress:
            initial_data = {
                'progress_date': timezone.now().date(),
                'weight': last_progress.weight,
                'height': last_progress.height,
                'neck': last_progress.neck,
                'chest': last_progress.chest,
                'waist': last_progress.waist,
                'hip': last_progress.hip,
            }
        else:
            initial_data = {'progress_date': timezone.now().date()}

        progress_form = ProgressForm(initial=initial_data)

    context = {
        'progress_form': progress_form,
        'progress_entries': progress_entries,
        'start_date': start_date,
        'end_date': end_date,
        'client': client,
        'goals_choices': ClientGoals.choices(),
        'is_client_user': hasattr(request.user, 'client') and request.user.client.id == client.id,

    }
    return render(request, 'progress/add_progress.html', context=context)


@login_required
def progress_chart(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    progress_data = Progress.objects.filter(client=client).order_by('progress_date')

    context = {
        'client': client,
        'dates': json.dumps([entry.progress_date.strftime('%Y-%m-%d') for entry in progress_data]),
        'weights': json.dumps([float(entry.weight) for entry in progress_data]),
        'body_fat': json.dumps([float(entry.body_fat_percentage or 0) for entry in progress_data]),
        'muscle_mass': json.dumps([float(entry.muscle_mass or 0) for entry in progress_data]),
        'request': request
    }
    return render(request, 'progress/progress_chart.html', context=context)


@login_required
def client_progress_view(request, client_id, username=None):
    client = get_object_or_404(Client, pk=client_id)
    progresses = Progress.objects.filter(client=client).order_by('progress_date')

    for p in progresses:
        if p.body_fat_percentage is None:
            p.body_fat_percentage = calculate_body_fat_percentage(
                gender=p.client.user.gender,
                height=p.height,
                neck=p.neck,
                waist=p.waist,
                hip=p.hip
            )

            p.save()

        if p.muscle_mass is None or p.muscle_mass == 0:
            if p.body_fat_percentage is not None:
                p.muscle_mass = float(p.weight) * (1 - float(p.body_fat_percentage) / 100)
                p.save()

    context = {
        'client': client,
        'dates': [p.progress_date.strftime('%Y-%m-%d') for p in progresses],
        'weights': [float(p.weight) for p in progresses],
        'body_fat': [float(p.body_fat_percentage or 0) for p in progresses],
        'muscle_mass': [float(p.muscle_mass) if p.muscle_mass is not None else 0 for p in progresses],
        'is_client_user': hasattr(request.user, 'client') and request.user.client.id == client.id,
    }

    return render(request, 'progress/progress_chart.html', context)


def client_progress(request):
    return None
