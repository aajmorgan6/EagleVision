from django.shortcuts import render, redirect
from django.http import HttpRequest, JsonResponse
from .models import SystemConfig
from loginPage.models import Student
from watchlist.models import PersonalWatchlist, OverallWatchlist
from searchPage.views import cleanClasses, cleanWatchlist, checkClasses, drop_class, add_class
from loginPage.forms import RegistrationFormStudent
from .forms import EditProfileAdmin, EditFormStudent
from watchlist.views import populate_db
import requests
from searchPage.views import getSemester
from django.conf import settings

# Create your views here.


def profile(request: HttpRequest):
    # Check if OAuth validated user        
    session = request.session.get("user")
    if not session:
        return redirect("/login")

    # User information
    name = session["userinfo"].get("name")
    email = session["userinfo"].get("email")
    bc_user = email.endswith("@bc.edu")
    if not bc_user:
        return redirect("/login")

    semester = getSemester()

    # See if system object exists, create if not
    system_obj = SystemConfig.objects.filter(semester_code=semester).first()
    if not system_obj:
        sem = "Spring" if semester[-1] == 'S' else "Fall"
        semester_str = f'Add/Drop Period of {sem} {semester[:4]}'
        system_obj = SystemConfig(
            system_open=False, # Start up on a closed system
            semester_code=semester,
            semester_name=semester_str
        )
        system_obj.save()

    open_course = request.session.get("open_course")
    request.session["open_course"] = ""

    config = system_obj.system_open
    # See if student in database, send to sign up page if not
    nickname = session["userinfo"]["nickname"]
    try:
        user = Student.objects.get(username=session["userinfo"]["nickname"])
    except:
        return redirect("/signUp")

    # Render correct page
    watchlist = PersonalWatchlist.objects.filter(user=nickname, active_semester=semester) # all watchlists
    if not watchlist:
        populate_db()
        watchlist = PersonalWatchlist.objects.filter(user=nickname, active_semester=semester)

    classes = []
    watches = cleanWatchlist(watchlist)
    for c in watches:
        r = requests.get(f"{settings.API_ENDPOINT}/waitlist/waitlistcourseofferings?termId=kuali.atp.FA2023-2024&code=" + watches[c]["course_code"])
        if r.status_code == 200:
            classes.append(r.json()[0])
    classes = cleanClasses(classes)
    
    classes = checkClasses(classes, watches)
    if user.is_student is False:
        return render(request, "adminProfilePage.html", locals())

    return render(request, "studentProfilePage.html", locals())
    

def editStudentProfile(request: HttpRequest):
    session = request.session.get("user")
    student = Student.objects.get(username=session["userinfo"].get("nickname"))
    if request.method == "POST":

        form = EditFormStudent(request.POST)

        if form.is_valid():
            print('oh yea')
            majors = form.cleaned_data["majors"]
            minors = form.cleaned_data["minors"]
            second_major = form.cleaned_data["majors_2"]
            second_minor = form.cleaned_data["minors_2"]
            if second_major:
                majors += f", {second_major}"
            if second_minor:
                minors += f", {second_minor}"

            student.majors = majors
            student.minors = minors
            student.grad_year = form.cleaned_data["grad_year"]
            student.grad_sem = form.cleaned_data["grad_sem"]
            student.save()

        return redirect("/profile/")

    else:
        form = EditFormStudent()
        second_major = ""
        second_minor = ""
        majors = student.majors
        minors = student.minors
        if "," in student.majors:
            majors = student.majors.split(",")[0]
            second_major = student.majors.split(" ")[1]
        if "," in student.minors:
            minors = student.minors.split(",")[0]
            second_minor = student.minors.split(" ")[1]
        form.fields["majors"].initial = majors
        form.fields["majors_2"].initial = second_major
        form.fields["minors"].initial = minors
        form.fields["minors_2"].initial = second_minor
        form.fields["grad_year"].initial = student.grad_year
        form.fields["grad_sem"].initial = student.grad_sem

    return render(request, "editStudentProfile.html", {"form": form, "user": session["userinfo"]})

def editAdminProfile(request: HttpRequest):
    session = request.session.get("user")
    admin = Student.objects.get(username=session["userinfo"].get("nickname"))
    if admin.is_student:
        return redirect("/profile/")
    if request.method == "POST":

        form = EditProfileAdmin(request.POST)

        if form.is_valid():
            
            admin.majors = form.cleaned_data["department"]
            admin.save()

        return redirect("/profile/")

    else:
        form = EditProfileAdmin()
        form.fields["department"].initial = admin.majors
    return render(request, "editAdminProfile.html", {"form": form, "user": session["userinfo"]}) 

def current_change(request):
    res = {
        'code': 200,
        'msg': 'success',
        'data': {}
    }

    semester = getSemester()

    system_obj = SystemConfig.objects.filter(semester_code=semester).first()
    if not system_obj:
        sem = "Spring" if semester[-1] == 'S' else "Fall"
        semester_str = f'Add/Drop Period of {sem} {semester[:4]}'
        system_obj = SystemConfig(
            system_open=False, # Start up on a closed system
            semester_code=semester,
            semester_name=semester_str
        )
        system_obj.save()
    else:
        system_obj.system_open = not system_obj.system_open
        system_obj.save()
    return redirect('/profile')


def get_config(request):
        res = {
            'code': 200,
            'msg': 'open',
            'data': {}
        }
        system_obj = SystemConfig.objects.filter(id=1).first()
        if system_obj:
             res['msg'] = 'open' if system_obj.system_open == True else 'close'
        return JsonResponse(res)
    
def removeClass(request, class_id):
    if request.method == 'POST':
        session = request.session.get("user")
        nickname = session["userinfo"]["nickname"]
        activity_ids = []
        semester = getSemester()
        watchlists = PersonalWatchlist.objects.filter(user=nickname, class_id=class_id, active_semester=semester)
        for watch in watchlists:
            activity_ids.append(watch.activity_id)
            watch.delete()
        objects = OverallWatchlist.objects.filter(class_id=class_id, active_semester=semester)
        for object in objects:
            if object.activity_id in activity_ids:
                object.remove_watcher()
                object.save()

    return redirect('/profile/')

def changeAlert(request): 
    
    if request.method == 'POST':
        data = request.POST
        session = request.session.get("user")
        submit_type = data.get("submit_type")
        
        class_id = data.get('class_id')
        activity_id = data.get("activity_id")
        
        if submit_type == "drop":
            drop_class(class_id, activity_id, session["userinfo"].get("nickname"))

        else:
            add_class(class_id, activity_id, session["userinfo"].get("nickname"), data, session["userinfo"].get("name"))

        # TODO: run another periodic task with celery to make sure 
        # num_watchers = len(PersonalWatchlist.objects.filter(class_id=class_id, activity_id=activity_id))
        # since multiple users might be accessing it at the same time

        
        # save id for last open class (from submit) so we can keep it open
        request.session["open_course"] = class_id

    return redirect("/profile/")



