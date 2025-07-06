from django.contrib import admin

# Register your models here.
from .models import Department, Student, Faculty, Course,Notification,Attendance,Assignment

admin.site.register(Department)
admin.site.register(Student)
admin.site.register(Faculty)
admin.site.register(Course)
admin.site.register(Attendance)
admin.site.register(Assignment)
admin.site.register(Notification)


