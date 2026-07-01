from . import views
from django.urls import path

urlpatterns = [

    #real
    path('',views.xlogin,name='xlogin'),
    path('login_form_validate/',views.login_form_validate,name='login_form_validate'),
    path('xlogout/',views.xlogout,name='xlogout'),
    path('takeattendance/<sub>',views.take_attendace,name='take_attendace'),
    path('get_img/',views.get_img,name="get_img"),
    path('img_upload/',views.img_upload,name="img_upload"),
    path('train/',views.train,name="train"),
    path('checkattendance/<sub>',views.check_attendance,name='check_attendace'),
    path('inquiry/',views.inquiry_z,name="inquiry_z"),
    path('get_inquiry/',views.get_inquiry,name="get_inquiry"),
    path('set_inquiry/',views.set_inquiry,name="set_inquiry"),
    path('complaint/',views.complain_form,name="complain_form"),
    path('save_complaint/',views.save_complain_form,name="save_complain_form"),
    path('course material/',views.notes,name="notes"),
    path('savenotes/<sub_id>',views.save_notes,name='save_notes'),
    path('delete_notes/<note_id>',views.delete_notes,name='delete_notes'),
    path('calendar/',views.calendar,name='calendar'),
    path('calendar_c/',views.coordinator_calendar,name='coordinator_calendar'),
    path('send_mail_p/',views.send_mail_password,name='send_mail_pasword'),
    path('get_mail_p/',views.get_mail_password,name='get_mail_pasword'),
    path('set_p/',views.set_password,name='set_pasword'),
    
        ##student
    path('home/student/',views.student_home,name='student_home'),
    path('home/student/timetable/',views.student_time_table,name='student_time_table'),
    path('home/student/attendance/',views.student_atendance,name='student_atendance'),

        ##faculty
    path('home/faculty/',views.faculty_home,name='faculty_home'),
    path('home/faculty/timetable/',views.faculty_time_table,name='faculty_time_table'),
    path('home/faculty/attendance/',views.faculty_attendance,name='faculty_atendance'),
    path('home/faculty/timetable/regular/save/',views.faculty_time_table_save,name='faculty_time_table_regular_save'),
    path('home/faculty/attendance/modify/',views.faculty_attendance_modify,name='faculty_attendance_modify'),

    
        ##coordinator
    path('home/coordinator/',views.coordinator_home,name='coordinator_home'),
    path('home/coordinator/admin/',views.coordinator_admin,name='coordinator_admin'),
    path('home/coordinator/admin/save/',views.coordinator_admin_save,name='coordinator_admin_save'),
    path('home/coordinator/timetable/regular/',views.coordinator_time_table_regular,name='coordinator_time_table_regular'),
    path('home/coordinator/timetable/regular/save/',views.coordinator_time_table_regular_save,name='coordinator_time_table_regular_save'),
    path('home/coordinator/timetable/semester/',views.coordinator_time_table_semester,name='coordinator_time_table_semester'),
    path('home/coordinator/timetable/semester/save/',views.coordinator_time_table_semester_save,name='coordinator_time_table_semester_save'),
    path('home/coordinator/attendance/',views.coordinator_attendance,name='coordinator_atendance'),


    
]
#add module: document submission/assignment submission, chatbot