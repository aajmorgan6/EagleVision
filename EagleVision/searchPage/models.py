from django.db import models

# Create your models here.

class FilterCourseInfo(models.Model):
    '''
    Do an initial grab of all classes and populate the db with these filterable things
    Will have to be mostly boolean fields since can't filter with "in", like
    ...filter("thursday" in day) doesn't work
    '''
    course_id = models.CharField(max_length=50) # class id for overall class
    course_code = models.CharField(max_length=9) # i.e. CSCI2243, no activity code  
    
    monday = models.BooleanField(default=False)
    tuesday = models.BooleanField(default=False)
    wednesday = models.BooleanField(default=False)
    thursday = models.BooleanField(default=False)
    friday = models.BooleanField(default=False)
    saturday = models.BooleanField(default=False)
    sunday = models.BooleanField(default=False)
    asynch = models.BooleanField(default=False)

    early_morning = models.BooleanField(default=False)
    late_morning = models.BooleanField(default=False)
    early_afternoon = models.BooleanField(default=False)
    late_afternoon = models.BooleanField(default=False)
    evening = models.BooleanField(default=False)

    credits = models.CharField(max_length=10)

    lecture = models.BooleanField(default=False)
    discussion = models.BooleanField(default=False)
    lab = models.BooleanField(default=False)
    seminar = models.BooleanField(default=False)
    studio = models.BooleanField(default=False)
    clinical = models.BooleanField(default=False)
    doct_cont = models.BooleanField(default=False)
    field = models.BooleanField(default=False)
    thesis = models.BooleanField(default=False)
    hybrid = models.BooleanField(default=False)
    independ = models.BooleanField(default=False)
    internship = models.BooleanField(default=False)
    online = models.BooleanField(default=False)
    online_async = models.BooleanField(default=False)
    online_sync = models.BooleanField(default=False)
    practicum = models.BooleanField(default=False)
    recitation = models.BooleanField(default=False)
    tutorial = models.BooleanField(default=False)

    school = models.CharField(max_length=10)

    instructors = models.CharField(max_length=200, default="")

    active_semester = models.CharField(max_length=6)

    def __str__(self):
        return self.course_code
