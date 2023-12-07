from django.shortcuts import render, redirect
from profilePage.models import SystemConfig
from loginPage.models import Student
from django.http import HttpRequest
import requests
from lxml import etree
from watchlist.models import PersonalWatchlist, OverallWatchlist
from typing import List
from datetime import date 
from .models import FilterCourseInfo
from loginPage.forms import RegistrationFormStudent
from django.db.models import Q
from django.conf import settings
from .tasks import check_classes
# Create your views here.

SCHOOLS = {
    "MCAS": [
        "AADS",
        "ARTH",
        "ARTS",
        "BIOL",
        "CHEM",
        "CLAS",
        "COMM",
        "CSCI",
        "EALC",
        "ECON",
        "EESC",
        "ENGL",
        "ENGR",
        "ENVS",
        "FILM",
        "FREN",
        "GERM",
        "HIST",
        "ICSP",
        "INTL",
        "ITAL",
        "JOUR",
        "LING",
        "MATH",
        "MUSA",
        "MUSP",
        "NELC",
        "PHIL",
        "PHYS",
        "POLI",
        "PSYC",
        "RLRL",
        "ROTC",
        "SLAV",
        "SOCY",
        "SPAN",
        "THEO",
        "THTR",
        "UNAS",
        "UNCP",
        "UNCS"
    ],
    "CSOM": [
        "ACCT",
        "BCOM",
        "BSLW",
        "BZAN",
        "GSOM",
        "ISYS",
        "MFIN",
        "MGMT",
        "MKTG",
        "PRTO",
        "UGMG",
    ],
    "CSON": [
        "FORS",
        "HLTH",
        "NURS",
    ],
    "LAWS": [
        "LAWS"
    ],
    "LYNCH": [
        "APSY",
        "EDUC",
        "ELHE",
        "FORM",
        "LREN",
        "MESA",
    ],
    "SCHILLER": [
        "PHCG",
        "SCHI",
    ],
    "SOCIAL": [
        "SCWK",
    ],
    "THEO": [
        "TMCE",
        "TMHC",
        "TMNT",
        "TMOT",
        "TMPS",
        "THPT",
        "TMRE",
        "TMST",
        "TMTM"
    ],
    "WOODS": [
        "ADAC",
        "ADAN",
        "ADBI",
        "ADBM",
        "ADCJ",
        "ADCO",
        "ADCY",
        "ADEC",
        "ADEN",
        "ADET",
        "ADEX",
        "ADFA",
        "ADFM",
        "ADGR",
        "ADHA",
        "ADHS",
        "ADIT",
        "ADMK",
        "ADMT",
        "ADPL",
        "ADPO",
        "ADPS",
        "ADSA",
        "ADSB",
        "ADSO",
        "ADTH"
    ]
}

