from django.contrib import admin

# Register your models here.
from .models import Article,Customer

admin.site.register(Article)
admin.site.register(Customer)