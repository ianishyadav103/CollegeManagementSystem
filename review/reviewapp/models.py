from django.db import models

# Create your models here.

    
class teacher_data(models.Model): #manual entry
    name = models.CharField(max_length=25)
    email = models.EmailField()
    qualifications = models.CharField(max_length=200)
    def __str__(self):
        return self.email

def update_filename(instance,f):
    return 'train/'+ instance.course.c_name + " " + instance.course.batch + "/" + instance.prn + ".jpg"


class courses(models.Model): 
    c_name = models.CharField(max_length=8)
    batch = models.CharField(max_length=10)
    total_sem = models.IntegerField()
    current_sem = models.IntegerField(null=True)

    def __str__(self):
        return self.c_name +" "+ self.batch


class semester(models.Model):
    course = models.ForeignKey(courses, on_delete=models.SET_NULL,null=True)
    sem = models.IntegerField()
    start_date = models.CharField(max_length=10)
    end_date = models.CharField(max_length=10)
    def __str__(self):
        return self.course.c_name +" "+ self.course.batch + " " + "Sem: " +str(self.sem)

class subject(models.Model):
    sub_name = models.CharField(max_length=50)
    sem_course = models.ForeignKey(semester, on_delete=models.SET_NULL,null=True) 
    credit = models.IntegerField()
    div_group = models.CharField(max_length=10)
    teacher_reference = models.ForeignKey(teacher_data, on_delete=models.SET_NULL,null=True)
    count = models.CharField(max_length=2,default=0)
    last_modified = models.CharField(max_length=12,null=True,blank=True)
    last_modified_by = models.CharField(max_length=20,null=True,blank=True)
     #testing vs1
    def __str__(self):
        return self.sub_name + " " + self.sem_course.course.c_name +" "+ self.sem_course.course.batch + " " + "Sem: " +str(self.sem_course.sem) + " " + self.div_group

class timetable(models.Model): #created through drag and drop by co-ordinator
    subject_reference = models.ForeignKey(subject, on_delete=models.CASCADE)
    start_time = models.CharField(max_length=7)
    end_time = models.CharField(max_length=7)
    room = models.IntegerField()
    day = models.CharField(max_length=10)
    def __str__(self):
        return self.subject_reference.sub_name + " " + self.subject_reference.sem_course.course.c_name +" "+ self.subject_reference.sem_course.course.batch + " " + " " + self.day + " " + str(self.room) + " " + self.start_time

class timetable_default_custom(models.Model):
    subject_reference = models.ForeignKey(subject, on_delete=models.CASCADE)
    start_time = models.CharField(max_length=7)
    end_time = models.CharField(max_length=7)
    room = models.IntegerField()
    date_c = models.CharField(max_length=10)
    def __str__(self):
        return self.subject_reference.sub_name + " " + self.subject_reference.sem_course.course.c_name +" "+ self.subject_reference.sem_course.course.batch + " " + " " + self.date_c + " " + str(self.room) + " " + self.start_time

class timetable_deleted(models.Model):
    timetable_reference = models.ForeignKey(timetable, on_delete=models.CASCADE)
    date_c = models.CharField(max_length=10)
    def __str__(self):
        return self.timetable_reference.subject_reference.sub_name + " " + self.timetable_reference.subject_reference.sem_course.course.c_name +" "+ self.timetable_reference.subject_reference.sem_course.course.batch + " " + " " + self.date_c + " " + str(self.timetable_reference.room) + " " + self.timetable_reference.start_time

class timetable_custom(models.Model): 
    sub_name_c = models.CharField(max_length=25)
    start_time_c = models.CharField(max_length=7)
    end_time_c = models.CharField(max_length=7)
    room_c = models.IntegerField()
    date_c = models.CharField(max_length=10)
    description_c = models.CharField(max_length=35)
    def __str__(self):
        return self.sub_name_c + " " + self.date_c + " " + str(self.room_c) + " " + self.start_time_c
    

class student_data(models.Model):
    prn = models.CharField(max_length=15)
    name = models.CharField(max_length=25)
    div = models.CharField(max_length=25)
    email = models.EmailField()
    course = models.ForeignKey(courses, on_delete=models.SET_NULL,null=True)
    train_image = models.ImageField(upload_to=update_filename,null=True)
    def __str__(self):
        return self.prn

class student_sub_elective(models.Model):
    stud_reference = models.ForeignKey(student_data, on_delete=models.CASCADE)
    subject_reference =  models.ForeignKey(subject, on_delete=models.CASCADE,blank=True,null=True) #testing vs1
    def __str__(self):
        return self.stud_reference.prn


class attendance(models.Model):
    stud_reference = models.ForeignKey(student_data, on_delete=models.CASCADE)
    attendance_count = models.CharField(max_length=2,default=0)
    subject =  models.ForeignKey(subject, on_delete=models.CASCADE)
    marked_on = models.CharField(max_length=25,null=True)
    def __str__(self):
        return self.stud_reference.prn

class inquiry_contacts_i(models.Model):
    group_name = models.CharField(max_length=25)
    description = models.CharField(max_length=20,null=True)
    admin = models.EmailField(null=True)
    def __str__(self):
        return self.group_name

class inquiry(models.Model):
    email_from = models.EmailField()
    text_i = models.CharField(max_length=300)
    time_i = models.CharField(max_length=5)
    date_i = models.CharField(max_length=25)
    contacts_i = models.ForeignKey(inquiry_contacts_i, on_delete=models.CASCADE)

class complain(models.Model):
    from_email_hidden = models.EmailField()
    subject_c = models.CharField(max_length=200)
    against_c = models.EmailField()
    text_c = models.CharField(max_length=500)
    date_c = models.CharField(max_length=25)
    to_email = models.EmailField()

class notes_d(models.Model):
    sub_n = models.ForeignKey(subject, on_delete=models.CASCADE)
    file_n = models.FileField(upload_to="notes/")
    name  = models.CharField(max_length=50)

class calendar_d(models.Model):
    date_e = models.CharField(max_length=10)
    desc_e = models.CharField(max_length=80)
    type_c = models.CharField(max_length=20)
    for_c = models.CharField(max_length=20)

class otp_d(models.Model):
    date_o = models.DateTimeField(null=True)
    otp_o = models.CharField(max_length=13,null=True)
    user_o = models.EmailField()
    count_o = models.IntegerField(default=0)