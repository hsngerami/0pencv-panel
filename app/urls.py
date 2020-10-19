from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from app.views import index

app_name = 'PicMove'

urlpatterns = [
                  path('', index, name='Index'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