def create_class_list():
    # Get all classes
    r = requests.get(f"{settings.API_ENDPOINT}/waitlist/waitlistcourseofferings?termId=kuali.atp.FA2023-2024&code=")
    if r.status_code == 200:
        courses = r.json()
        for course in courses:
            if FilterCourseInfo.objects.filter(course_id=course["courseOffering"]["id"]).first():
                continue
            model = FilterCourseInfo()
            model.course_id = course["courseOffering"]["id"]
            model.course_code = course["courseOffering"]["courseCode"]
            model.credits = course["courseOffering"]["creditOptionId"][-3:]
            code = model.course_code[:4]
            for school in SCHOOLS:
                if code in SCHOOLS[school]:
                    model.school = school
            model.save()
            activities = requests.get(f"{settings.API_ENDPOINT}/waitlist/waitlistactivityofferings?courseOfferingId=" + model.course_id)
            if activities.status_code != 200:
                continue
            activities = activities.json()
            for activity in activities:
                # Get all values first, then do logic
                type = activity["activityOffering"]["typeKey"].split(".")[-1].lower()
                events = activity["events"]
                if len(events) == 0:
                    # Asynch classes
                    model.asynch = True
                    days = ""
                else:
                    location = events[0]["locationDescription"]
                    place = activity["scheduleNames"][0][len(location) + 1:].split(" ")
                    if place[0].lower() == "by":
                        days = ""
                        time = "" # By arrangement
                    else:
                        days = place[0]
                        time = activity["scheduleNames"][0][len(location) + len(days) + 1:]
                        time = time.split("-")[0] # start time

                school = "" # Find some way to map each department to a school?

                activity_type = activity["activityOffering"]["typeKey"].split(".")[-1].capitalize()

                instructor = activity["activityOffering"]["instructors"]                
                instructors = [instruc["personName"].split(",")[0] for instruc in instructor] # last name
                instr_str = ""
                for ins in instructors:
                    instr_str += ins + " "

                if instr_str not in model.instructors:
                    model.instructors += instr_str[:-1]

                if "M" in days:
                    model.monday = True 
                if "Tu" in days:
                    model.tuesday = True 
                if "W" in days:
                    model.wednesday = True 
                if "Th" in days:
                    model.thursday = True
                if "F" in days:
                    model.friday = True
                if "S" in days and not "Su":
                    model.saturday = True 
                if "Su" in days:
                    model.sunday = True
                
                if "AM" in time:
                    if int(time[:3]) < 10: 
                        model.early_morning = True 
                    else:
                        model.late_morning = True 
                else:
                    if time[:3] == " 12" or time[:3] == " 01": 
                        model.early_afternoon = True 
                    elif time[:3] < " 06": 
                        model.late_afternoon = True 
                    elif time and time not in "Lounge": model.evening = True 


                if activity_type == "Lecture": model.lecture = True 
                elif activity_type == "Discussion": model.discussion = True
                elif activity_type =="Lab": model.lab = True
                elif activity_type == "Doctcontinuation": model.doct_cont = True
                elif activity_type == "Thesis": model.thesis = True
                elif activity_type == "Independ": model.independ = True 
                elif activity_type == "Clinical": model.clinical = True 
                elif activity_type == "Practicum": model.practicum = True 
                elif activity_type == "Internship": model.internship = True 
                elif activity_type == "Recitation": model.recitation = True 
                elif activity_type == "Seminar": model.seminar = True 
                elif activity_type == "Studio": model.studio = True 
                elif activity_type == "Tutorial": model.tutorial = True 
                
                model.save()


def loadCourses(course_code, week, time, credits, delivery, instructor, schools):
    filter_course_info = FilterCourseInfo.objects.all()
    courses = None        
    print(course_code)
    if course_code:
        for cc in course_code:
            if not courses:
                courses = filter_course_info.filter(course_code__icontains=cc)
            else:
                courses |= filter_course_info.filter(course_code__icontains=cc)
    if week:
        week_q_objects = Q()
        for day in week:
            week_q_objects |= Q(**{f'{day}': True})
        if not courses:
            courses = filter_course_info.filter(week_q_objects)
        else:
            courses = courses.filter(week_q_objects)
    if time:
        time_q_objects = Q()
        for period in time:
            time_q_objects |= Q(**{f'{period}': True})
        if not courses:
            courses = filter_course_info.filter(time_q_objects)
        else:
            courses = courses.filter(time_q_objects)
    if credits:
        credits_q_objects = Q()
        for credit in credits:
            credits_q_objects |= Q(credits__icontains=credit)
        if not courses:
            courses = filter_course_info.filter(credits_q_objects)
        else:
            courses = courses.filter(credits_q_objects)
    if delivery:
        delivery_q_objects = Q()
        for d in delivery:
            delivery_q_objects |= Q(**{f'{d}': True})
        if not courses:
            courses = filter_course_info.filter(delivery_q_objects)
        else:
            courses = courses.filter(delivery_q_objects)
    if instructor:
        for instr in instructor:
            if not courses:
                courses = filter_course_info.filter(instructors__icontains=instr)
            else:
                courses |= courses.filter(instructors__icontains=instr)
    if schools:
        for s in schools:
            if not courses:
                courses = filter_course_info.filter(school=s)
            else:
                courses = courses.filter(school=s)
    if not courses:
        return []

    course_ids = [course.course_id for course in courses]
    return course_ids


def getSemester() -> str:
    '''
    Will return semester used for current registration, i.e. 2024S for 2024 Spring
    '''
    today = str(date.today())
    year = today.split('-')[0]
    month = today.split('-')[1]
    sem = 'F' # Between March and September
    if int(month) > 9: # if after September 
        sem = 'S'
        year = str(int(year) + 1)
    elif int(month) < 3: # if before March
        sem = 'S'
        
    return year + sem

