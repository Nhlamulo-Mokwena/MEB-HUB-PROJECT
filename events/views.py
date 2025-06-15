
from django.shortcuts import render, redirect
from django.urls import reverse
from login.models import Admin
from datetime import datetime, date
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import connection, IntegrityError
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from .models import Event, RSVP
import csv
from administration.views import addAction
from login.models import Student
from django.utils import timezone
from django.db import models


# Create your views here.
def add_event(request):
    admin_id = request.session.get('admin_id')
    admin = Admin.objects.get(admin_id=admin_id)
    initials = request.session.get("initials")

    # 'select_related' obtains all data at one time through a multi-table join Association
    # We have two tables that are related through foreign key 'campus_id', so basically what
    # is that the data related to the Admin in the campus table is stored as an attribute in the
    # Admin table with the attribute name "campus_id", so to access the information of the campus
    # the Admin is related to you have to access it through the foreign key linking the two tables.
    # We make use of select_related to retrieve the information of a specific Admin object which has
    # campus_id foreign key which points to the Campus model.

    # instead of using Django form for the input values of adding events, I manually created the form.  Reason is django form does not serve binary files
    if request.method == 'POST':
        description = request.POST.get('description')
        date = request.POST.get('date')
        location = request.POST.get('location')
        admin_id = request.POST.get('admin_id')
        image_file =request.FILES.get('image')
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']
        capacity=request.POST['capacity']
        title=request.POST['title']

        s_time = datetime.strptime(start_time, '%H:%M')
        e_time = datetime.strptime(end_time, '%H:%M')
        image_data=image_file.read() #read binary file so it can be stored in the database

        if image_file:
            event = Event(
                description=description,
                date=date,
                location=location,
                admin_id_id=admin_id,
                image=image_data,
                start_time=s_time.time(),
                end_time=e_time.time(),
                attendance_count=0,
                capacity=capacity,
                title=title
            )
            event.save()

            addAction(admin_id=admin, record_type="Added a new event", icon="bi bi-calendar")

        messages.success(request, "Event Added successfully")
        return redirect(reverse("admin_home"))

    return render(request, 'admin/events/add_event.html', { 'admin': admin,'initials':initials})





def update_event_page(request):
    #this is the page which admin uses to update events.
    initials = request.session.get("initials")

    if request.method=='POST':
        try:
            admin_id=request.session.get("admin_id")
            admin=Admin.objects.get(admin_id=admin_id)
            dateStr= request.POST.get("date")
            date_obj=datetime.strptime(dateStr,"%B %d, %Y").date()

            location = request.POST.get("location")
            description=request.POST.get("description")

            start_time = request.POST['start_time']
            end_time = request.POST['end_time']

            capacity = request.POST['capacity']

            title= request.POST['title']

            eventID = request.GET.get('eventID')
            eventImage=request.FILES.get('eventImage')
            #retrieve the data in the fields and create an event object
            event = get_object_or_404(Event, event_id=eventID)

            # set the event attributes to the new values and save the updated version in the database
            if eventImage:
                event.image = eventImage.read()  #test if image is updated or not

            if start_time:
                s_time = datetime.strptime(start_time, '%H:%M')
                event.start_time = s_time.time()

            if end_time:
                e_time = datetime.strptime(end_time, '%H:%M')
                event.end_time = e_time.time()


            event.date=date_obj
            event.location=location
            event.description=description
            event.capacity=capacity
            event.title=title

            event.save()
            addAction(admin_id=admin, record_type="Updated an event", icon="bi bi-calendar")

            messages.success(request, "Event Updated")

            return redirect(reverse("admin_home"))
        except ValueError:
            messages.error(request, "Date format must be: Month DD, YYYY (e.g., April 25, 2025)")
            return redirect(request.path + f"?eventID={request.GET.get('eventID')}")

    #retrieve eventID from the url (GET method) and create event object which you will pass to the template to
    #display relevant information to update.
    eventID = request.GET.get('eventID')
    event = Event.objects.get(event_id=eventID)
    if not event:
                messages.error(request, "Event not found!")
                return redirect("/update_events")

    return render(request, 'admin/events/update_event_page.html',{'event':event,'initials':initials})

def delete_event(request):
    admin_id = request.session.get("admin_id")
    admin = Admin.objects.get(admin_id=admin_id)
    event_id=request.GET.get("eventID")
    if request.method == 'POST':
        event = get_object_or_404(Event, event_id=event_id)
        models.Model.delete(Event.objects.get(event_id=event_id))
        messages.success(request, "Event Deleted")
        addAction(admin_id=admin, record_type="Deleted an event", icon="bi bi-x-circle")

    return redirect(reverse("admin_home"))



def update_events(request):
    #recieves the adminID from the URL which is passed from the admin.html page and you retrieve the events posted
    #by that specfic admin, pass the list of events to the template to display so admin can choose which event to update,
    #once event is select, redirect to update_event_page to allow admin to update the event details
    admin_id = request.session.get('admin_id')
    admin = Admin.objects.get(admin_id=admin_id)
    initials = request.session.get("initials")

    events=Event.objects.all()

    if request.method=='POST':
        event_id=request.POST.get("event_id")
        event=Event.objects.all().get(event_id=event_id)
        return redirect(f"{reverse('update_event_page')}?eventID={event.event_id}")
    return render(request, 'admin/events/update_events.html', {'admin': admin,'events':events,'initials':initials})




