from django.contrib.auth.models import User
import json
import logging
import time
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
from .forms import RegistrationForm, UploadFileForm
from .models import *
from .tasks import process_csv
from django.db.models import Q
from django.core.cache import cache
from django.views.decorators.http import require_GET

# Logger setup
logger = logging.getLogger(__name__)
extra_param = {"AppName": "MetricsManagerApp"}

# Views

def pagenotfound(request, exception):
    return render(request, "404_error.html")

def register(request):
    try:
        if request.method == 'POST':
            form = RegistrationForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'You have registered successfully! Please log in.')
                logger.info("User registration successful", extra=extra_param)
                return redirect('login')
            else:
                logger.info("User registration failed", extra=extra_param)
                return render(request, 'register.html', {'form': form})
        else:
            form = RegistrationForm()
        return render(request, 'register.html', {'form': form})

    except Exception as e:
        logger.error("Exception occurred in register view: %s", str(e), extra=extra_param)
        messages.error(request, 'An unexpected error occurred. Please try again later.')
        return render(request, 'register.html', {'form': RegistrationForm()})

def user_login(request):
    try:
        if request.user.is_authenticated:
            return redirect('home')

        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful!')
                logger.info(f"User {username} logged in successfully", extra=extra_param)
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
                logger.warning(f"Failed login attempt for user {username}", extra=extra_param)

        return render(request, 'login.html')

    except Exception as e:
        logger.error("Exception occurred in user_login view: %s", str(e), extra=extra_param)
        messages.error(request, 'An unexpected error occurred. Please try again later.')
        return render(request, 'login.html')

@login_required
def user_logout(request):
    try:
        username = request.user.username
        logout(request)
        logger.info(f"User {username} logged out", extra=extra_param)
        return redirect('login')

    except Exception as e:
        logger.error("Exception occurred in user_logout view: %s", str(e), extra=extra_param)
        messages.error(request, 'An unexpected error occurred. Please try again later.')
        return redirect('home')

def home(request):
    try:
        if not request.user.is_authenticated:
            return redirect('login')

        logger.info(f"User {request.user.username} accessed home page", extra=extra_param)
        return render(request, 'home.html')
    except Exception as e:
        logger.error("Exception occurred in home view: %s", str(e), extra=extra_param)
        messages.error(request, 'An unexpected error occurred. Please try again later.')
        return redirect('login')

@login_required
def user_management(request):
    try:
        logger.info(f"User {request.user.username} accessed user management", extra=extra_param)
        return render(request, 'user_management.html')
    except Exception as e:
        logger.error("Exception occurred in user_management view: %s", str(e), extra=extra_param)
        messages.error(request, 'An unexpected error occurred. Please try again later.')
        return redirect('home')

@login_required
def upload_file_page(request):
    try:
        form = UploadFileForm()
        logger.info(f"User {request.user.username} accessed the upload page", extra=extra_param)
        return render(request, 'upload.html', {'form': form})
    except Exception as e:
        logger.error("Exception occurred in upload_file_page view: %s", str(e), extra=extra_param)
        return redirect('home')

@login_required
def query_builder_page(request):
    try:
        return render(request, 'query_builder.html')
    except Exception as e:
        logger.error("Exception occurred in upload_file_page view: %s", str(e), extra=extra_param)
        return redirect('home')

# REST APIs

@csrf_exempt
def fetch_users(request):
    try:
        if request.method == 'GET':
            if not request.user.is_authenticated:
                logger.warning("Unauthenticated access attempt to fetch users", extra=extra_param)
                return JsonResponse({'error': 'User not authenticated'}, status=401)

            users = User.objects.exclude(id=request.user.id).filter(is_staff=False).values('id', 'username', 'email')
            logger.info(f"Fetched {users.count()} users", extra=extra_param)
            return JsonResponse(list(users), safe=False)
        
        logger.error("Invalid request method for fetch_users", extra=extra_param)
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    except Exception as e:
        logger.error("Exception occurred in fetch_users view: %s", str(e), extra=extra_param)
        return JsonResponse({'error': 'An unexpected error occurred. Please try again later.'}, status=500)

