from django.contrib import admin
from .models import Bottle

@admin.register(Bottle)
class BottleAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)
