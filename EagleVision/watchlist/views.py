from django.http import HttpRequest
from django.shortcuts import render, redirect
from profilePage.models import SystemConfig
from loginPage.models import Student
from .models import OverallWatchlist, PersonalWatchlist
from searchPage.views import getSemester

# Create your views here.
 
def watchlistOverview(request: HttpRequest):
    # See if user is validated by OAuth
    session = request.session.get("user")
    if not session:
        return redirect("/login")
    
    # User information
    name = session["userinfo"].get("name")
    email = session["userinfo"].get("email")
    bc_user = email.endswith("@bc.edu")
    if not bc_user:
        return redirect("/login")

    # See if user is in database, create one if not
    try:
        user = Student.objects.get(username=session["userinfo"]["nickname"])
    except:
        return redirect("/signUp")

    # If not admin, not allowed on this page
    if user.is_student:
        return redirect("/search")

    semester = getSemester()

    # Get system object for state of system
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
    config = system_obj.system_open

    if request.method == 'POST':
        selected_option = request.POST.get('watchlistOptions')
        selected_semester = request.POST.get('semesterOptions')
        request.session["watchlistFilters"] = selected_option
        request.session["semesterFilter"] = selected_semester

    if request.session.get("semesterFilter"):
        semester = request.session["semesterFilter"]
        
    watches = OverallWatchlist.objects.filter(active_semester=semester)

    session_filters = request.session.get("watchlistFilters")
    if session_filters:
        if session_filters == "courseID":
            watches = watches.order_by("course_code").values()
        elif session_filters == "courseName":
            watches = watches.order_by("class_name_filter").values()
        elif session_filters == "numWatches":
            watches = watches.order_by("-num_watchers").values()
        elif session_filters == "professor":
            watches = watches.order_by("professor").values()
        elif session_filters == "professor_r":
            watches = watches.order_by("-professor").values()     


    return render(request, "watchlistReport.html", locals())


def watchlistStudents(request, class_id=""):
    session = request.session.get("user")
    if not session:
        return redirect("/login")
    name = session["userinfo"].get("name")
    email = session["userinfo"].get("email")
    bc_user = email.endswith("@bc.edu")
    if not bc_user:
        return redirect("/login")

    try:
        user = Student.objects.get(username=session["userinfo"]["nickname"])
    except:
        return redirect("/signUp")
    if user.is_student:
        return redirect("/search")

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
    config = system_obj.system_open
    watchlists = PersonalWatchlist.objects.filter(class_id=class_id[:-2], active_semester=semester).filter(activity_id=class_id[-2:])
    professor = OverallWatchlist.objects.get(class_id=class_id[:-2], active_semester=semester, activity_id=class_id[-2:]).professor
    return render(request, "studentListReport.html", locals())