@csrf_exempt
def create_user(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password1 = data.get('password1')
            password2 = data.get('password2')

            if password1 != password2:
                logger.warning(f"Password mismatch for username {username}", extra=extra_param)
                return JsonResponse({'error': 'Passwords must match.'}, status=400)
            
            if User.objects.filter(username=username).exists():
                logger.warning(f"Username {username} already exists", extra=extra_param)
                return JsonResponse({'error': 'A user with that username already exists.'}, status=400)

            user = User.objects.create(username=username, email=email, password=make_password(password1))
            logger.info(f"User {username} created successfully", extra=extra_param)
            return JsonResponse({'id': user.id, 'username': user.username, 'email': user.email})

    except json.JSONDecodeError:
        logger.error("JSON decoding error in create_user", extra=extra_param)
        return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
    except Exception as e:
        logger.error("Exception occurred in create_user view: %s", str(e), extra=extra_param)
        return JsonResponse({'error': 'An unexpected error occurred. Please try again later.'}, status=500)
    
    logger.error("Invalid request method for create_user", extra=extra_param)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def delete_user(request, user_id):
    try:
        if request.method == 'DELETE':
            user = get_object_or_404(User, id=user_id)
            user.delete()
            logger.info(f"User with ID {user_id} deleted successfully", extra=extra_param)
            return JsonResponse({'message': 'User deleted successfully!'})
        
        logger.error("Invalid request method for delete_user", extra=extra_param)
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    except Exception as e:
        logger.error("Exception occurred in delete_user view: %s", str(e), extra=extra_param)
        return JsonResponse({'error': 'An unexpected error occurred. Please try again later.'}, status=500)

@login_required
def handle_file_upload(request):
    try:
        if request.method == 'POST':
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                uploaded_file = form.save()

                # Check file size (1GB limit)
                max_size = 1 * 1024 * 1024 * 1024  # 1GB in bytes
                if uploaded_file.file.size > max_size:
                    logger.error("Uploaded file exceeds 1GB limit", extra=extra_param)
                    return JsonResponse({'error': 'File size exceeds 1GB limit.'}, status=400)

                # Check if the file is a CSV
                if not uploaded_file.file.name.lower().endswith('.csv'):
                    logger.error("Uploaded file is not a CSV", extra={'request': request})
                    return JsonResponse({'error': 'Uploaded file is not a CSV.'}, status=400)

                process_csv.delay(uploaded_file.file.path)
                logger.info(f"User {request.user.username} uploaded file successfully", extra=extra_param)
                return JsonResponse({'status': 'success'})
            else:
                logger.error("Form validation failed for file upload", extra=extra_param)
                return JsonResponse({'error': form.errors}, status=400)  # Return specific form errors
        else:
            return JsonResponse({'error': 'Invalid request method'}, status=405)
    except Exception as e:
        logger.error("Exception occurred in handle_file_upload view: %s", str(e), extra=extra_param)
        return JsonResponse({'error': 'An unexpected error occurred. Please try again later.'}, status=500)

@require_GET
def query_builder_data(request):
    try:
        start_time = time.time()

        # Fetch distinct values from related models
        industries = Industry.objects.values_list('name', flat=True).distinct()
        years = Company.objects.values_list('year_founded', flat=True).distinct()
        cities = City.objects.values_list('name', flat=True).distinct()
        states = State.objects.values_list('name', flat=True).distinct()
        countries = Country.objects.values_list('name', flat=True).distinct()

        #countries = [countries.title() for city in cities if city]
        #industries = [industries.title() for city in cities if city]

        response_data = {
            'industries': sorted(industries),
            'years': sorted(years),
            'cities': sorted(cities),
            'states': sorted(states),
            'countries': sorted(countries),  # Fixed to 'countries' to match key in the response
        }
        
        end_time = time.time()
        execution_time = end_time - start_time

        logger.info("Dropdown data retrieved successfully", extra=extra_param)
        logger.info(f"Execution time: {execution_time} seconds", extra=extra_param)

        return JsonResponse(response_data)
    
    except Exception as e:
        logger.error("Exception occurred while retrieving dropdown data: %s", str(e), extra=extra_param)
        return JsonResponse({'error': 'An unexpected error occurred. Please try again later.'}, status=500)

@login_required
def query(request):
    try:
        if request.method == 'GET':
            # Retrieve query parameters
            keyword = request.GET.get('keyword', '')
            industry = request.GET.get('industry', '')
            year = request.GET.get('year', '')
            city = request.GET.get('city', '')
            state = request.GET.get('state', '')
            country = request.GET.get('country', '')
            employee_from = request.GET.get('employee_from', None)
            employee_to = request.GET.get('employee_to', None)

            # Build the query
            query_filters = Q()
            if keyword:
                query_filters &= Q(name__icontains=keyword)
            if industry:
                query_filters &= Q(industry__name__icontains=industry)
            if year:
                query_filters &= Q(year_founded=year)
            if city:
                query_filters &= Q(city__name__icontains=city)
            if state:
                query_filters &= Q(city__state__name__icontains=state)
            if country:
                query_filters &= Q(city__state__country__name__icontains=country)
            if employee_from:
                query_filters &= Q(total_employee_estimate__gte=int(employee_from))
            if employee_to:
                query_filters &= Q(total_employee_estimate__lte=int(employee_to))

            companies = Company.objects.filter(query_filters)
            count = companies.count()

            logger.info("Query executed successfully, record count: %d", count, extra=extra_param)
            return JsonResponse({'count': count})
        
        logger.error("Invalid request method for query_builder: %s", request.method, extra=extra_param)
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    except Exception as e:
        logger.error("Exception occurred while querying data: %s", str(e), extra=extra_param)
        return JsonResponse({'error': 'An unexpected error occurred. Please try again later.'}, status=500)

@require_GET
def get_states(request):
    country_name = request.GET.get('country')
    if not country_name:
        return JsonResponse({'states': []})

    states = State.objects.filter(country__name=country_name).values_list('name', flat=True).distinct()
    states = [state.title() for state in states if state]
    
    return JsonResponse({'states': sorted(states)})

@require_GET
def get_cities(request):
    state_name = request.GET.get('state')
    country_name = request.GET.get('country')

    if not (state_name or country_name):
        return JsonResponse({'cities': []})

    # Filter cities based on state and optional country
    if state_name:
        query = City.objects.filter(state__name=state_name.lower())

    if country_name:
        query = City.objects.filter(state__country__name=country_name)

    cities = query.values_list('name', flat=True).distinct()
    cities = [city.title() for city in cities if city]

    return JsonResponse({'cities': sorted(cities)})
