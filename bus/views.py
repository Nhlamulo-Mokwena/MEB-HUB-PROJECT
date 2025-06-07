from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from .models import Bus_schedule,ScheduleCode
from .models import Bus_Stats
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

from .forms import ApplicationConfirmationForm
from login.models import Student
import pytesseract
import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageOps
import io

# Create your views here.s
def home(request):
    stud = Student.objects.get(studentNumber=request.session['stud_id'])
    initials = f"{stud.name[0].upper()}{stud.surname[0].upper()}"
    schedule_list = ScheduleCode.objects.all()

    return render(request, "buses/home.html", {
        "list": schedule_list,
        "initials": initials
    })


def view_schedule(request,schedule_code):

    if request.method == 'POST':
        
        code = request.POST['code']
        list = Bus_schedule.objects.filter(schedule_code=code)
        
        #Creating a response object with the appropriate content type for PDFs
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="bus_schedule.pdf"'
        
        #Creating a pdf canvas object
        p = canvas.Canvas(response,pagesize=letter)
        width, height = letter
        
        # Creating Title for the report
        p.setFont("Helvetica-Bold", 16)
        p.drawString(200, height - 40, "Bus Schedule")
        
        # Creating the font for the table headers and content
        p.setFont("Helvetica-Bold", 12) 
        
        # Draw table header
        p.drawString(30, height - 80, "Code")
        p.drawString(120, height - 80, "Departure")
        p.drawString(210, height - 80, "Destination")
        p.drawString(300, height - 80, "Departure-Time")
        p.drawString(390, height - 80, "Arrival-Time")
        p.drawString(480, height - 80, "Duration")
        
        # Set the font for the table content
        p.setFont("Helvetica", 10)
        
        # Start position for the table rows
        y_position = height - 100
        
        for schedule in list:
            
            p.drawString(30, y_position, code)
            p.drawString(120, y_position, schedule.departure)
            p.drawString(210, y_position, schedule.destination)
            p.drawString(300, y_position, schedule.departure_time.strftime('%H:%M'))
            p.drawString(390, y_position, schedule.arrival_time.strftime('%H:%M'))
            p.drawString(480, y_position, str(schedule.duration))
            y_position -= 20  # Move to the next row

            # Add a page break if the content goes beyond the page
            if y_position < 40:
                p.showPage()  # Start a new page
                p.setFont("Helvetica-Bold", 12)
                p.drawString(30, y_position, code)
                p.drawString(120, y_position, schedule.departure)
                p.drawString(210, y_position, schedule.destination)
                p.drawString(300, y_position, schedule.departure_time.strftime('%H:%M'))
                p.drawString(390, y_position, schedule.arrival_time.strftime('%H:%M'))
                p.drawString(480, y_position, str(schedule.duration))
                p.setFont("Helvetica", 10)
                y_position = height - 60  # Reset y_position for the new page
        
        # Finalize the PDF document
        p.showPage()
        p.save()
        
        return response

    list = Bus_schedule.objects.filter(schedule_code=schedule_code)
    
    schedule = ScheduleCode(schedule_code=schedule_code)
    stats = Bus_Stats(schedule_code=schedule)
    stats.save()
    
    return render(request,"buses/view_schedule.html",{
        "list": list,
        "schedule_code": schedule_code
    })


def upload_img_and_check(request):
    if request.method == 'POST':
        form = ApplicationConfirmationForm(request.POST, request.FILES)
        if form.is_valid():
            if 'document' not in request.FILES:
                messages.error(request, "No file uploaded")
                return redirect('view_status')

            try:
                document = request.FILES['document']
                image = Image.open(io.BytesIO(document.read())).convert('RGB')

                # Convert PIL to OpenCV format
                open_cv_image = np.array(image)
                image_cv = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)

                # Preprocessing improvements
                # 1. Convert to grayscale
                gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)

                # 2. Apply Gaussian blur to reduce noise
                blurred = cv2.GaussianBlur(gray, (5, 5), 0)

                # 3. Use different thresholding approach
                # Try both adaptive and simple thresholding and pick the better result
                thresh_adaptive = cv2.adaptiveThreshold(blurred, 255,
                                                        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10)

                _, thresh_simple = cv2.threshold(blurred, 0, 255,
                                                 cv2.THRESH_BINARY + cv2.THRESH_OTSU)

                # 4. Try both thresholding methods and see which gives better results
                custom_config = r'--oem 3 --psm 6'
                text_adaptive = pytesseract.image_to_string(thresh_adaptive, config=custom_config)
                text_simple = pytesseract.image_to_string(thresh_simple, config=custom_config)

                # Choose the version with more valid words
                extracted_text = text_adaptive if (
                            len(text_adaptive.split()) > len(text_simple.split())) else text_simple

                # Alternative approach if both fail - try without thresholding
                if len(extracted_text.strip()) < 20:  # If we got very little text
                    extracted_text = pytesseract.image_to_string(gray, config=custom_config)

                print("Extracted text:", extracted_text)  # For debugging

                expected_texts = [
                    "good day student",
                    "Please note that your student bus application for the academic year 2025 was approved and you may now proceed to make your student card",
                    "transport department"
                ]

                studentNum = request.session.get('student_number')
                student = Student.objects.get(studentNumber=studentNum)

                # More flexible text matching
                extracted_lower = extracted_text.lower()
                matches = sum(1 for expected in expected_texts if expected.lower() in extracted_lower)

                if matches >= 2:  # Require at least 2 out of 3 expected phrases
                    student.uses_bus = True
                    student.save()
                    messages.success(request, "Verification successful!")
                else:
                    messages.error(request, "Verification unsuccessful! Could not find required text in the image.")

            except Exception as e:
                messages.error(request, f"Error processing image: {str(e)}")
                return redirect('view_status')

            return redirect('view_status')

    return redirect('view_status')

def view_status(request):
    studentNum = request.session.get('student_number')
    student = Student.objects.all().get(studentNumber=studentNum)
    initials = f"{student.name[0].upper()}{student.surname[0].upper()}"
    uses_bus = student.uses_bus
    context = {
        "initials": initials,
        "status": uses_bus,
        "confirmation_form": ApplicationConfirmationForm()
    }
    return render(request, "buses/view_status.html", context)