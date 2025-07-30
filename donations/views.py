from .models import Donation
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, logout
from django.contrib.auth.models import User
from datetime import datetime

from django.template.loader import render_to_string

# Import only the minimal Google Sheets functions
from googlesheets import gs_read, gs_create


def login_view(request):
    print(f"Request method: {request.method}")
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(f"Username: {username}, Password: {password}")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            print("Authentication successful")
            # Custom login without database writes
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            request.session['is_authenticated'] = True
            # Force session save
            request.session.save()
            print(f"Session saved: {request.session.get('is_authenticated')}")
            return redirect('donation_form')
        else:
            print("Authentication failed")
            return render(request, 'donations/login.html', {'error': 'Invalid credentials'})
    print("Rendering login page")
    return render(request, 'donations/login.html')


def get_current_user(request):
    """Get the current user from session without database queries"""
    if request.session.get('is_authenticated'):
        user_id = request.session.get('user_id')
        username = request.session.get('username')
        # Create a minimal user object
        user = User()
        user.id = user_id
        user.username = username
        return user
    return None


def add_committee_member_info(donation_data):
    """Add committee_member object to donation data for template compatibility"""
    try:
        committee_member_id = donation_data.get('committee_member_id')
        if committee_member_id:
            user = User.objects.get(id=committee_member_id)
            donation_data['committee_member'] = user
        else:
            donation_data['committee_member'] = None
    except User.DoesNotExist:
        donation_data['committee_member'] = None
    return donation_data


def custom_login_required(view_func):
    """Custom login decorator that doesn't use Django's database-based auth"""
    def wrapper(request, *args, **kwargs):
        print(f"Checking authentication: {request.session.get('is_authenticated')}")
        print(f"Session keys: {list(request.session.keys())}")
        if request.session.get('is_authenticated'):
            return view_func(request, *args, **kwargs)
        else:
            return redirect('login')
    return wrapper


@custom_login_required
def donation_form_view(request):
    if request.method == 'POST':
        building = request.POST.get('building')
        flat_number = request.POST.get('flat_number')
        phone_number = request.POST.get('phone_number')
        amount = request.POST.get('amount')
        mode = request.POST.get('mode')
        committee_member = get_current_user(request)

        amount_paid = True if int(amount) > 0 else False 

        # Allow only one donation per (building, flat_number) per year
        current_year = datetime.now().year
        existing_donations = gs_read('donations', {'building': building, 'flat_number': flat_number})
        year_donations = [d for d in existing_donations if str(d.get('date', '')).startswith(str(current_year))]
        if len(year_donations) >= 1:
            return render(request, 'donations/donation_form.html', {'error': f'Donation already received from {building} - {flat_number} for {current_year}.'})
        else:
            # Create donation using Google Sheets
            donation_data = {
                'building': building,
                'flat_number': int(flat_number),
                'phone_number': int(phone_number) if phone_number else 0,
                'amount_paid': amount_paid,
                'amount': int(amount),
                'mode': mode,
                'committee_member_id': committee_member.id
            }
            
            donation = gs_create('donations', donation_data)
            
            if donation:
                request.session['donation_id'] = donation['id']
                return redirect('receipt_choice')
            else:
                return render(request, 'donations/donation_form.html', {'error': 'Failed to save donation. Please try again.'})
    
    return render(request, 'donations/donation_form.html')


@custom_login_required
def receipt_choice_view(request):
    donation_id = request.session.get('donation_id')
    
    if donation_id is None:
        return HttpResponse("No donation data found.")
    
    donation_list = gs_read('donations', {'id': donation_id})
    if not donation_list:
        return HttpResponse("Donation not found.")
    donation_data = donation_list[0]
    
    # Add committee_member object for template compatibility
    donation_data = add_committee_member_info(donation_data)
    
    return render(request, 'donations/receipt_choice.html', {'donation': donation_data})


@custom_login_required
def generate_receipt_view(request):
    donation_id = request.session.get('donation_id')

    if donation_id is None:
        return HttpResponse("No donation data found.")
    
    donation_list = gs_read('donations', {'id': donation_id})
    if not donation_list:
        return HttpResponse("Donation not found.")
    donation_data = donation_list[0]
    
    # Add committee_member object for template compatibility
    donation_data = add_committee_member_info(donation_data)
          
    return render(request, 'donations/generate_receipt.html', {'donation': donation_data})


def generate_receipt_by_token(request, receipt_token):
    donation_list = gs_read('donations', {'receipt_token': receipt_token})
    if not donation_list:
        return HttpResponse("Donation not found.")
    donation_data = donation_list[0]
    
    # Add committee_member object for template compatibility
    donation_data = add_committee_member_info(donation_data)
    
    return render(request, 'donations/generate_receipt_by_token.html', {'donation': donation_data})
    

@custom_login_required
def donations_view(request):
    donations = gs_read('donations')
    
    # Add committee_member objects for template compatibility
    for donation in donations:
        add_committee_member_info(donation)
    
    return render(request, 'donations/donations.html', {'donations': donations})  


def logout_view(request):
    # Clear session data
    request.session.flush()
    return redirect('login')   


from django.views.decorators.csrf import csrf_exempt
import subprocess

@csrf_exempt
def github_webhook(request):
    if request.method == 'POST':
        result = subprocess.run(['git', 'pull', 'origin', 'main'], cwd='/home/soham/DonationProject', capture_output=True, text=True)
        if result.returncode == 0:
            return HttpResponse('Git pull successful', status=200)
        else:
            return HttpResponse(f'Git pull failed: {result.stderr}', status=500)
    else:
        return HttpResponse('Invalid request method', status=400)
