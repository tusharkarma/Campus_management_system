from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('student-login/', views.student_login, name='student_login'),
    path('student-signup/', views.student_signup, name='student_signup'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student-logout/', views.student_logout, name='student_logout'),
    path('faculty-login/', views.faculty_login, name='faculty_login'),
    path('faculty-signup/', views.faculty_signup, name='faculty_signup'),
    path('faculty/dashboard/', views.faculty_dashboard, name='faculty_dashboard'),
    path('faculty-logout/', views.faculty_logout, name='student_logout'),
    path('faculty/assignment/create/', views.create_assignment, name='create_assignment'),
    path('faculty/notification/create/', views.post_notification, name='post_notification'),
]
