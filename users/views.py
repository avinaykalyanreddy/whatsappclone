from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.template.loader import render_to_string

from .forms import SignUpForm, LoginForm
from django.contrib.auth.hashers import  make_password,check_password
from django.core.mail import  EmailMessage
from uuid import    uuid4
from django.contrib import messages
from .models import User

from random import choice

avatars = ["https://cdn2.iconfinder.com/data/icons/christmas-holiday-10/512/teddy_bear_teddy_bear_christmas.png","https://cdn2.iconfinder.com/data/icons/christmas-holiday-10/256/elf_avatar_christmas.png","https://cdn2.iconfinder.com/data/icons/christmas-holiday-10/512/reindeer_avatar_christmas.png",
     "https://cdn2.iconfinder.com/data/icons/christmas-holiday-10/256/santa_beard.png","https://cdn2.iconfinder.com/data/icons/christmas-holiday-10/256/reindeer_avatar_plasticine_effect_structure_2.png","https://cdn2.iconfinder.com/data/icons/christmas-holiday-10/256/reindeer_avatar_plasticine_effect_structure.png",
     "https://cdn2.iconfinder.com/data/icons/christmas-holiday-10/256/reindeer_avatar.png"]

# Create your views here.
def index(request):

    user_id = request.session.get("user_id",None)

    if user_id == None:
         latest_users = User.objects.order_by("-created_at")[:10]
         print(latest_users)
         return render(request,"users/index.html",{"latest_users":latest_users})

    else:

        return redirect("users:home")

    # return render(request,"users/verification_signup.html")

def home(request):

    user_obj = User.objects.filter(id=request.session.get("user_id",None)).first()

    friends = user_obj.get_friends()



    return render(request,"users/home.html",{"friends":friends})

def login(request):

    if request.method == "POST":

        form = LoginForm(request.POST)

        if form.is_valid():


            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user_obj = User.objects.filter(email=email).first()
            if check_password(password,user_obj.password):

                request.session["user_id"] = user_obj.id # id
                request.session["user_name"] = user_obj.name # name
                messages.success(request,"Login successful")

                return redirect("users:home")


            else:

                form.add_error("password","Incorrect password")

        return render(request,"users/login.html",{"form":form})

    form = LoginForm()
    return  render(request,"users/login.html",{"form":form})

def logout(request):

    request.session.flush()
    messages.success(request,"Logout successful")

    return redirect("users:index")
def signup(request):

    if request.method == "POST":

        form = SignUpForm(request.POST)

        if form.is_valid():

            user_obj = form.save(commit=False)

            password = form.cleaned_data.get("password",None)

            if password:

                user_obj.password = make_password(password)
                user_obj.icon = choice(avatars)
                user_obj.save()

                if send_signup_email(user_obj):
                    messages.success(request,f"Verification email has been sent successfully to {user_obj.email}. Please check your inbox to verify your account.")

                else:
                    messages.error(request,"Internal Server Error")
                return redirect("users:login")


        return render(request,"users/signup.html",{"form":form})

    form = SignUpForm()

    return render(request,"users/signup.html",{"form":form})


def send_signup_email(user_obj):

  try:
    subject = "Verification mail for signup"
    link = str(uuid4())

    user_obj.token = link

    user_obj.save()



    html_message = render_to_string("users/verification_signup.html",{"link":link,"user_obj":user_obj})

    mail  = EmailMessage(subject=subject,body=html_message,from_email="godsons12072004@gmail.com",to=[user_obj.email])

    mail.content_subtype="html"
    mail.send()

    return True


  except Exception as e:

      print("Email sending failed:", e)

      return False


def verify_signup_email(request,link):

    user_obj = User.objects.filter(token=link).first()

    if user_obj and  not user_obj.is_verified:
        user_obj.is_verified = True
        user_obj.token = ""

        user_obj.save()
        messages.success(request,"Thank you! Your email is now verified. Please proceed to log in.")
        return redirect("users:login")

    return HttpResponse("Link Expired")

