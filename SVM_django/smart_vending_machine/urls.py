from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # default Django admin
    path('', include('vending_machine.urls')),  # our app
]
