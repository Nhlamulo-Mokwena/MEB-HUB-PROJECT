from django.http import JsonResponse, HttpResponse
from django.shortcuts import render,redirect
import cloudinary.uploader
from .models import CampusLocation
from login.models import Admin
from .models import CampusLocation
from django.contrib import messages
from administration.views import addAction

def campus_locations_json(request):
    data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "name": loc.name,
                    "description": loc.description,
                    "icon": loc.icon,
                    "image": loc.image_url if loc.image_url else None,
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(loc.longitude), float(loc.latitude)],
                },
            }
            for loc in CampusLocation.objects.all()
        ],
    }
    return JsonResponse(data)


def display_map(request):
    return render(request,'map/map.html')

def display_map_menu(request):
    initials = request.session.get("initials")
    return  render(request,'map/map_menu.html',{
        "initials": initials
    })

def add_location(request):
    initials = request.session.get("initials")
    locations = CampusLocation.objects.all()
    errors = {}

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        image_file = request.FILES.get('image')
        icon = request.POST.get('icon', 'building')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except (TypeError, ValueError):
            errors['invalid values'] = 'Invalid latitude or longitude'
            return render(request, 'map/add_location.html', {
            'errors': errors, 
            'initials': initials })      
        
        if name.isdigit() :
            errors['invali name'] = "Location name cannot be only digits!"
        
        if description.isdigit() :
            errors['invalid description'] = "description cannot be only digits!"
            
        for loc in locations:
            if ((loc.name.lower() == name.lower()) or (loc.latitude == latitude and loc.longitude == longitude )) :
                errors['duplicate locations'] = 'The location already exists!'

        if not errors:
            image_url = None
            if image_file:
                upload_result = cloudinary.uploader.upload(image_file)
                image_url = upload_result.get('secure_url')

            admin = Admin.objects.get(admin_id=request.session["admin_id"])

            CampusLocation.objects.create(
                name=name,
                description=description,
                image_url=image_url,
                icon=icon,
                latitude=latitude,
                longitude=longitude,
                admin_id=admin
            )
            admin = Admin.objects.all().get(admin_id=request.session['admin_id'])
            addAction(admin_id=admin,record_type="Add campus location",icon="bi bi-map")
            messages.success(request, 'Location added successfully!')
            return redirect('add_location')  # Redirect to clear the form

    return render(request, 'map/add_location.html',{
        'errors':errors,'initials':initials
    })

def remove_location(request):
    initials = request.session.get("initials")
    locations = CampusLocation.objects.all()
    
    if request.method == 'POST':
        id = request.POST['location']
        
        loc = CampusLocation.objects.all().get(id=id)
        loc.delete()
        
        admin = Admin.objects.all().get(admin_id=request.session['admin_id'])
        addAction(admin_id=admin,record_type="Removed campus location",icon="bi bi-map")
        messages.success(request, 'Location removed successfully!')
        return redirect('remove_location')  # Redirect to clear the form
        
        
    return render(request,'map/remove_location.html',{
        'locations': locations,'initials':initials
    })


def view_all(request):
    initials = request.session.get("initials")
    locations = CampusLocation.objects.all()
    
    return render(request,'map/view_all_location.html',{
        'locations': locations,'initials':initials
    })
    
def update_location(request,id):
    
    locations = CampusLocation.objects.all()
    camp_loc = CampusLocation.objects.all().get(id=id)
    errors = {}
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        image_file = request.FILES.get('image') or request.POST.get('current_image_url')
        icon = request.POST.get('icon', 'building')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        
        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except (TypeError, ValueError):
            errors['invalid values'] = 'Invalid latitude or longitude'
 
        for loc in locations:
            if  not loc.id == id :
                if ((loc.name.lower() == name.lower()) or (loc.latitude == latitude and loc.longitude == longitude )) :
                    errors['duplicate locations'] = 'The location already exists!'
                
        if name.isdigit() :
            errors['invali name'] = "Location name cannot be only digits!"
        
        if description.isdigit() :
            errors['invalid description'] = "description cannot be only digits!"
        
        # Upload image to Cloudinary
        
        if not errors:
            image_url = None
            if image_file and image_file != 'None':  # Add this check
                upload_result = cloudinary.uploader.upload(image_file)
                image_url = upload_result.get('secure_url')

            # Assuming you have a way to get admin from request.user
            admin =  Admin.objects.get(admin_id=request.session["admin_id"])  # adapt this to your auth system

            camp_loc.name = name
            camp_loc.description = description
            camp_loc.icon = icon
            camp_loc.longitude = longitude
            camp_loc.latitude = latitude
            camp_loc.admin_id = admin
            if image_url:
                camp_loc.image_url = image_url
            
            camp_loc.save()
            
            messages.success(request, 'Location Updated successfully!')
            return redirect('update_location',id=id)  # Redirect to clear the form      
    
    return render(request,"map/update_location.html",{
        "camp_loc": camp_loc,
        "errors": errors
    })