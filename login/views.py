from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.contrib import messages
from administration.models import Admin_Action
from .models import Student, RegisteredStudent, Admin
from django.contrib.auth import logout
from django.contrib.auth.hashers import check_password
from django.shortcuts import redirect


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
                        initials = f"{stud.name[0].upper()}{stud.surname[0].upper()}"
                        return render(request,"home/home.html",{
                            "email": stud,
                            "initials": initials
                        })
                    else:
                        messages.error(request, "Inccorect Username / Password!")
                        return redirect("/login")

                except:
                    messages.error(request, "Inccorect Username / Password!")
                    return redirect("/login")

            elif "@mebhub.ac.za" in username:
                try:

                    admin = Admin.objects.all().get(email=username)
                    
                    try:
                        actions = Admin_Action.objects.all().get(admin_id=admin.admin_id)
                    except:
                        actions = []

                    if admin.password == password:
                        return render(request,"admin/admin.html",{
                            "admin": admin,
                            "actions": actions
                        })
                    else:
                        
                        messages.error(request, "Inccorect Username / Password!")
                        return redirect("/login")
                except:
                    messages.error(request, "Incorrect Username / Password!")
                    return redirect('/login')
        else:
            
            messages.error(request, 'Account does not exist!')
            return redirect('/login')
    else:
        return render(request, 'login/login.html')


def register(request):
    if request.method == 'POST':
        student_no = request.POST['student_no']
        name = request.POST['name']
        surname = request.POST['surname']
        student_email = request.POST['student_email']
        password = request.POST['password']
        password_confirmation = request.POST['confirm_password']

        if RegisteredStudent.objects.filter(studentNumber=student_no).exists():
            if password == password_confirmation:
                camp_id = RegisteredStudent.objects.all().get(studentNumber=student_no).campus_id
                student = Student(studentNumber=student_no, name=name, surname=surname,
                                studentEmail=student_email, password=password,
                                campus_id=camp_id)
                student.save()
                messages.success(request,"Account Created!")
                return redirect("/login/register")
            else:
                messages.error(request,"password not matching")
                return redirect('/login/register')
        else:
            messages.error(request,"student not registerd on tut")
            return redirect('/login/register')

    else:
        return render(request, "login/register.html")


def admin(request):
    return render(request, "login/admin.html")

def logout_view(request):
    logout(request)
    return redirect('account:landing')
def home(request):
    return render(request, 'home/home.html')
def about(request):
    return render(request,'about_us/about_us.html')
def contact(request):
    return render(request, 'contact_us/contact_us.html')
