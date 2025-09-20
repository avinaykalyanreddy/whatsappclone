from django import forms
from .models import User
class SignUpForm(forms.ModelForm):

    confirm_password = forms.CharField(max_length=256,label="Confirm Password",widget= forms.PasswordInput())
    password = forms.CharField(max_length=256,label="Password",widget= forms.PasswordInput());

    class Meta:

        model = User

        fields = ["name","email","password"]



    def clean_email(self):

        email = self.cleaned_data.get("email")

        is_email_exists = User.objects.filter(email=email).first()

        if is_email_exists:

            self.add_error("password","A user with this email already exists. Please try another email")

        return email

    def clean(self):

        cleaned_data = super().clean()

        pass1 = cleaned_data.get("password")
        pass2 = cleaned_data.get("confirm_password")

        if pass1 != pass2:

            self.add_error("confirm_password","Your passwords don’t match")

        if len(pass1) < 5:

            self.add_error("password","Password length must be at least 5 characters")


        return cleaned_data


class LoginForm(forms.Form):

    email = forms.EmailField(max_length=100)
    password = forms.CharField(max_length=100,widget= forms.PasswordInput())

    def clean_email(self):
        email = self.cleaned_data.get("email",None)
        user_obj = User.objects.filter(email=email).first()

        if not user_obj :

            self.add_error("email","No account found with this email address")

        elif not user_obj.is_verified:

            self.add_error("email","Email not verified")


        return email




