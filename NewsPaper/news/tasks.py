from celery import shared_task
from .models import Post, Category
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from datetime import datetime, timedelta

@shared_task
def hello():
    print('task works')

@shared_task
def new_post(post_id):
    print('task started')
    post = Post.objects.get(id=post_id)
    html_content = render_to_string('post_created_mail.html', {'post': post})
    if Post.objects.filter(id=post.id).values('category__subscribers').exists():
        subs = Post.objects.filter(id=post.id).values('category__subscribers')
    else:
        subs = []
    emails = []
    if subs != []:
        for sub in subs:
            for i in User.objects.all():
                if i.id == sub['category__subscribers']:
                    emails.append(i.email)
    msg = EmailMultiAlternatives(
        subject=f'Новый материал {post.title}',
        body='Sended by Celery',
        from_email='da3c709e-298c-4bc6-98b5-30bfc7892069@debugmail.io',
        to=emails,
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    print('task finished')

@shared_task
def weekly_mail():
    print('weekly task started')
    i = 1
    while True:
        if not Category.objects.filter(id=i).exists():
            print('weekly task finished')
            break
        subs = Category.objects.filter(id=i).values('subscribers')
        if subs[0]['subscribers']:
            limit = datetime.now() - timedelta(days=7)
            emails = []
            for sub in subs:
                reciever = User.objects.get(id=sub['subscribers'])
                emails.append(reciever.email)
            if Post.objects.filter(category__id=i, time_creating__gt=limit).exists():
                news = Post.objects.filter(category__id=i, time_creating__gt=limit)
                html_content = render_to_string('weekly_mail.html', {'posts': news})
                msg = EmailMultiAlternatives(
                    subject=f'Новый материал за неделю в подписке',
                    body='Материалы',
                    from_email='da3c709e-298c-4bc6-98b5-30bfc7892069@debugmail.io',
                    to=emails,
                    )
                msg.attach_alternative(html_content, "text/html")
                msg.send()
        i += 1

