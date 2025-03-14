from django.contrib import admin

from schedule.models import TimeSlot, WorkDay

# Register your models here.
admin.site.register(WorkDay)
admin.site.register(TimeSlot)
