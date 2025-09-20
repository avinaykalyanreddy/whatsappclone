
from . import views
from django.urls import path

app_name = "users"

urlpatterns = [

    path("",views.index,name="index"),
    path("home/",views.home,name="home"),
    path("login/",views.login,name="login"),
    path("logout/",views.logout,name="logout"),
    path("signup/",views.signup,name="signup"),
    path("users/verify/<str:link>/",views.verify_signup_email,name="verify_signup_email"),

]