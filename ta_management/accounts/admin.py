from django.contrib import admin
from .models import Application, Course

# Register your models here.

# Register the Application and Course models to make them accessible in the admin interface
admin.site.register(Application)
admin.site.register(Course)
