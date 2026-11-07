from django.contrib import admin

# Register your models here.
from .models import DailyCheckIn, WorkSession, CBTIntervention

admin.site.register(DailyCheckIn)
admin.site.register(WorkSession)
admin.site.register(CBTIntervention)