from authlib.integrations.django_client import OAuth #type: ignore
from django.conf import settings
from django.shortcuts import redirect, render, redirect
from django.urls import reverse
from urllib.parse import quote_plus, urlencode
from django.http import HttpRequest
from .forms import RegistrationFormStudent
from .models import Student

oauth = OAuth()

oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)

def login(request: HttpRequest):
    # Sends to login page
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("callback"))
    )

def callback(request):
    # Used to validate user
    token = oauth.auth0.authorize_access_token(request)
    request.session["user"] = token
    return redirect(request.build_absolute_uri(reverse("index")))

def logout(request):
    # Logout url, clears session and sends back to login page
    request.session.clear()

    return redirect(
        f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
        + urlencode(
            {
                "returnTo": request.build_absolute_uri(reverse("index")),
                "client_id": settings.AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        ),
    )

def index(request):
    # See if user is valid, send to invalid page if not @bc.edu, send to login if not valid
    session = request.session.get("user")
    if session:
        bc_user = session["userinfo"]["email"].endswith("@bc.edu")
        if bc_user:
            return redirect("/search")
        else:
            return render(request, "invalid.html", {"user": session["userinfo"],
            "bc_user": bc_user})

    return redirect("/login")

def signUp(request: HttpRequest):
    # See if user is valid (assumes not in database)
    session = request.session.get("user")
    if session:
        if session["userinfo"]["email"].endswith("@bc.edu"):
            if request.method == "POST":
                # When page is submitted, gets info and creates a Student model
                # with their information
                form = RegistrationFormStudent(request.POST)
                if form.is_valid():
                    majors = form.cleaned_data["majors"]
                    minors = form.cleaned_data["minors"]
                    second_major = form.cleaned_data["majors_2"]
                    second_minor = form.cleaned_data["minors_2"]
                    grad_year = form.cleaned_data["grad_year"]
                    grad_sem = form.cleaned_data["grad_sem"]
                    eagle_id = form.cleaned_data["eagle_id"]
                    if second_major:
                        majors += f", {second_major}"
                    if second_minor:
                        minors += f", {second_minor}"
                    user = Student(
                        username=session["userinfo"]["nickname"], eagle_id=eagle_id,
                        majors=majors, minors=minors, grad_year=grad_year, grad_sem=grad_sem
                        )
                    
                    # Save model, go to landing page
                    user.save()
                    return redirect("/search")
            else:
                form = RegistrationFormStudent()
            
            return render(request, "newProfileStudent.html", {"form": form, "user": session["userinfo"]})

        else:
            return redirect("/login")