def checkClasses(classes, watches):
    '''
    Sets classes to drop and with correct alert if previously added to watchlist
    '''
    for i in range(len(classes)):
        for j in range(len(classes[i]["activities"])):
            for watch in watches:
                alert = watches[watch].get(classes[i]["activities"][j]["id"])
                if watch == classes[i]["courseOffering"]["id"] and alert:
                    classes[i]["activities"][j]["watching"] = True
                    classes[i]["activities"][j]["alert"] = alert

    return classes

def cleanWatchlist(watchlist: List[PersonalWatchlist]):
    '''
    Organizes and strutures watchlist information to easily mark classes as being watched in checkClasses()
    '''
    ids = {watch.class_id: dict() for watch in watchlist}
    for activity in watchlist:
        # Due to activity ID's being duplicates, keeps them in their corresponding course
        ids[activity.class_id].update({activity.activity_id: activity.alert, "course_code": activity.course_code})
    return ids

def remove_html_tags(text):
    # Removes html tags from description
    parser = etree.HTMLParser()
    tree = etree.fromstring(text, parser)
    return etree.tostring(tree, encoding='unicode', method='text')

def cleanClasses(classes):
    '''
    Gets activity information for every course being displayed
    '''
    to_remove = [] # Used before for blank classes, keep in case
    for i in range(len(classes)):

        # gets course credits
        classes[i]["courseOffering"]["creditOptionId"] = float(classes[i]["courseOffering"]["creditOptionId"][-3:])

        # gets clean description
        classes[i]["courseOffering"]["descr"]["formatted"] = remove_html_tags(classes[i]["courseOffering"]["descr"]["formatted"])

        class_id = classes[i]["courseOffering"]["id"]

        # Activity list API call
        r = requests.get(f"{settings.API_ENDPOINT}/waitlist/waitlistactivityofferings?courseOfferingId=" + class_id)
        activites = []
        if r.status_code == 200:
            cls = r.json()

            # Loop through each section of a course
            for c in cls:
                instructor = c["activityOffering"]["instructors"]                
                instructors = [instruc["personName"] for instruc in instructor] # in case of multiple instructors
                instr_str = ""
                activity_seat_count = c.get("activitySeatCount")
                if activity_seat_count:
                    used_seats = activity_seat_count.get("used")
                    total_seats = activity_seat_count.get("total")
                else:
                    used_seats = 0
                    total_seats = 0

                # From list to string to display
                for instr in instructors:
                    instr_str += instr + ", "
                
                events = c["events"]
                if len(events) == 0:
                    # Asynch classes
                    location = "None"
                    time = c["scheduleNames"][0]
                    day = "None"
                else:
                    location = events[0]["locationDescription"]
                    place = c["scheduleNames"][0][len(location) + 1:].split(" ")
                    if place[0].lower() == "by":
                        day = "None"
                        time = c["scheduleNames"][0][len(location):]
                    else:
                        day = place[0]
                        time = c["scheduleNames"][0][len(location) + len(day) + 1:]

                # Create structure of activity information to be added to front end
                course = {
                    "instructors": instr_str[:-2],
                    "enrollment": c["activityOffering"]["maximumEnrollment"],
                    "time": time,
                    "location": location,
                    "id": c["activityOffering"]["activityCode"],
                    "section": c["activityOffering"]["activityCode"],
                    "activity_type": c["activityOffering"]["typeKey"].split(".")[-1].capitalize(),
                    "day": day,
                    "watching": False,
                    "registered": f"{used_seats} of {total_seats}",
                    "name": c["activityOffering"]["name"]
                }
                activites.append(course)
        
        # If no sections found
        if len(activites) == 0:
            to_remove.append(i)

        # Puts activity info into the classes struct
        classes[i]["activities"] = activites

    # blank classes get removed (no activities)
    # for index in sorted(to_remove, reverse=True):
    #     del classes[index]
    return classes

