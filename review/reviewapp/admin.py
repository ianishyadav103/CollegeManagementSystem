from django.contrib import admin

# Register your models here.
from reviewapp.models import teacher_data, courses, semester, subject, student_data, student_sub_elective, attendance, timetable, timetable_default_custom ,timetable_custom, timetable_deleted,inquiry_contacts_i, inquiry, complain, notes_d, calendar_d, otp_d

admin.site.register(teacher_data)
admin.site.register(courses)
admin.site.register(semester)
admin.site.register(subject)
admin.site.register(student_data)
admin.site.register(student_sub_elective)
admin.site.register(attendance)
admin.site.register(timetable)
admin.site.register(timetable_default_custom)
admin.site.register(timetable_custom)
admin.site.register(timetable_deleted)
admin.site.register(inquiry_contacts_i)
admin.site.register(inquiry)
admin.site.register(complain)
admin.site.register(notes_d)
admin.site.register(calendar_d)
admin.site.register(otp_d)