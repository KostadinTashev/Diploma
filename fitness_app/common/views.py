from django.core.mail import EmailMessage

from django.contrib import messages
from django.shortcuts import render, redirect

from fitness_app.clients.models import AppReview
from fitness_app.common.forms import ContactForm
from fitness_app.trainers.models import Trainer



def index(request):
    form = ContactForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        name = form.cleaned_data['name']
        email = form.cleaned_data['email']
        message = form.cleaned_data['message']

        email_message = EmailMessage(
            subject='Ново съобщение от контактната форма на Сила+',
            body=f'Име: {name}\nИмейл: {email}\n\nСъобщение:\n{message}',
            from_email='k.tashev02@gmail.com',
            to=['k.tashev02@gmail.com'],
            reply_to=[email],
        )
        email_message.send(fail_silently=False)

        messages.success(request, "Вашето съобщение беше изпратено успешно!")
        return redirect('index')

    trainers = Trainer.objects.all()
    reviews = AppReview.objects.all()
    context = {
        'form': form,
        'trainers': trainers,
        'reviews': reviews,
    }
    return render(request, 'common/index.html', context=context)
