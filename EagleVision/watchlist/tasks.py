from __future__ import absolute_import, unicode_literals
from django.core.mail import send_mass_mail
from django.conf import settings
from EagleVision.celery import app
from watchlist.models import PersonalWatchlist, OverallWatchlist
from profilePage.models import SystemConfig
import requests
from searchPage.views import getSemester
from searchPage.models import FilterCourseInfo
from celery import shared_task # type: ignore

@shared_task(bind=True)
def send_emails(self):
    semester = getSemester()
    # check if system is on
    if SystemConfig.objects.get(semester_code=semester):
        overall_watch = OverallWatchlist.objects.all()
        messages = tuple()
        for watch in overall_watch:
            # get num available
            if watch.num_watchers <= 0:
                continue
            r = requests.get(f"{settings.API_ENDPOINT}/waitlist/waitlistactivityofferings?courseOfferingId=" + watch.class_id)
            if r.status_code == 200:
                activities = r.json()
                available = 0
                for activity in activities:
                    if activity["activityOffering"]["activityCode"] == watch.activity_id:
                        available = activity["activitySeatCount"]["available"]
                        break
                print(f'{available=}')
                personal = PersonalWatchlist.objects.filter(class_id=watch.class_id, activity_id=watch.activity_id)
                emails = []
                for p in personal:
                    if int(p.alert) <= available: # add in p.alerted
                        if not p.alerted:
                            if "blank" not in p.user: # dev for now, have blank users
                                emails.append(p.user+"@bc.edu")
                            print(f'alerting {p.user}')
                            p.alerted = True
                            p.save()
                    elif p.alerted:
                        p.alerted = False
                        p.save()
                s = "s" if available != 1 else ""
                subject = f"Open Spot in {watch.class_name}"
                message = f"Hurry, {available} spot{s} left in {watch.class_name}! Go to https://eaen.bc.edu/student-registration/#/ to register!\nIf you want to stop this alert, remove this class from your watchlist at http://127.0.0.1:3000/profile/"
                from_email = settings.EMAIL_HOST_USER
                messages_list = [(subject, message, from_email, [email]) for email in emails]
                messages += tuple(messages_list)
        send_mass_mail(
            messages,
            fail_silently=False
        )


@shared_task(bind=True)
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