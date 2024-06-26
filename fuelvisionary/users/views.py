from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from profile.models import client
from quotes.models import FuelQuote
from django.contrib.auth import authenticate, login, logout
import re, hashlib
import datetime

def is_valid_email(email):
    # Regular expression pattern for matching email addresses
    email_pattern = r'^[\w\.-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9.-]+$'
    
    # Compile the pattern
    pattern = re.compile(email_pattern)
    
    # Use the compiled pattern to match the email address
    if pattern.match(email):
        return True
    else:
        return False

# Hash the password using the SHA-256 algorithm
def hash_password(password):
    # Hash the password using the SHA-256 algorithm
    return hashlib.sha256(password.encode()).hexdigest()    



def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = hash_password(request.POST.get('password'))

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            try:
                client_instance = client.objects.get(client=user)
                return redirect('home')
            except:
                return redirect('management')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'login.html')


def registerPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = hash_password(request.POST.get('password'))

        #Validate form data
        if not is_valid_email(username):
           messages.error(request, "Invalid email address.")
           return redirect('register')

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return redirect('register')

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        # Create the user

        user = User.objects.create_user(username=username, password=password)
        user.save()
        
        messages.success(request, "Account created successfully!")
        return redirect('login')

    return render(request, 'register.html')


@login_required
def homePage(request):
    user = request.user
    if user.is_authenticated:
        try:
            client_instance = client.objects.get(client=user)
            quote_instance = FuelQuote.objects.filter(client=client_instance)
            two_weeks = datetime.timedelta(weeks=2)
            quote_instance = quote_instance.filter(date__range=(datetime.date.today(), datetime.date.today()+two_weeks))
        except client.DoesNotExist or FuelQuote.DoesNotExist:
            return render(request, 'home.html')
    else:
        # Handle the case where the user is not authenticated
        return HttpResponse('User is not authenticated', status=401)

    context = {
        'client_instance': client_instance,
        'quote_instance': quote_instance
    }
    return render(request, 'home.html',context)


