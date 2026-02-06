from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login,logout
from .models import *
from django.contrib import messages

# Create your views here.
def home(request):
    products = Product.objects.all()

    return render(request,"home.html",{"products":products})

def about(request):
    profile = StoreProfile.objects.get(id=1)
    return render(request, "about.html", {"profile": profile})


def customer_signup(request):
    if request.method=="POST":
        username=request.POST["username"]
        email=request.POST["email"]
        password=request.POST["password"]

        if User.objects.filter(username=username).exists():
            messages.error(request,"username already exists")
            return redirect("signup")
        user=User.objects.create_user(username=username,email=email,password=password)
        Role.objects.create(user=user,role=Role.CUSTOMER,active=True)
        messages.success(request,"Account created")
        return redirect("login")
    return render(request,"registration/signup.html")

def login_view(request):
    if request.method=="POST":
        username=request.POST["username"]
        password=request.POST["password"]
    
        user=authenticate(request,username=username,password=password)
        if not user:
            messages.error(request,"invalid credentials")
            return redirect("login")
        login(request,user)

        # if user.is_superuser:
        #     return redirect("/admin/")

        # ADMIN
        if user.roles.filter(role=Role.ADMIN, active=True).exists():
            return redirect("dashboardpage")

        # SELLER
        # if user.roles.filter(role=Role.SELLER, active=True).exists():
        #     return redirect("seller_dashboard")

        # CUSTOMER
        return redirect("customerpage")

    return render(request,"registration/login.html")

def logout_view(request):
    logout(request)
    return redirect("login")