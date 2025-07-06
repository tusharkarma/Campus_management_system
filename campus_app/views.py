from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Student,Faculty,Course
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Faculty, Student, Course, Assignment, Notification, Attendance,Department
from .forms import AssignmentForm, NotificationForm
from datetime import date 
from django.views.decorators.csrf import csrf_exempt


def index(request):
    return render(request, 'index.html')


def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('/admin/login/?next=/admin/')  # Or redirect to a custom dashboard
        else:
            return render(request, "admin_login.html", {"error": "Invalid credentials or not an admin."})
    
    return render(request, "admin_login.html")

@csrf_exempt
def student_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('student_dashboard')  # or wherever you want
        else:
            messages.error(request, "Invalid credentials.")
            return redirect('student_login')

    return render(request, 'student_login.html')

@csrf_exempt
def student_signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        enrollment_number = request.POST.get('enrollment_number')
        department_id = request.POST.get('department')  # assuming you're using a dropdown

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('student_signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('student_signup')

        user = User.objects.create_user(username=username, email=email, password=password)

        # Get department object safely
        try:
            department = Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            department = None

        # Create corresponding Student record
        Student.objects.create(
            user=user,
            enrollment_number=enrollment_number,
            department=department
        )

        messages.success(request, "Signup successful. Please log in.")
        return redirect('student_login')

    departments = Department.objects.all()  # To populate the department dropdown
    return render(request, 'student_signup.html', {'departments': departments})


def student_logout(request):
    logout(request)
    return redirect('student_login')

@csrf_exempt
@login_required
def student_dashboard(request):
    student = Student.objects.get(user=request.user)

    courses = student.courses.all()
    attendance_records = Attendance.objects.filter(student=student)
    assignments = Assignment.objects.all().order_by('-due_date')
    # notifications = Notification.objects.filter(creator=request.user).order_by('-created_at')
    # notifications = Notification.objects.filter(course__in=courses).order_by('-created_at')
    notifications = Notification.objects.all().order_by('-created_at')



    context = {
        'student': student,
        'courses': courses,
        'attendance': attendance_records,
        'assignments': assignments,
        'notifications': notifications,
    }

    return render(request, 'student_dashboard.html', context)


def faculty_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('faculty_dashboard')
        else:
            return render(request, 'faculty/login.html', {'error': 'Invalid credentials'})

    return render(request, 'faculty_login.html')


def faculty_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        department_id = request.POST.get('department')
        course_ids = request.POST.getlist('courses')  # Get multiple course IDs

        if password1 != password2:
            return render(request, 'faculty/signup.html', {
                'error': 'Passwords do not match',
                'departments': Department.objects.all(),
                'courses': Course.objects.all(),
            })

        if User.objects.filter(username=username).exists():
            return render(request, 'faculty/signup.html', {
                'error': 'Username already exists',
                'departments': Department.objects.all(),
                'courses': Course.objects.all(),
            })

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password1)

        # Get department instance
        department = Department.objects.get(id=department_id)

        # Create faculty and associate department
        faculty = Faculty.objects.create(user=user, department=department)

        # Assign courses (many-to-many relationship)
        for course_id in course_ids:
            course = Course.objects.get(id=course_id)
            faculty.courses.add(course)  # Assuming Faculty has a ManyToManyField to Course

        login(request, user)
        return redirect('faculty_dashboard')

    # GET request
    return render(request, 'faculty_signup.html', {
        'departments': Department.objects.all(),
        'courses': Course.objects.all()
    })


def faculty_logout(request):
    logout(request)
    return redirect('faculty_login')



@login_required
def faculty_dashboard(request):
    faculty = Faculty.objects.get(user=request.user)
    courses = Course.objects.filter(faculty=faculty)
    students = Student.objects.filter(department=faculty.department)

    assignments = Assignment.objects.filter(created_by=faculty)
    notifications = Notification.objects.filter(creator=faculty)

    context = {
        'faculty': faculty,
        'courses': courses,
        'students': students,
        'assignments': assignments,
        'notifications': notifications,
    }
    return render(request, 'faculty_dashboard.html', context)

@login_required
def create_assignment(request):
    faculty = Faculty.objects.get(user=request.user)

    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.created_by = faculty
            assignment.save()
            return redirect('faculty_dashboard')
    else:
        form = AssignmentForm()

    # Set course queryset
    course_qs = Course.objects.filter(faculty=faculty)
    form.fields['course'].queryset = course_qs

    return render(request, 'create_assignment.html', {
        'form': form,
        'courses': course_qs,  # ✅ Manually pass to the template
    })



@login_required
def post_notification(request):
    faculty = Faculty.objects.get(user=request.user)

    if request.method == 'POST':
        form = NotificationForm(request.POST)
        if form.is_valid():
            notification = form.save(commit=False)
            notification.creator = faculty
            notification.save()
            return redirect('faculty_dashboard')
    else:
        form = NotificationForm()

    return render(request, 'post_notification.html', {'form': form})


