from __future__ import absolute_import, unicode_literals
from django.core.mail import send_mass_mail
from EagleVision.celery import app
from profilePage.models import SystemConfig
import requests
from searchPage.models import FilterCourseInfo
from EagleVision.celery import app
from django.conf import settings
from datetime import date

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


@app.task(bind=True)
def check_classes(self):
    semester = getSemester()
    sys = SystemConfig.objects.filter(semester_code=semester).first()
    if not sys:
        return
    if sys.system_open:
        r = requests.get(f"{settings.API_ENDPOINT}/waitlist/waitlistcourseofferings?termId=kuali.atp.FA2023-2024&code=")
        if r.status_code == 200:
            classes = r.json()
            filter_courses = FilterCourseInfo.objects.all()
            if len(classes) != len(filter_courses):
                for course in classes:
                    if not FilterCourseInfo.objects.filter(course_id=course["courseOffering"]["id"]).first():
                        model = FilterCourseInfo()
                        model.course_id = course["courseOffering"]["id"]
                        model.course_code = course["courseOffering"]["courseCode"]
                        model.credits = course["courseOffering"]["creditOptionId"][-3:]
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
                                time = ""
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
                            
                            if "AM" in time:
                                if time[:2] < "10": model.early_morning = True 
                                else: model.late_morning = True 
                            else:
                                if time[:2] == "12" or time[:2] == "01": model.early_afternoon = True 
                                elif time[:2] < "06": model.late_afternoon = True 
                                else: model.evening = True 

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