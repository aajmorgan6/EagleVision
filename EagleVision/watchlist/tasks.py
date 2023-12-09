from __future__ import absolute_import, unicode_literals
from django.core.mail import send_mass_mail
from django.conf import settings
from EagleVision.celery import app
from watchlist.models import PersonalWatchlist, OverallWatchlist
from profilePage.models import SystemConfig
import requests
from searchPage.views import getSemester
from EagleVision.celery import app


@app.task(bind=True)
def send_emails(self):
    semester = getSemester()
    # check if system is on
    if SystemConfig.objects.filter(semester_code=semester).first():
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
                message = f"Hurry, {available} spot{s} left in {watch.class_name}! Go to https://eaen.bc.edu/student-registration/#/ to register!\nIf you want to stop this alert, remove this class from your watchlist at {settings.API_ENDPOINT}/profile/"
                from_email = settings.EMAIL_HOST_USER
                messages_list = [(subject, message, from_email, [email]) for email in emails]
                messages += tuple(messages_list)
        send_mass_mail(
            messages,
            fail_silently=False
        )

