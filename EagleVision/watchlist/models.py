from django.db import models

# Create your models here.

class OverallWatchlist(models.Model): 
    """
    Watchlist Overview

    Each individual class will get this and be updated in num_watchers
    with each users' add to watchlist
    Used for /watchlist page, with button to list of students using WatchListP
    """
    class_id = models.CharField(max_length=50) # unique id for each course, maybe the activity ID for specific section?
    course_code = models.CharField(max_length=10)
    activity_id = models.CharField(max_length=50)
    class_name = models.CharField(max_length=50) # displayable class name
    professor = models.CharField(max_length=50) # professor name to display
    class_name_filter = models.CharField(max_length=50)
    num_watchers = models.IntegerField() # number of watchers for each class
    active_semester = models.CharField(max_length=6) # Active period of watchlists, can filter through this

    def __str__(self):
        return f"{self.class_name} -- {self.num_watchers} watchers"

    def add_watcher(self):
        self.num_watchers += 1

    def remove_watcher(self):
        if self.num_watchers > 0:
            self.num_watchers -= 1
        else:
            raise ValueError("Can't remove more students")


class PersonalWatchlist(models.Model):
    """
    Watchlist Personal

    Each individual watchlist, with a unique combination of class_id, user, and alert
    Will be displayed by filtering through class_id for the individual watchlist pages
    """
    # we'll see what else we need
    class_id = models.CharField(max_length=50) # unique id for each course, can be used to then find specific section
    course_code = models.CharField(max_length=10)
    activity_id = models.CharField(max_length=50) # activity id, not sure how to search it
    class_name = models.CharField(max_length=50) # displayable class name
    user = models.CharField(max_length=50) # i.e. morganan
    user_name = models.CharField(max_length=100) # i.e. Addison Morgan
    alert = models.CharField(max_length=50) # at what point to alert
    alerted = models.BooleanField(default=False) # so it doesn't continuously send emails for same spot
    active_semester = models.CharField(max_length=6) # Active period of watchlists
    grad_sem = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.class_name} {self.activity_id} {self.user} {self.class_id}"