# your_project_name/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.urls import re_path
from django.views.generic import TemplateView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('check/', include('check.urls')),  # Include the API URLs
    re_path(r'^cryptomus_33a04e6f.html$', TemplateView.as_view(template_name='cryptomus_33a04e6f.html')),
]

