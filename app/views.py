from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core import management
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import render

from app.models import Movement, Option


def background_process():
    import time
    print("process started")
    management.call_command('motion_detection')
    print("process finished")


@login_required()
def index(request):
    if request.method == "POST":
        is_camera_on = False if request.POST.get("camera") is None else True
        is_send_email = False if request.POST.get("send_email") is None else True
        is_minute = False if request.POST.get("check_minute") is None else True
        with_photo = False if request.POST.get("with_picture") is None else True

        is_camera_on_obj = Option.objects.get(key='is_camera_on')
        is_send_email_obj = Option.objects.get(key="is_send_email")
        is_minute_obj = Option.objects.get(key="is_minute")
        with_photo_obj = Option.objects.get(key="with_photo")

        if not is_camera_on_obj.value and is_camera_on:
            import threading
            t = threading.Thread(target=background_process, args=(), kwargs={})
            t.setDaemon(True)
            t.start()

        is_camera_on_obj.value = is_camera_on
        is_camera_on_obj.save()

        is_send_email_obj.value = is_send_email
        is_send_email_obj.save()

        is_minute_obj.value = is_minute
        is_minute_obj.save()

        with_photo_obj.value = with_photo
        with_photo_obj.save()

        context = {
            'is_camera_on': is_camera_on_obj.value,
            'is_send_email': is_send_email_obj.value,
            'is_minute': is_minute_obj.value,
            'with_photo': with_photo_obj.value,
            'movements': Movement.objects.order_by("datetime")
        }
        return render(request, 'index.html', context=context)
    else:

        context = {
            'is_camera_on': Option.objects.get(key='is_camera_on').value,
            'is_send_email': Option.objects.get(key='is_send_email').value,
            'is_minute': Option.objects.get(key='is_minute').value,
            'with_photo': Option.objects.get(key='with_photo').value,
            'movements': Movement.objects.order_by("datetime")
        }

        return render(request, 'index.html', context=context)
