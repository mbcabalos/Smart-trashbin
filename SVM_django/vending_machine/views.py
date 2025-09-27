from functools import wraps
from django.shortcuts import render, get_object_or_404, redirect
from bson.objectid import ObjectId
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from .models import User, ActivityLog, Voucher

# ------------------------------
# Session-based decorators
# ------------------------------
def login_required_session(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            messages.error(request, "You must log in first.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

def admin_required_session(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.session.get('role') != 'admin':
            messages.error(request, "Access denied.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

# ------------------------------
# Helper to get current user
# ------------------------------
def get_current_user(request):
    username = request.session.get('username')
    if not username:
        return None
    try:
        return User.objects.get(username=username)
    except User.DoesNotExist:
        return None


# ------------------------------
# Registration
# ------------------------------
def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm = request.POST.get("confirmPassword")

        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("register")

        User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            role="user",
            created_at=timezone.now()
        )

        messages.success(request, "Account created successfully! Please log in.")
        return redirect("login")

    return render(request, "registration/register.html")

# ------------------------------
# Login
# ------------------------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        if not username or not password:
            messages.error(request, "Please enter both username and password.")
            return redirect("login")

        try:
            # Fetch the user from MongoDB
            user = User.objects.get(username=username)

            # Check hashed password
            if check_password(password, user.password):
                # Set session
                request.session['user_id'] = str(user.id)  # Convert ObjectId to string
                request.session['username'] = user.username
                request.session['role'] = user.role

                messages.success(request, f"Welcome {user.username}!")

                # Redirect based on role
                if user.role.lower() == "admin":
                    return redirect("admin_dashboard")
                else:
                    return redirect("dashboard")
            else:
                messages.error(request, "Invalid username or password.")

        except User.DoesNotExist:
            messages.error(request, "Invalid username or password.")

        return redirect("login")  # Always redirect after POST

    # GET request
    return render(request, "registration/login.html")


# ------------------------------
# Logout
# ------------------------------
def logout_view(request):
    request.session.flush()
    messages.success(request, "Logged out successfully.")
    return redirect("login")

# ------------------------------
# Dashboard
# ------------------------------
@login_required_session
def dashboard(request):
    user = get_current_user(request)
    vouchers = Voucher.objects.filter(redeemed_by=user).order_by('-created_at')
    transactions = ActivityLog.objects.filter(email=user.email).order_by('-timestamp')

    # Count vouchers based on ActivityLog for this user
    redeemed_vouchers_count = ActivityLog.objects.filter(email=user.email).count()
    total_duration_minutes = redeemed_vouchers_count * 5

    context = {
        'user': user,
        'vouchers': vouchers,
        'transactions': transactions,
        'redeemed_vouchers': redeemed_vouchers_count,
        'total_duration_minutes': total_duration_minutes
    }
    return render(request, "users/dashboard.html", context)



# ------------------------------
# Admin Views
# ------------------------------
@login_required_session
def admin_dashboard(request):
    vouchers = ActivityLog.objects.all().order_by('-timestamp')[:10]
    redeemed_vouchers_count = ActivityLog.objects.filter(action='redeem').count()
    total_users = User.objects.count()
    total_vouchers = ActivityLog.objects.values('voucher_code').count()

    context = {
        'vouchers': vouchers,
        'redeemed_vouchers': redeemed_vouchers_count,
        'total_users': total_users,
        'total_vouchers': total_vouchers
    }
    return render(request, "admin/admin_dashboard.html", context)


@admin_required_session
def admin_users(request):
    users = User.objects.all().order_by('-created_at')
    return render(request, 'admin/admin_users.html', {
        'users': users,
        'title': 'Users Management - Smart Wi-Fi Bin'
    })

@admin_required_session
def admin_add_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role', 'user')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
        else:
            User.objects.create(
                username=username,
                email=email,
                password=make_password(password),
                role=role
            )
            messages.success(request, f'User {username} created successfully.')

    return redirect('admin_users')

@admin_required_session
def admin_edit_user(request, user_id):
    user = User.objects.get(id=user_id)  # or User.objects(id=user_id).first() depending on your ODM
    if not user:
        messages.error(request, "User not found.")
        return redirect('admin_users')

    if request.method == 'POST':
        new_username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role', 'user')

        if User.objects(username=new_username).filter(id__ne=user_id).first():
            messages.error(request, 'Username already exists.')
        elif User.objects(email=email).filter(id__ne=user_id).first():
            messages.error(request, 'Email already exists.')
        else:
            user.username = new_username
            user.email = email
            user.role = role
            if password:
                user.password = make_password(password)  
            user.save()
            messages.success(request, f'User {new_username} updated successfully.')

    return redirect('admin_users')

@admin_required_session
def admin_delete_user(request, username):
    current_user = get_current_user(request)

    # Fetch the user by username
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('admin_users')

    # Prevent deleting yourself
    if user.username == current_user.username:
        messages.error(request, "You cannot delete your own account.")
        return redirect('admin_users')

    # Delete the user
    user.delete()
    messages.success(request, f"User {username} deleted successfully.")
    return redirect('admin_users')




@admin_required_session
def admin_vouchers(request):
    vouchers = Voucher.objects.all().order_by('-created_at')
    return render(request, 'admin/admin_vouchers.html', {
        'vouchers': vouchers,
        'title': 'Vouchers Management - Smart Wi-Fi Bin'
    })

@admin_required_session
def admin_add_voucher(request):
    if request.method == 'POST':
        import random, string

        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        duration_minutes = request.POST.get('duration_minutes')

        while Voucher.objects.filter(code=code).exists():
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

        Voucher.objects.create(code=code, duration_minutes=duration_minutes)
        messages.success(request, f'Voucher {code} created successfully.')

    return redirect('admin_vouchers')

@admin_required_session
def admin_delete_voucher(request, voucher_id):
    voucher = get_object_or_404(Voucher, id=voucher_id)
    code = voucher.code
    voucher.delete()
    messages.success(request, f'Voucher {code} deleted successfully.')
    return redirect('admin_vouchers')
