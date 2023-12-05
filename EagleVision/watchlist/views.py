from django.http import HttpRequest
from django.shortcuts import render, redirect
from profilePage.models import SystemConfig
from loginPage.models import Student
from .models import OverallWatchlist, PersonalWatchlist
import random
from searchPage.views import getSemester

# Create your views here.

def populate_db():
    semester = getSemester()
    courses = {
            "PHIL1070 01 - Philosophy of the Person I": ["0d10fa07-c981-445e-a2e6-f86ce5cdb370","01","Sellick, Charles D"], 
            "CSCI1101 03 - Computer Science I": ["d8b107f6-656b-4760-96e0-6624aab21bd8","03","Eggleston, Cierra"],
            "ENGL2170 01 - Introduction to British Literature and Culture I": ["952e91af-ffb8-471e-b135-04d6d0b02c62","01","Buckston, Belkis N"],
            "CSCI2243 02 - Logic and Computation": ["fc9393ec-9c0a-48bd-9a52-87d0b68320a4","02","Adlam, Magan H"],
            "CSCI3311 01 - Data Visualization": ["b0c268ca-f942-4d53-97d1-736805dd38f9","01","Sellick, Velva Noma"],
            "BIOL2000 01 - Molecules and Cells": ["e3306dc1-abaa-46bf-a357-bdadb3a9d31a","01","Edith, Jeffrey S"]
        }
    users = [
        "morganan",
        "condonai",
        "agmata",
        "baosi",
        "doung",
        "blank1",
        "blank2",
        "blank3"
    ]
    names = [
        "Addison Morgan", 
        "Aidan Condon",
        "Calista Agmata",
        "Siyuan Bao",
        "Alicia Doung",
        "User 1",
        "User 2",
        "User 3"
        ]
    grad_sems = ["Fall 2023", "Spring 2023", "Fall 2024", "Spring 2024", "Fall 2025", "Spring 2025"]
    semesters = ["2023F", "2024S"]
    for semester in semesters:
        for cls in courses:
            c = OverallWatchlist()
            c.class_id = courses[cls][0]
            c.activity_id = courses[cls][1]
            c.class_name = cls 
            c.class_name_filter = cls.split(' - ')[1]
            c.num_watchers = 0
            c.active_semester = semester
            c.professor = courses[cls][2]
            c.course_code = f"{cls.split(' ')[0]}{cls.split(' ')[1]}"
            c.save()
            r = random.randint(5, len(users))
            for i in range(r):
                new_watch = PersonalWatchlist()
                new_watch.class_id = courses[cls][0]
                new_watch.activity_id = courses[cls][1]
                new_watch.class_name = cls
                new_watch.user = users[i]
                new_watch.alert = f"{random.randint(1,4)}"
                new_watch.user_name = names[i]
                new_watch.course_code = cls.split(" ")[0]
                new_watch.active_semester = semester
                new_watch.grad_sem = random.choice(grad_sems)
                new_watch.save()
                c.add_watcher()
                c.save()
            c.save()
 
def watchlistOverview(request: HttpRequest):
    #print(class_id)
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

    #return render(request, "watchlistReport.html", locals())
        #if selected_option == "courseID":
            #print(selected_option)
            #return redirect("/search")
        #return render(request, 'watchlistReport.html', {'selected_option': selected_option})
            # filter based 

        

    if not watches:
        # class.activityOffering.name, looks different on API
        # will just fill up these courses for now
        # can't search for class by specific course ID, so will use regular class ID and then
        # loop through classes until the name/activity_id matches
        # once we're done with this, we can comment it out so it shows blank watchlists
        # populate_db()

        watches = OverallWatchlist.objects.filter(active_semester=semester)

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

