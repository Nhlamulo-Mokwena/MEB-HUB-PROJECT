from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.contrib import messages
from administration.models import Admin_Action
from .models import Student, RegisteredStudent, Admin
from django.contrib.auth import logout
from django.contrib.auth.hashers import check_password
from django.shortcuts import redirect
from datetime import date
from django.urls import reverse
import re
from django.utils import timezone
from django.db.models.functions import TruncDate
from bus.models import Route
from events.models import Event
from .models import Student, Campus
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import render
from .forms import ContactForm
from django.conf import settings 
from django.core.mail import send_mail, BadHeaderError
import re
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import RegisteredStudent, Student  # Adjust if models are elsewhere
from django.db import IntegrityError
from django.shortcuts import render, redirect
from .models import Student, Campus
from django.utils import timezone
from django.contrib import messages


# Create your views here.
def landing(request):
    return render(request,"login/landing_page.html")

def login(request):
    if request.method == 'POST':

        username = request.POST['email']
        password = request.POST['password']

        if Student.objects.filter(studentEmail=username).exists() or Admin.objects.filter(email=username).exists():

            if "@tut4life.ac.za" in username:

                try:
                    stud = Student.objects.all().get(studentEmail=username)
                    
                    if stud.password == password:
                        request.session['stud_id'] = stud.studentNumber
                        stud.login_time = timezone.now()
                        stud.save()
                        return redirect("account:home")
                        
                    else:
                        messages.error(request, "Incorrect Password!")
                        return redirect("account:login")

                except:
                    messages.error(request, "Incorrect Username")
                    return redirect("account:login")

            elif "@mebhub.ac.za" in username:
                try:

                    admin = Admin.objects.all().get(email=username)

                    try:
                        today = timezone.localdate()
                        actions = Admin_Action.objects.annotate(action_date=TruncDate('datetime')).filter(admin_id=admin.admin_id, action_date=today)
                        events = Event.objects.filter(date__year=today.year, date__month=today.month)
                        cnt_routes=Route.objects.count()
                    except Exception as e:
                        print(f"Error fetching actions or events: {e}")
                        actions = None
                        events=None

                    if admin.password == password:


                        request.session["admin_id"] = admin.admin_id

                        initials = f"{admin.name[0].upper()}{admin.surname[0].upper()}"
                        request.session["initials"]=initials

                        return render(request, "admin/admin.html", {
                        "admin": admin,
                        "actions": actions,
                        "events":events,
                        "initials":initials,
                        "cnt_routes":cnt_routes
                        })
                    else:
                        
                        messages.error(request, "Incorrect Password!")
                        return redirect("account:login")
                except:
                    messages.error(request, "Incorrect Username")
                    return redirect('account:login')
        else:
            
            messages.error(request, 'Account does not exist!')
            return redirect('account:login')
    else:
        return render(request, 'login/login.html')


def register(request):
    if request.method == 'POST':
        student_no = request.POST.get('student_no')
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        student_email = request.POST.get('student_email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
 
        form_data = {
            'student_no': student_no,
            'name': name,
            'surname': surname,
            'student_email': student_email
        }

        errors = {}
        
        pattern =  "@tut4life.ac.za"

        # Manual duplicate checks (better UX than letting the DB error)
        if not RegisteredStudent.objects.filter(studentNumber=student_no).exists():
            messages.error(request,"The student number not found!")
            return render(request,'login/register.html',{
                'form_data': form_data
            })
            
        if Student.objects.filter(studentNumber=student_no).exists():
            messages.error(request,"This student number is already registered!")
            return render(request,'login/register.html',{
                'form_data': form_data
            })
            
        if Student.objects.filter(studentEmail=student_email).exists():
            messages.error(request,"This email is already registered!")
            return render(request,'login/register.html',{
                'form_data': form_data
            })

        if not re.search(pattern,student_email):
            messages.error(request,"Use TUT student email")
            return render(request,'login/register.html',{
                'form_data': form_data
            })

        try:
            campus = RegisteredStudent.objects.all().get(studentNumber=student_no).campus_id
            student = Student(
                studentNumber=student_no,
                name=name,
                surname=surname,
                studentEmail=student_email,
                password=password,  # ❗ You should hash this
                campus_id=campus,
                login_time=timezone.now()
            )
            student.save()
            messages.success(request, "Registration successful.")
            return redirect('account:login')

        except IntegrityError:
            errors['student_no'] = "This student number already exists."
            return render(request, 'login/register.html', {
                'form_data': form_data,
                'errors': errors
            })

    return render(request, 'login/register.html', {
        'form_data': {},
        'errors': {}
    })



def admin(request):
    return render(request, "login/admin.html")

def logout_view(request):
    logout(request)
    return redirect('account:landing')

def home(request):
    if 'stud_id' in request.session:
        stud = Student.objects.all().get(studentNumber=request.session['stud_id'])
        initials = f"{stud.name[0].upper()}{stud.surname[0].upper()}"
        request.session["initials"] = initials
        return render(request,"home/home.html",{
        "email": stud,
        "initials": initials })
    else:
        return render(request,"login/landing_page.html")
        
def about(request):
    return render(request,'about_us/about_us.html')
def contact(request):
    return render(request, 'contact_us/contact_us.html')

def landing_about(request):
    return render(request,'login/landing_about.html')
def landing_contact(request):
    return render(request, 'login/landing_contactUs.html')

def update_profile(request):
        stud_id = request.session.get("stud_id")
        student = Student.objects.get(studentNumber=stud_id)
        initials=request.session.get("initials")

        if request.method == 'POST':
            student = Student.objects.get(studentNumber=stud_id)
            student.name = request.POST.get('name')
            student.surname = request.POST.get('surname')

            if student.name or student.surname:
                initials = f"{student.name[0].upper()}{student.surname[0].upper()}"
                request.session["initials"] = initials

            student_password= request.POST.get('password')
            if student_password:
                student.password=student_password

            student.save()
            messages.success(request, "Profile updated successfully! 🎉")

            # Redirect with actual student email in query param
            url = reverse('account:update_profile')
            return redirect(f'{url}?initials={initials}')


        return render(request, 'home/update_profile.html', {'student': student, 'initials': initials})


User = get_user_model()

 # Adjust import if models are in a different module

def reset_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "login/reset_password.html")

        student = Student.objects.filter(studentEmail=email).first()
        admin = Admin.objects.filter(email=email).first()

        if student:
            student.password = new_password  # You should hash passwords in production
            student.save()
            messages.success(request, "Student password reset successfully.")
            return redirect("account:login")
        elif admin:
            admin.password = new_password  # You should hash passwords in production
            admin.save()
            messages.success(request, "Admin password reset successfully.")
            return redirect("account:login")
        else:
            messages.error(request, "No student or admin found with that email.")

    return render(request, "login/reset_password.html")





