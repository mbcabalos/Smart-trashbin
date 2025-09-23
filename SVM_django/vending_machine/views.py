from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .forms import RegistrationForm
from .models import UserProfile, Bottle, Voucher

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # create profile automatically
            UserProfile.objects.create(user=user)
            login(request, user)  # auto login after registration
            return redirect("dashboard")
    else:
        form = RegistrationForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
def dashboard(request):
    # if the logged-in user is an admin, send them to admin dashboard
    if request.user.is_staff or request.user.is_superuser:
        return redirect('admin_dashboard')
    
    # otherwise, normal users get their user dashboard
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    vouchers = Voucher.objects.filter(redeemed_by=request.user).order_by('-created_at')
    transactions = []  # Replace with actual transaction query
    
    # Calculate stats
    redeemed_vouchers = vouchers.filter(is_redeemed=True).count()
    total_transactions = len(transactions)  # Replace with actual count
    
    context = {
        'profile': profile,
        'vouchers': vouchers,
        'transactions': transactions,
        'redeemed_vouchers': redeemed_vouchers,
        'total_transactions': total_transactions,
    }
    
    return render(request, "users/dashboard.html", context)

# User views
def user_home(request):
    bottles = Bottle.objects.all()
    return render(request, "users/user_home.html", {"bottles": bottles})

def bottle_detail(request, pk):  
    bottle = get_object_or_404(Bottle, id=pk)
    return render(request, "users/bottle_detail.html", {"bottle": bottle})

# Admin views
def is_admin(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    bottles = Bottle.objects.all()
    vouchers = Voucher.objects.all().order_by('-created_at')[:10]
    total_bottles = Bottle.objects.count()
    total_vouchers = Voucher.objects.count()
    total_users = User.objects.count()
    redeemed_vouchers = Voucher.objects.filter(is_redeemed=True).count()
    
    context = {
        'bottles': bottles,
        'vouchers': vouchers,
        'total_bottles': total_bottles,
        'total_vouchers': total_vouchers,
        'total_users': total_users,
        'redeemed_vouchers': redeemed_vouchers,
        'title': 'Admin Dashboard - Smart Bottle Vending Machine'
    }
    return render(request, 'admin/admin_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def admin_users(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'admin/admin_users.html', {
        'users': users,
        'title': 'Users Management - Smart Bottle Vending Machine'
    })

@login_required
@user_passes_test(is_admin)
def admin_bottles(request):
    bottles = Bottle.objects.all().order_by('-created_at')
    return render(request, 'admin/admin_bottles.html', {
        'bottles': bottles,
        'title': 'Bottles Management - Smart Bottle Vending Machine'
    })

@login_required
@user_passes_test(is_admin)
def admin_vouchers(request):
    vouchers = Voucher.objects.all().order_by('-created_at')
    return render(request, 'admin/admin_vouchers.html', {
        'vouchers': vouchers,
        'title': 'Vouchers Management - Smart Bottle Vending Machine'
    })

@login_required
@user_passes_test(is_admin)
def admin_add_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        is_staff = request.POST.get('is_staff') == 'on'
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
        else:
            user = User.objects.create(
                username=username,
                email=email,
                password=make_password(password),
                is_staff=is_staff
            )
            # Create user profile
            UserProfile.objects.create(user=user)
            messages.success(request, f'User {username} created successfully.')
        
        return redirect('admin/admin_users')
    return redirect('admin/admin_users')

@login_required
@user_passes_test(is_admin)
def admin_edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        is_staff = request.POST.get('is_staff') == 'on'
        
        # Check if username already exists (excluding current user)
        if User.objects.filter(username=username).exclude(id=user_id).exists():
            messages.error(request, 'Username already exists.')
        # Check if email already exists (excluding current user)
        elif User.objects.filter(email=email).exclude(id=user_id).exists():
            messages.error(request, 'Email already exists.')
        else:
            user.username = username
            user.email = email
            user.is_staff = is_staff
            
            if password:
                user.password = make_password(password)
            
            user.save()
            messages.success(request, f'User {username} updated successfully.')
        
        return redirect('admin/admin_users')
    return redirect('admin/admin_users')

@login_required
@user_passes_test(is_admin)
def admin_delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if user == request.user:
        messages.error(request, 'You cannot delete your own account.')
    else:
        username = user.username
        user.delete()
        messages.success(request, f'User {username} deleted successfully.')
    
    return redirect('admin/admin_users')

@login_required
@user_passes_test(is_admin)
def admin_add_bottle(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        image_url = request.POST.get('image_url')
        
        bottle = Bottle.objects.create(
            name=name,
            description=description,
            price=price,
            stock=stock,
            image_url=image_url
        )
        messages.success(request, f'Bottle {name} created successfully.')
        return redirect('admin/admin_bottles')
    return redirect('admin/admin_bottles')

@login_required
@user_passes_test(is_admin)
def admin_edit_bottle(request, bottle_id):
    bottle = get_object_or_404(Bottle, id=bottle_id)
    
    if request.method == 'POST':
        bottle.name = request.POST.get('name')
        bottle.description = request.POST.get('description')
        bottle.price = request.POST.get('price')
        bottle.stock = request.POST.get('stock')
        bottle.image_url = request.POST.get('image_url')
        bottle.save()
        
        messages.success(request, f'Bottle {bottle.name} updated successfully.')
        return redirect('admin/admin_bottles')
    return redirect('admin/admin_bottles')

@login_required
@user_passes_test(is_admin)
def admin_delete_bottle(request, bottle_id):
    bottle = get_object_or_404(Bottle, id=bottle_id)
    name = bottle.name
    bottle.delete()
    messages.success(request, f'Bottle {name} deleted successfully.')
    return redirect('admin/admin_bottles')

@login_required
@user_passes_test(is_admin)
def admin_add_voucher(request):
    if request.method == 'POST':
        import random
        import string
        
        # Generate random voucher code
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        duration_minutes = request.POST.get('duration_minutes')
        
        # Make sure code is unique
        while Voucher.objects.filter(code=code).exists():
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        voucher = Voucher.objects.create(
            code=code,
            duration_minutes=duration_minutes
        )
        messages.success(request, f'Voucher {code} created successfully.')
        return redirect('admin/admin_vouchers')
    return redirect('admin/admin_vouchers')

@login_required
@user_passes_test(is_admin)
def admin_delete_voucher(request, voucher_id):
    voucher = get_object_or_404(Voucher, id=voucher_id)
    code = voucher.code
    voucher.delete()
    messages.success(request, f'Voucher {code} deleted successfully.')
    return redirect('admin/admin_vouchers')