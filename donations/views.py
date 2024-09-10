from .models import Donation
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from django.template.loader import render_to_string


def login_view(request):
    print(f"Request method: {request.method}")
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(f"Username: {username}, Password: {password}")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            print("Authentication successful")
            login(request, user)
            return redirect('donation_form')
        else:
            print("Authentication failed")
            return render(request, 'donations/login.html', {'error': 'Invalid credentials'})
    print("Rendering login page")
    return render(request, 'donations/login.html')


@login_required
def donation_form_view(request):
    if request.method == 'POST':
        building = request.POST.get('building')
        flat_number = request.POST.get('flat_number')
        phone_number = request.POST.get('phone_number')
        amount = request.POST.get('amount')
        mode = request.POST.get('mode')
        committee_member = request.user

        amount_paid = True if int(amount) > 0 else False 

        if Donation.objects.filter(building=building, flat_number=flat_number).exists():
            return render(request, 'donations/donation_form.html', {'error': f'Donation already received from {building} - {flat_number}.'})
        else:
            donation = Donation.objects.create(
                building=building,
                flat_number=flat_number,
                phone_number=phone_number,
                amount_paid=amount_paid,
                amount=amount,
                mode=mode,
                committee_member=committee_member
            )

            request.session['donation_id'] = donation.id

            return redirect('receipt_choice')
    return render(request, 'donations/donation_form.html')


@login_required
def receipt_choice_view(request):
    donation_id = request.session.get('donation_id')
    
    if donation_id is None:
        return HttpResponse("No donation data found.")
    try:
        donation_data = Donation.objects.get(id=donation_id)
    except Donation.DoesNotExist:
        return HttpResponse("Donation not found.")
    
    return render(request, 'donations/receipt_choice.html', {'donation': donation_data})


@login_required
def generate_receipt_view(request):
    donation_id = request.session.get('donation_id')

    if donation_id is None:
        return HttpResponse("No donation data found.")
    try:
        donation_data = Donation.objects.get(id=donation_id)
    except Donation.DoesNotExist:
        return HttpResponse("Donation not found.")
          
    return render(request, 'donations/generate_receipt.html', {'donation': donation_data})


def generate_receipt_by_token(request, receipt_token):
    try:
        donation_data = Donation.objects.get(receipt_token=receipt_token)
    except Donation.DoesNotExist:
        return HttpResponse("Donation not found.")
    return render(request, 'donations/generate_receipt_by_token.html', {'donation': donation_data})
    

@login_required
def donations_view(request):
    donations = Donation.objects.all()
    return render(request, 'donations/donations.html', {'donations': donations})  


def logout_view(request):
    logout(request)
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
