from celery import shared_task
from .models import Post
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives

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