def landingPage(request: HttpRequest):

    # Checks if user has been verified by OAuth
    session = request.session.get("user")

    if not session:
        return redirect("/login")

    # User information
    name = session["userinfo"].get("name")
    email = session["userinfo"].get("email")
    bc_user = email.endswith("@bc.edu")
    if not bc_user:
        return redirect("/login")

    if len(FilterCourseInfo.objects.all()) == 0:
        create_class_list()
    
    # See if user exists in database
    try:
        user = Student.objects.get(username=session["userinfo"]["nickname"])
    except:
        return redirect("/signUp")

    semester = getSemester()

    STEP = 25 # This is how many classes are shown, there's only 23 CSCI so i made it 5

    # Get last open class so that it can be opened on refresh
    open_course = request.session.get("open_class")
    # Reset
    request.session["open_class"] = ""

    # Get last page so that it opens correct class on the correct page
    start = request.session.get("start")
    if not start: start = 0
    if start == -1: start = 0
    end = start + STEP

    # Get user's watchlists 
    watchlist = PersonalWatchlist.objects.filter(user=session["userinfo"]["nickname"], active_semester=semester)

    # Getting state of system
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
    majors = RegistrationFormStudent.majors_choice

    # Page change ...
    if request.method == "POST": 
        # Check for type of post update
        data = request.POST 
        if data.get("clear"):
            request.session["filters"] = None
        if data.get("remove"):
            remove = data.get("remove").split(" ")[-1]
            session_filters = request.session["filters"]
            for filter in session_filters:
                if remove in session_filters[filter]:
                    session_filters[filter].remove(remove)
        if data.get("filters"):
            start = 0
            end = start + STEP

            #filter functionality
            search = request.POST.get('search', "")
            course_code = request.POST.getlist('course_code', [])
            week = request.POST.getlist('week', [])
            time = request.POST.getlist('time', [])
            credits = request.POST.getlist('credits', [])
            delivery = request.POST.getlist('delivery', [])
            instructor = request.POST.get("instructor", "")
            school = request.POST.getlist("school", [])

            # if blank submit button pressed, gets all classes right now
            # can change it so it just updates what's already there

            if request.session.get("filters"):
                if request.session["filters"].get("course_code"):
                    request.session["filters"]["course_code"] = list(set(request.session["filters"]["course_code"] + course_code))
                else:
                    request.session["filters"]["course_code"] = course_code

                if request.session["filters"].get("week"):
                    request.session["filters"]["week"] = list(set(request.session["filters"]["week"] + week))
                else:
                    request.session["filters"]["week"] = week

                if request.session["filters"].get("time"):
                    request.session["filters"]["time"] = list(set(request.session["filters"]["time"] + time))
                else:
                    request.session["filters"]["time"] = time

                if request.session["filters"].get("credits"):
                    request.session["filters"]["credits"] = list(set(request.session["filters"]["credits"] + credits))
                else:
                    request.session["filters"]["credits"] = credits

                if request.session["filters"].get("delivery"):
                    request.session["filters"]["delivery"] = list(set(request.session["filters"]["delivery"] + delivery))
                else:
                    request.session["filters"]["delivery"] = delivery

                if request.session["filters"].get("school"):
                    request.session["filters"]["school"] = list(set(request.session["filters"]["school"] + school))
                else:
                    request.session["filters"]["school"] = school
                
                if instructor != "":
                    request.session["filters"]["instructor"] += [instructor]

                if search != "":
                    request.session["filters"]["search"] = list(set(request.session["filters"]["search"] + [search]))
                

            else:
                request.session["filters"] = {
                    "course_code": course_code,
                    "week": week,
                    "time": time,
                    "credits": credits,
                    "delivery": delivery,
                    "instructor": [instructor] if instructor != "" else [],
                    "search": [search] if search != "" else [],
                    "school": school
                }

        # Page change ...
        if data.get("paginate"):
            value = data.get('paginate')

            # Get current start and end numbers to know where the next ones go
            start_end = data.get("values").split(" ")
            start = int(start_end[0])
            end = int(start_end[1])

            if value == "page_left":
                start -= STEP
                if start < 0:
                    start = 0
                end = start + STEP 
            else:
                start += STEP
                end = start + STEP

    filters = []
    session_filters = request.session.get("filters")
    if session_filters:
        course_code = session_filters.get("course_code")
        week = session_filters.get("week")
        time = session_filters.get("time")
        credits = session_filters.get("credits")
        delivery = session_filters.get("delivery")
        instructor = session_filters.get("instructor")
        search = session_filters.get("search")
        schools = session_filters.get("school")
        if course_code or week or time or credits or delivery or instructor or schools:
            course_ids = loadCourses(course_code, week, time, credits, delivery, instructor, schools)
        else:
            course_ids = None
        if course_code or week or time or credits or delivery or instructor or schools or search:
            filters += [f"Subject Area: {code}" for code in course_code]
            filters += [f"Day: {day}" for day in week]
            filters += [f"Time of Day: {ti}" for ti in time]
            filters += [f"Credits: {credit}" for credit in credits]
            filters += [f"Delivery Method: {deliver}" for deliver in delivery]
            filters += [f"Instructor: {instr}" for instr in instructor]
            filters += [f"Keyword: {s}" for s in search]
            filters += [f"School: {scho}" for scho in schools]
    else:
        course_code = week = time = credits = delivery = instructor = schools = None
        course_ids = None
        search = None

    #filter_course_info for conbining course_code
    classes = []
    tmp = []
    if search:
        for url in search:
            r = requests.get(f'{settings.API_ENDPOINT}/waitlist/waitlistcourseofferings?termId=kuali.atp.FA2023-2024&code={url}')
            if r.status_code == 200:
                tmp += r.json()

    else:
        api_url = f'{settings.API_ENDPOINT}/waitlist/waitlistcourseofferings?termId=kuali.atp.FA2023-2024&code='
        response = requests.get(api_url)
        if response.status_code == 200:
            tmp = response.json()
            if len(FilterCourseInfo.objects.all()) != len(tmp):
                create_class_list()

    if course_ids:
        for t in tmp:
            if t["courseOffering"]["id"] in course_ids:
                classes.append(t)
    elif course_ids == []:
        classes = []
    else:
        classes = tmp

    course_length = len(classes)

    # Correct end for pages with less than STEP classes
    if course_length == 0:
        start = end = -1
    if start > course_length - 1:
        start -= STEP
    if end >  course_length - 1:
        end = course_length - 1
    
    # Save start and end
    request.session["start"] = start 
    request.session["end"] = end
    
    course_length = len(classes)
    # classes = classes[page*ppage+1: page*ppage+1+ppage]
    classes = classes[start : end+1]

    # Get activity listings for displaying classes
    classes = cleanClasses(classes)

    # If user has watchlists, display them as dropping instead of adding
    if watchlist:
        watches = cleanWatchlist(watchlist)
        classes = checkClasses(classes, watches)

    # Render correct page based on user information
    return render(request, "landingPage.html", locals())