def events_home(request):
    expired_events = Event.objects.filter(date__lt=date.today()) #automatically delete events
    for event in expired_events:
        event.delete()


    stud_id=request.session.get('stud_id')
    events = Event.objects.all()

    rsvp_event_ids = list(RSVP.objects.filter(guest_studentnumber=stud_id).values_list('event_id', flat=True))
    rsvp_event_ids = [int(eid) for eid in rsvp_event_ids]

    initials=request.session.get("initials")

    events=events.order_by('date')

    context = {
        'events': events,
        'rsvp_event_ids': rsvp_event_ids,
        'initials' : initials
    }


    return render(request, 'events/events_home.html',context)

def event_details(request):
    admin_id = request.session.get('admin_id')
    admin = Admin.objects.get(admin_id=admin_id)
    events = Event.objects.all()
    initials = request.session.get("initials")
    return render(request, 'admin/events/event_details.html',{'admin': admin,'events':events,'initials':initials})


def download_event_report(request,event_id,format):
    if format == 'pdf':
        return generate_event_pdf(request, event_id)
    elif format == 'csv':
        return generate_event_csv(request, event_id)
    else:
        return HttpResponse("Invalid format", status=400)

def generate_event_csv(request, event_id):
    #specify format for csv file
    event = get_object_or_404(Event, event_id=event_id)
    rsvps = RSVP.objects.filter(event_id=event_id)

    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="event_{event.title}_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Event Title', event.title])
    writer.writerow(['Date', event.date])
    writer.writerow(['Attendance Count', event.attendance_count])
    writer.writerow([])
    writer.writerow(['Guest Name', 'Guest Surname','Student Number'])

    for rsvp in rsvps:
        writer.writerow([rsvp.guest_name,rsvp.guest_surname, rsvp.guest_studentnumber])

    return response


def generate_event_pdf(request, event_id):
        # specify format for pdf file
        event = get_object_or_404(Event, event_id=event_id)
        rsvps=RSVP.objects.filter(event_id=event_id)
        attendance_count=event.attendance_count

        # Create PDF response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="event_{event.title}_report.pdf"'

        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4
        y = height - 50

        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, y, f"Event Report: {event.title}")
        y -= 30

        p.setFont("Helvetica", 12)
        p.drawString(50, y, f"Date: {event.date}")
        y -= 20
        p.drawString(50, y, f"Attendance Count: {attendance_count}")
        y -= 30

        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, "Name")
        p.drawString(200, y, "Surname")
        p.drawString(350, y, "Student Number")
        y -= 20
        p.line(50, y + 10, 550, y + 10)

        p.setFont("Helvetica", 10)
        for rsvp in rsvps:
            if y < 100:
                p.showPage()
                y = height - 50
            p.drawString(50, y, rsvp.guest_name)
            p.drawString(200, y, rsvp.guest_surname)
            p.drawString(350, y, rsvp.guest_studentnumber)
            y -= 18

        p.showPage()
        p.save()
        return response




def is_valid_email(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False

def rsvp_event(request):
    eventID=request.GET.get("eventID")
    event=Event.objects.get(event_id=eventID)
    studNum=request.session.get("stud_id")
    student=Student.objects.get(studentNumber=studNum)
    time = event.start_time.strftime('%H:%M')+"-"+event.end_time.strftime('%H:%M')
    initials=request.session.get('initials')


    if request.method=='POST':
        event_id = request.POST.get("eventID")
        event = Event.objects.all().get(event_id=event_id)
        guest_student_no = request.POST['studentNo']
        guest_name = request.POST['name']
        guest_surname = request.POST['surname']
        email = request.POST['email']
        done_at=timezone.now()


        if is_valid_email(email): #check if the email is valid
            try:
                with connection.cursor() as cursor:
                    #call the procedure so it can add values into the rsvp table
                    cursor.execute(""" 
                            CALL public.add_rsvp(%s, %s, %s,%s,%s) 
                        """, [event_id, guest_name, guest_student_no,guest_surname,done_at])
                messages.success(request, "RSVP Successful, check your email or email spam")
                return redirect(f"{reverse('events_home')}")
            except IntegrityError:
                messages.error(request, "Database Error! Could not save RSVP.")
            return redirect(f"{reverse('events_home')}")
        else:
            messages.success(request, "Invalid email!! Try again")
            return redirect(f"{reverse('rsvp_event')}?eventID={event.event_id}")

    return render(request,'events/rsvp_event.html',{'event':event,'time':time,'student':student,'initials':initials})

def serve_image(request,id): #serve the image from the database as image, converting it from binary to image
    event = Event.objects.get(event_id=id)
    return HttpResponse(event.image, content_type="image/jpeg")  # Or png