def drop_class(class_id, activity_id, user):
    '''
    Delete instance of a section of a class
    '''
    semester = getSemester()
    watch = PersonalWatchlist.objects.filter(
        class_id=class_id,
        activity_id=activity_id,
        user=user,
        active_semester=semester
    )
    if watch:
        watch.delete()

        # Update overall watchlist
        course = OverallWatchlist.objects.filter(
            class_id=class_id,
            activity_id=activity_id,
            active_semester=semester
        ).first()
        course.remove_watcher()
        course.save()

def add_class(class_id, activity_id, user, data, user_name):
    '''
    Add a class to watchlist and create instance of overall watchlist if needed
    '''
    semester = getSemester()
    class_name = data.get('class_name')
    course_code = class_name.split(" ")[0]
    section_name = data.get("section_name")
    professor = data.get("professor")

    student = Student.objects.get(username=user)
    edit = True
    watch = PersonalWatchlist.objects.filter(
            class_id=class_id, 
            activity_id=activity_id,
            user=user,
            active_semester=semester
        ).first()

    if not watch:
        edit = False
        # Create new class
        watch = PersonalWatchlist(
            class_id=class_id,
            class_name=class_name,
            activity_id=activity_id,
            alert=data.get('watchlistOptions mb-2'),
            user=user,
            course_code=course_code,
            user_name=user_name,
            active_semester=semester,
            grad_sem=student.grad_sem+student.grad_year
        )
        watch.save()
    else:
        # Edit class alert
        watch.alert = data.get('watchlistOptions mb-2')
        watch.save()

    # Update overall watchlist
    course = OverallWatchlist.objects.filter(
        class_id=class_id,
        activity_id=activity_id,
        active_semester=semester
    ).first()

    if not course:
        # Create if first instance of class
        course = OverallWatchlist(
            class_id=class_id,
            class_name=section_name,
            activity_id=activity_id,
            num_watchers=0,
            active_semester=semester,
            professor=professor,
            course_code=course_code+activity_id,
            class_name_filter=section_name.split(" - ")[1]
        )
    if not edit:
        course.add_watcher()
    course.save()

def notification_selection(request): 
    '''
    Get POST data from search page and add, drop, or edit a section
    '''
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
        request.session["open_class"] = class_id

    return redirect("/search/")



            



