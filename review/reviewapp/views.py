from django.shortcuts import render
from django.core.mail import send_mail
from django.views.decorators.cache import cache_control
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate,login,logout,get_user_model
import face_recognition, pickle, numpy as np, cv2 as cv, json, base64, openpyxl, os, random
from . models import teacher_data, courses, semester, subject, student_data, student_sub_elective,attendance, timetable, timetable_default_custom ,timetable_custom, timetable_deleted, inquiry, inquiry_contacts_i, complain, notes_d, calendar_d, otp_d
from datetime import datetime, timedelta

#multithreading
#yml
#replace inculde.html with extends.html
#has chat app made this complete appkication async ?
#put condtions of columns of excel like some allowed values only
#clear otp dict on backup
def xlogout(request): #not inegrated
    logout(request)
    return HttpResponseRedirect("/")
    


@cache_control(no_store=True)
def xlogin(request):
    xuser = request.user
    if(xuser.is_authenticated):
        if(xuser.groups.filter(name='student').exists()):
            return HttpResponseRedirect("/home/student")
        elif(xuser.groups.filter(name='faculty').exists()):
            return HttpResponseRedirect("/home/faculty")
        elif(xuser.groups.filter(name='coordinator').exists()):
            return HttpResponseRedirect("/home/coordinator")
        else:
            return render(request,'login.html')
    else:
        return render(request,'login.html')

def login_form_validate(request):
    xgroup = request.POST['login_as']
    xuser = authenticate(username = request.POST['username'],password = request.POST['password'])
    if (xuser is not None) and (xuser.groups.filter(name=xgroup).exists()):
        login(request,xuser)
        return HttpResponseRedirect(f"/home/{xgroup}")
    else:
        return HttpResponseRedirect("/")

    ##STUDENT

def student_home(request):
    xuser = request.user
    if(xuser.is_authenticated and xuser.groups.filter(name='student').exists()):
        data = student_data.objects.get(email=str(xuser))
        return render(request,'student_home.html',{"data":data})
    else:
        return HttpResponseRedirect("/")

def student_time_table(request):
    xuser = request.user
    if(xuser.is_authenticated and xuser.groups.filter(name='student').exists()):
        data = student_data.objects.get(email=str(xuser))
        l=[]
        for x in student_sub_elective.objects.filter(stud_reference = data):
            l.append(x.subject_reference)
        temp = subject.objects.filter(sem_course = semester.objects.get(course = data.course), div_group = data.div )

        #real_core
        real_core = timetable.objects.filter(subject_reference__in = temp) | (timetable.objects.filter(subject_reference__in = l))
   
        #custom
        custom = timetable_custom.objects.all()

        #custom_default
        custom_default = timetable_default_custom.objects.filter(subject_reference__in = temp) | timetable_default_custom.objects.filter(subject_reference__in = l)
        
        #deleted_core
        deleted_core = timetable_deleted.objects.filter(timetable_reference__in = real_core)
        return render(request,'student_time_table.html',{"data":data,"real_core":real_core,"custom_default":custom_default,"custom":custom,"deleted_core":deleted_core})
    else:
        return HttpResponseRedirect("/")

def student_atendance(request):
    xuser = request.user
    if(xuser.is_authenticated and xuser.groups.filter(name='student').exists()):
        data = student_data.objects.get(email=str(xuser))
        temp_l = student_sub_elective.objects.filter(stud_reference = data).values_list("subject_reference",flat=True)
        all_sub = subject.objects.filter(sem_course = semester.objects.get(course = data.course), div_group = data.div) | subject.objects.filter(id__in = temp_l)
        attendance_d = attendance.objects.filter(stud_reference = data)
        return render(request,'student_attendance.html',{"data":data,"all_sub":all_sub,"attendance_d":attendance_d})
    else:
        return HttpResponseRedirect("/")

    ##FACULTY

def faculty_home(request):
    xuser = request.user
    if(xuser.is_authenticated and xuser.groups.filter(name='faculty').exists()):
        data = teacher_data.objects.get(email=str(xuser))
        return render(request,'faculty_home.html',{"data":data})
    else:
        return HttpResponseRedirect("/")

def faculty_time_table(request):
    xuser = request.user
    if(xuser.is_authenticated and xuser.groups.filter(name='faculty').exists()):
        data = teacher_data.objects.get(email=str(xuser))

        #real_core
        temp =  subject.objects.filter(teacher_reference = data)
        real_core = timetable.objects.filter(subject_reference__in = temp)
   
        #custom
        custom = timetable_custom.objects.all()

        #custom_default
        custom_default = timetable_default_custom.objects.filter(subject_reference__in = temp) 
        
        #deleted_core
        deleted_core = timetable_deleted.objects.filter(timetable_reference__in = real_core)
        return render(request,'faculty_time_table.html',{"data":data,"real_core":real_core,"custom_default":custom_default,"custom":custom,"deleted_core":deleted_core})
    else:
        return HttpResponseRedirect("/")

def faculty_attendance(request):
    xuser = request.user
    if(xuser.is_authenticated and xuser.groups.filter(name='faculty').exists()):
        data = teacher_data.objects.get(email=str(xuser))
        
        all_sub = subject.objects.filter(teacher_reference =data )
        return render(request,'faculty_attendance.html',{"data":data,"all_sub":all_sub})
    else:
        return HttpResponseRedirect("/")

def check_attendance(request,sub):
    xuser = request.user
    if(xuser.is_authenticated and xuser.groups.filter(name='faculty').exists()):
        data = teacher_data.objects.get(email=str(xuser))
    elif(xuser.is_authenticated and xuser.groups.filter(name='student').exists()):
        data = student_data.objects.get(email=str(xuser))
    else:
        return HttpResponseRedirect("/")

    sub = sub.split(":)")[1]
    sub  = subject.objects.get(id = sub)
    last_att_data = attendance.objects.filter(subject = sub,marked_on = sub.last_modified)
    temp = last_att_data.values_list("stud_reference",flat=True)
    absent_x = student_data.objects.filter(div = sub.div_group).exclude(id__in = temp) 
    if(absent_x.exists()):
        return render(request,'show_last_attendance.html',{"data":data,"last_att_data":last_att_data,"sub":sub,"absent_x":absent_x})
    else:
        absent_x = student_sub_elective.objects.filter(subject_reference = sub).exclude(stud_reference__in = temp)
        absent_x =student_data.objects.filter(id__in = absent_x.values_list("stud_reference",flat=True))
        return render(request,'show_last_attendance.html',{"data":data,"last_att_data":last_att_data,"sub":sub,"absent_x":absent_x})

def faculty_attendance_modify(request):
    xuser = request.user
    if(xuser.is_authenticated and xuser.groups.filter(name='faculty').exists()):
        prn = request.POST['prn_z']
        marked_on = request.POST['marked_on']
        sub_id = request.POST['sub_id']

        att_val =request.POST['attendance_val']
        sub_n = subject.objects.get(id=sub_id)
        if(sub_n.teacher_reference.email == str(xuser)):
            stud = student_data.objects.get(prn = prn)
            if(att_val == "PRESENT"):
                temp = attendance.objects.get(stud_reference = stud, subject = sub_n)
                temp.attendance_count = str(int(temp.attendance_count) - 1)
                temp.marked_on = ""
                temp.save()
            elif(att_val == "ABSENT"):
                temp = attendance.objects.get_or_create(stud_reference = stud, subject = sub_n)
                temp[0].attendance_count = str(int(temp[0].attendance_count) + 1)
                temp[0].marked_on = marked_on
                temp[0].save()

        
        
        return HttpResponseRedirect(f"/checkattendance/{sub_n.sub_name}:){sub_id}")
    else:
        return HttpResponseRedirect("/")

def faculty_time_table_save(request):  
    xuser = request.user
    if(xuser.is_authenticated and xuser.groups.filter(name='faculty').exists()):
        erased = request.POST['erased'].split(":)")
        datez = request.POST['date_x'].split(",")
        tempy = timetable_default_custom.objects.filter(date_c  = datez[1], start_time=erased[1],room = erased[0])
        
        if(tempy.exists()):
            if(tempy[0].subject_reference.teacher_reference.email == str(xuser)):
                tempy.delete()

        tempx = timetable.objects.filter(day = datez[0], start_time=erased[1],room = erased[0])
        if(tempx.exists()):
            if(tempy[0].subject_reference.teacher_reference.email == str(xuser)):
                tempy = timetable_deleted(timetable_reference = tempx[0], date_c = datez[1])
                tempy.save()

        return HttpResponseRedirect("/home/faculty/timetable/")

    else:
        return HttpResponseRedirect("/")

    
    ##COORDINATOR

def coordinator_home(request):
    xuser = request.user
    if(xuser.is_authenticated and xuser.groups.filter(name='coordinator').exists()):
        data = {'name':"Crd " + xuser.first_name + " " + xuser.last_name}
        return render(request,'coordinator_home.html',{'data':data})
    else:
        return HttpResponseRedirect("/")
    
def coordinator_calendar(request):
    xuser = request.user
    if(xuser.is_authenticated and xuser.groups.filter(name='coordinator').exists()):
        wrkbk = openpyxl.load_workbook(request.FILES["calendar_excel"])
        max = 0 
        for x in wrkbk.worksheets[0]["A"]:
            if(str(x.value) != "None"):
                    max = max + 1
        sh = wrkbk.active
        for row in sh.iter_rows(min_row=2, min_col=1, max_row=max, max_col=4): #edit always
            x=[]
            for cell in row:
                x.append(cell.value)
            temp = calendar_d(date_e = x[0].strftime("%d-%m-%Y"), desc_e = x[2], type_c =x[1], for_c = x[3])
            temp.save()       
        return HttpResponseRedirect("/calendar")
    else:
        return HttpResponseRedirect("/")

def coordinator_admin(request):
    xuser = request.user
    if(xuser.is_authenticated and xuser.groups.filter(name='coordinator').exists()):
        data = {'name':"Crd " + xuser.first_name + " " + xuser.last_name}
        courses_d = courses.objects.all()
        semester_d = semester.objects.all()
        return render(request,'coordinator_data_dashboard.html',{'data':data,"courses_d":courses_d,"semester_d":semester_d})
    else:
        return HttpResponseRedirect("/")  
      
def coordinator_admin_save(request):
    xuser = request.user
    if(xuser.is_authenticated and xuser.groups.filter(name='coordinator').exists()):
        type_d = request.POST['type']
        type_d_split = type_d.split(",")

        if(type_d == "sem"):
            c_id = request.POST["course"]
            sem = request.POST["sem"]
            start_date = request.POST["start_date"]
            end_date = request.POST["end_date"]
            course = courses.objects.get(id= c_id)
            temp = semester(course = course, sem = sem, start_date = start_date, end_date = end_date)
            temp.save()

        elif(type_d_split[0] == "course"):
            c_name = request.POST["c_name"]
            start_year = request.POST["start_year"]
            end_year = request.POST["end_year"]
            total_sem = request.POST["total_sem"]
            temp = courses(c_name = c_name, batch = start_year + "-" + end_year,total_sem = total_sem)
            temp.save()

        elif(type_d_split[0] == "Add Students"):
            course_data = courses.objects.get(id =type_d_split[1])
            wrkbk = openpyxl.load_workbook(request.FILES["admin_excel"])
            max = 0 
            for x in wrkbk.worksheets[0]["A"]:
                if(str(x.value) != "None"):
                    max = max + 1
            sh = wrkbk.active
            for row in sh.iter_rows(min_row=2, min_col=1, max_row=max, max_col=5): #edit always
                x=[]
                for cell in row:
                    x.append(cell.value)
                data = student_data(prn = x[0],name = x[1], div = x[2],email = x[3],course = course_data)
                data.save()
                        
                new_user = User.objects.create_user(username= x[3],password=str(x[4]))
                new_user.save()
                g = Group.objects.get(name='student')
                g.user_set.add(new_user)

        elif(type_d_split[0] == "Add Subjects"):
            xsemester = semester.objects.get(id =type_d_split[2])
            wrkbk = openpyxl.load_workbook(request.FILES["admin_excel"])
            max = 0 
            for x in wrkbk.worksheets[0]["A"]:
                if(str(x.value) != "None"):
                    max = max + 1
            sh = wrkbk.active
            for row in sh.iter_rows(min_row=2, min_col=1, max_row=max, max_col=4): #edit always
                x=[]
                for cell in row:
                    x.append(cell.value)
                
                xteacher  = teacher_data.objects.get(email = x[2])
                data = subject(sub_name = x[0], sem_course = xsemester, credit = x[3],  div_group = x[1], teacher_reference = xteacher)
                data.save()

        elif(type_d_split[0] == "Assign Electives"):
            wrkbk = openpyxl.load_workbook(request.FILES["admin_excel"])
            max = 0 
            for x in wrkbk.worksheets[0]["A"]:
                if(str(x.value) != "None"):
                    max = max + 1
            sh = wrkbk.active

            for row in sh.iter_rows(min_row=2, min_col=1, max_row=max, max_col=3):
                x=[]
                for cell in row:
                    x.append(cell.value)
                print(x)
                xstudent_data = student_data.objects.get(email=x[0])
                print(xstudent_data)
                xsemester = semester.objects.get(id =type_d_split[2])
                print(xsemester)
                print(subject.objects.get(div_group=x[2],sub_name = x[1], sem_course=xsemester) )
                xsubject_data = subject.objects.get(div_group=x[2],sub_name = x[1], sem_course=xsemester)
                data = student_sub_elective(stud_reference = xstudent_data, subject_reference = xsubject_data)
                data.save()

        elif(type_d == "Add Faculty Member"):
            name = request.POST["name"]
            email = request.POST["email"]
            qualifications = request.POST["qualifications"]
            password = request.POST["password"]
            temp = teacher_data(name = name,email = email,qualifications = qualifications)
            temp.save()
            new_user = User.objects.create_user(username= email,password=password)
            new_user.save()
            g = Group.objects.get(name='faculty')
            g.user_set.add(new_user)

        elif(type_d == "Add Coordinators"):
            first_name = request.POST["first_name"]
            last_name = request.POST["last_name"]
            email = request.POST["email"]
            password = request.POST["password"]
            new_user = User.objects.create_user(username= email,password=password,email=email,first_name = first_name, last_name = last_name)
            new_user.save()
            g = Group.objects.get(name='coordinator')
            g.user_set.add(new_user)
        return HttpResponseRedirect("/home/coordinator/admin/")
    else:
        return HttpResponseRedirect("/")   

def coordinator_time_table_semester(request):
    xuser = request.user
    if(xuser.is_authenticated and xuser.groups.filter(name='coordinator').exists()):
        data = {'name':"Crd " + xuser.first_name + " " + xuser.last_name}
        time_table = subject.objects.all()
        real_tt = timetable.objects.all()
        return render(request,'coordinator_time_table_semester.html',{'data':data,'time_table':time_table,'real_time_table':real_tt})
    else:
        return HttpResponseRedirect("/")
    

def coordinator_time_table_semester_save(request):
    xuser = request.user
    if(xuser.is_authenticated and xuser.groups.filter(name='coordinator').exists()):
        data = request.POST['corex']
        day = request.POST['corey']
        erased_data = request.POST['corez'].split(":$:")
        for z in range(0,len(erased_data)-1):
            erased = erased_data[z].split(":)")
            tempy = timetable.objects.filter(day = day, start_time=erased[0],end_time =erased[1],room = erased[2])
            if(tempy.exists()):
                tempy.delete()
        #subject_name, course , Sem, Div, start_time, end_time, room, batch
        data = data.split(":$:")
        for x in range(0,len(data)-1):
            x = data[x].split(":)")
            x.append(x[1][-9::1])
            x[1] = x[1].replace(" " + x[7],"")
            course_data = courses.objects.get(batch = x[7],c_name = x[1])
            xsemester = semester.objects.get(course =course_data, sem = x[2])
            xsubject_data = subject.objects.get(div_group=x[3],sub_name = x[0],sem_course=xsemester)
            tempx = timetable.objects.filter(day = day, start_time=x[4],end_time =x[5],room = x[6])
            if(tempx.exists()):
                tempx.delete()
            data_tt = timetable(subject_reference=xsubject_data ,start_time=x[4],end_time =x[5],room =x[6],day=day)
            data_tt.save()

        return HttpResponseRedirect("/home/coordinator/timetable/semester")
    else:
        return HttpResponseRedirect("/")

def coordinator_time_table_regular(request):
    xuser = request.user
    if(xuser.is_authenticated and xuser.groups.filter(name='coordinator').exists()):
        data = {'name':"Crd " + xuser.first_name + " " + xuser.last_name}
        time_table = subject.objects.all()
        real_tt = timetable.objects.all()
        timetable_deletedx = timetable_deleted.objects.all()
        timetable_customx = timetable_custom.objects.all()
        timetable_default_customx = timetable_default_custom.objects.all()
        
        return render(request,'coordinator_time_table_regular.html',{'data':data,'time_table':time_table,'real_time_table':real_tt,"timetable_default_custom" : timetable_default_customx,"timetable_custom":timetable_customx,"timetable_deleted" : timetable_deletedx})
    else:
        return HttpResponseRedirect("/")
    

def coordinator_time_table_regular_save(request):
    xuser = request.user
    if(xuser.is_authenticated and xuser.groups.filter(name='coordinator').exists()):
        data = request.POST['corex']
        custom_qq = request.POST['coreq'].split(":$:")
        datez = request.POST['corey'].split(",")
        erased_data = request.POST['corez'].split(":$:")
        for z in range(0,len(erased_data)-1):
            erased = erased_data[z].split(":)")
            tempy = timetable_default_custom.objects.filter(date_c  = datez[1], start_time=erased[0],end_time =erased[1],room = erased[2])
            if(tempy.exists()):
                tempy.delete()  #try to continue loop if this satisfies.
            tempy = timetable_custom.objects.filter(date_c  = datez[1], start_time_c=erased[0],end_time_c=erased[1],room_c = erased[2])
            if(tempy.exists()):
                tempy.delete()
            tempx = timetable.objects.filter(day = datez[0], start_time=erased[0],end_time =erased[1],room = erased[2])
            if(tempx.exists()):
                tempy = timetable_deleted(timetable_reference = tempx[0], date_c = datez[1])
                tempy.save()

        for z in range(0,len(custom_qq)-1):
            custom_q = custom_qq[z].split(":)")
            tempy = timetable_default_custom.objects.filter(date_c  = datez[1], start_time=custom_q[2],room = custom_q[4])
            if(tempy.exists()):
                tempy.delete()
            tempy = timetable_custom.objects.filter(date_c  = datez[1], start_time_c=custom_q[2],room_c = custom_q[4])
            if(tempy.exists()):
                tempy.delete()
            tempx = timetable.objects.filter(day = datez[0], start_time=custom_q[2],room = custom_q[4])
            if(tempx.exists()):
                tempy = timetable_deleted(timetable_reference = tempx[0], date_c = datez[1])
                tempy.save()
            tempy = timetable_custom(sub_name_c=custom_q[0],start_time_c=custom_q[2],end_time_c=custom_q[3],room_c=custom_q[4],date_c=datez[1],description_c =custom_q[1])
            tempy.save()

        #subject_name, course , Sem, Div, start_time, end_time, room, batch
        data = data.split(":$:")
        for x in range(0,len(data)-1):
            x = data[x].split(":)")
            x.append(x[1][-9::1])
            x[1] = x[1].replace(" " + x[7],"")
            course_data = courses.objects.get(batch = x[7],c_name = x[1])
            xsemester = semester.objects.get(course =course_data, sem = x[2])
            xsubject_data = subject.objects.get(div_group=x[3],sub_name = x[0],sem_course=xsemester)
            tempx = timetable.objects.filter(day = datez[0], start_time=x[4],end_time =x[5],room = x[6])
            if(tempx.exists()):
                tempy = timetable_deleted(timetable_reference = tempx[0], date_c = datez[1])
                tempy.save()
            tempy = timetable_default_custom.objects.filter(date_c  = datez[1], start_time=x[4],end_time =x[5],room = x[6])
            if(tempy.exists()):
                tempy.delete()
            tempy = timetable_custom.objects.filter(date_c  = datez[1], start_time_c=x[4],end_time_c=x[5],room_c = x[6])
            if(tempy.exists()):
                tempy.delete()


            data_tt = timetable_default_custom(subject_reference=xsubject_data ,start_time=x[4],end_time =x[5],room =x[6],date_c = datez[1])
            data_tt.save()

        return HttpResponseRedirect("/home/coordinator/timetable/regular")
    else:
        return HttpResponseRedirect("/")


def coordinator_attendance(request):
    xuser = request.user
    if(xuser.is_authenticated and xuser.groups.filter(name='coordinator').exists()):
        data = {'name':"Crd " + xuser.first_name + " " + xuser.last_name}
        return render(request,'coordinator_attendance.html',{'data':data})
    else:
        return HttpResponseRedirect("/")

face_dic = {}

def get_face_enco(path, var_x):
    with open(path, 'rb') as f:
        face_dic[var_x] = pickle.load(f)
        
#TAKE attendace
def take_attendace(request,sub):
    xuser = request.user
    if(xuser.is_authenticated and xuser.groups.filter(name='student').exists()):
        data = student_data.objects.get(email=str(xuser))
        t = data.course.c_name + " " + data.course.batch
        get_face_enco(os.path.join(r"media/imp",t + ".dat"),t)
        sub = sub.split(":)")[1]
        cc = t
    elif(xuser.is_authenticated and xuser.groups.filter(name='faculty').exists()):
        sub = sub.split(":)")[1]
        temp = subject.objects.get(id=sub).sem_course
        t  = temp.course.c_name + " " + temp.course.batch
        get_face_enco(os.path.join(r"media/imp",t + ".dat"),t)
        data = teacher_data.objects.get(email=str(xuser))
        cc = t
    else:
        return HttpResponseRedirect("/")

    
    
    my_d = datetime.now()
    myday = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday','Sunday'][my_d.weekday()]
    date_m = " " +str(my_d.day) + " " +  ['','January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][my_d.month] + " "  + str(my_d.year)
    timetable_d = timetable.objects.filter(subject_reference = sub, day = myday)
    timetable_d_c = timetable_default_custom.objects.filter(subject_reference = sub,date_c = date_m )
    timetable_d_removed = timetable_deleted.objects.filter(timetable_reference__in = timetable_d)
    l=[]
    for x in timetable_d_removed:
        l.append(x.timetable_reference.id)
    timetable_d = timetable_d.exclude(id__in = l)
 
    return render(request,'take_attendance.html',{"data":data,"timetable_d":timetable_d,"timetable_d_c":timetable_d_c,"cc":cc})


def img_upload(request):
    xuser = request.user
    if(xuser.is_authenticated and xuser.groups.filter(name='student').exists()):
        data = student_data.objects.get(email=str(xuser))
        data.train_image.delete()
        img = request.FILES['image_x']  
        data.train_image = img
        data.save()
        return HttpResponseRedirect('/')
        
    else:
        return HttpResponseRedirect('/')

def train(request): #update face_dic also
    xuser = request.user
    if(xuser.is_authenticated and xuser.groups.filter(name='coordinator').exists()):
        dir = r'media/train'
        for i in os.listdir(dir):
            encodings = []
            lables = [] 
            dir_c = os.path.join(dir,i)
            for j in os.listdir(dir_c):
                label = j[0:-4]
                img = face_recognition.load_image_file(os.path.join(dir_c,j))

                faceloc = face_recognition.face_locations(img)    
                if(len(faceloc)==1):
                    face_encode = face_recognition.face_encodings(img,faceloc)[0] 
                    encodings.append(face_encode)
                    lables.append(label)

            dir_x = r"media/imp"        
            all_face_encodings= []
            all_face_encodings.append(encodings)
            all_face_encodings.append(lables)

            with open(os.path.join(dir_x,i)+".dat", 'wb') as f:
                pickle.dump(all_face_encodings, f) 

        return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")
        
def get_img(request): #add module for attendace through excel submission
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data_from_post = json.load(request)['post_data']
        course_x = request.headers.get('Course')
        id_a = request.headers.get('id').split(":)")
        id_z = id_a[0]
        marked_on_x = id_a[1]
        marker = id_a[2]
        img = cv.imdecode(np.fromstring(base64.b64decode(data_from_post), dtype=np.uint8),cv.IMREAD_UNCHANGED)
        temp = face_dic[course_x]
        #main processing
        test_faceloc = face_recognition.face_locations(img)    
        test_face_encode = face_recognition.face_encodings(img,test_faceloc)
        temp_x = "No Face Found"
        for test_enco in test_face_encode:
            matches = face_recognition.compare_faces(temp[0],test_enco)
            face_dis = face_recognition.face_distance(temp[0],test_enco)
            matchindex = np.argmin(face_dis) 

            if(matches[matchindex]):
                temp_x = temp[1][matchindex]
                stud =student_data.objects.get(prn = temp_x)
                sub_j = subject.objects.get(id =id_z)
                if(sub_j.last_modified != marked_on_x):
                    sub_j.count = str(int(sub_j.count) + 1)
                    sub_j.last_modified = marked_on_x
                    sub_j.last_modified_by = marker
                    sub_j.save()
                if(sub_j.teacher_reference.email == marker):
                    pass
                elif(sub_j.last_modified_by != marker):
                    temp_x = "Access Denied"
                    break
                try:
                    d = attendance.objects.get(stud_reference = stud,subject = sub_j)
                    if(d.marked_on != marked_on_x):
                        d.attendance_count = str(int(d.attendance_count) + 1)
                        d.marked_on = marked_on_x
                        d.save()
                    else:
                        temp_x = "@"+ temp_x + " " + "Already Done"
                        

                except(Exception):
                    if((sub_j.div_group == stud.div) or (student_sub_elective.objects.filter(stud_reference = stud, subject_reference= sub_j).exists())):
                        d = attendance(stud_reference = stud,subject = sub_j,attendance_count = "1")
                        d.marked_on = marked_on_x

                        d.save()
                    else:
                        temp_x = "Doesn't belong here"
            else:
                temp_x = "Unknown"
    
        ################

        data = {
                'my_data':temp_x
            }
        return JsonResponse(data)

def inquiry_z(request):
    xuser = request.user
    if(xuser.is_authenticated):
        #All
        #course_contact
        #subject_contact

        if(xuser.groups.filter(name='student').exists()):
            data = student_data.objects.get(email=str(xuser))
            # course_contact = [(str(data.course),data.course.id)]
            course_contact = courses.objects.filter(id = data.course.id).values_list("c_name","batch","id")
  
            l =student_sub_elective.objects.filter(stud_reference = data).values_list("subject_reference",flat=True)
            subject_contact = (subject.objects.filter(sem_course = semester.objects.get(course = data.course), div_group = data.div) | subject.objects.filter(id__in = l)).values_list("sub_name","id")
        elif(xuser.groups.filter(name='faculty').exists()):

            data = teacher_data.objects.get(email=str(xuser))
            subject_contact = []
            course_contact = courses.objects.all().values_list("c_name","batch","id")

            temp = subject.objects.filter(teacher_reference = data).values_list("sub_name","div_group","id")
            for x in range(0,len(temp)):
                subject_contact.append((temp[x][0],temp[x][2], " @"+temp[x][1]))

        elif(xuser.groups.filter(name='coordinator').exists()):

            data = {'name':"Crd " + xuser.first_name + " " + xuser.last_name}
        else:
            return HttpResponseRedirect("/")

    else:
        return HttpResponseRedirect("/")

    return render(request,'inquiry.html',{'data':data,"course_contact":course_contact,"subject_contact":subject_contact})

def get_inquiry(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data_from_post = json.load(request)['post_data']
        temp = ""
        try:
            temp = list(inquiry.objects.filter(contacts_i = inquiry_contacts_i.objects.get(group_name = data_from_post)).values())
            
        except(Exception):
            pass
        data = {
                'my_data':temp
            }
        return JsonResponse(data)

def set_inquiry(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data_from_post = json.load(request)['post_data']
        #email, text, time, date, id
        temp = data_from_post.split(":)")
        temp_d = inquiry_contacts_i.objects.get_or_create(group_name = temp[4])
        temp_i = inquiry(email_from  = temp[0],text_i = temp[1], time_i = temp[2], date_i = temp[3], contacts_i  =temp_d[0])
        temp_i.save()

        data = {
                'my_data':"saved"
            }
        return JsonResponse(data)
    
#COMPLAIN
def complain_form(request):
    xuser = request.user
    if(xuser.is_authenticated):
        if(xuser.groups.filter(name='student').exists()):
            data = student_data.objects.get(email=str(xuser))
        elif(xuser.groups.filter(name='faculty').exists()):
            data = teacher_data.objects.get(email=str(xuser))
        else:
            return HttpResponseRedirect("/")

    else:
        return HttpResponseRedirect("/")
    complains = complain.objects.filter(to_email = data.email) | complain.objects.filter(from_email_hidden = data.email)
    return render(request,"complain.html",{'data':data,'complains':complains})

def save_complain_form(request):
    xuser = request.user
    if(xuser.is_authenticated):
        if(xuser.groups.filter(name='student').exists() or xuser.groups.filter
            (name='faculty').exists()):
            subject_c = request.POST['subject_c']
            against_c = request.POST['against_c']
            text_c = request.POST['text_c']
            date_c = request.POST['date_c']
            to_email = request.POST['to_email']
            data = complain(from_email_hidden = str(xuser), subject_c = subject_c, against_c = against_c, text_c = text_c, date_c = date_c, to_email = to_email)
            data.save()
        else:
            return HttpResponseRedirect("/")

    else:
        return HttpResponseRedirect("/")
    return HttpResponseRedirect("/")

#NOTES
def notes(request):
    xuser = request.user
    if(xuser.is_authenticated):
        if(xuser.groups.filter(name='student').exists()):
            data = student_data.objects.get(email=str(xuser))
            temp_l = student_sub_elective.objects.filter(stud_reference = data).values_list("subject_reference",flat=True)
            all_sub = subject.objects.filter(sem_course = semester.objects.get(course = data.course), div_group = data.div) | subject.objects.filter(id__in = temp_l)
            notes_x = notes_d.objects.filter(sub_n__in = all_sub)
            return render(request,"notes.html",{"data":data,"all_sub":all_sub,"notes_x":notes_x})
        
        elif(xuser.groups.filter(name='faculty').exists()):
            data = teacher_data.objects.get(email=str(xuser))
            all_sub = subject.objects.filter(teacher_reference =data )
            notes_x = notes_d.objects.filter(sub_n__in = all_sub)
            return render(request,"notes.html",{"data":data,"all_sub":all_sub,"notes_x":notes_x})
        else:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")

def save_notes(request,sub_id):
    xuser = request.user
    if(xuser.is_authenticated and xuser.groups.filter(name='faculty').exists()):
        doc = request.FILES['notes_file']
        name = request.POST['name']
        data = notes_d(sub_n = subject.objects.get(id = sub_id),file_n = doc, name = name)
        data.save()
        return HttpResponseRedirect("/course material")
    else:
        return HttpResponseRedirect("/")

def delete_notes(request,note_id):
    xuser = request.user
    if(xuser.is_authenticated and xuser.groups.filter(name='faculty').exists()):
        temp = notes_d.objects.get(id = note_id)
        if(temp.sub_n.teacher_reference.email == str(xuser)):
            temp.file_n.delete()
            temp.delete()
        return HttpResponseRedirect("/course material")
    else:
        return HttpResponseRedirect("/")
    
def calendar(request):
    xuser = request.user
    if(xuser.is_authenticated):
        if(xuser.groups.filter(name='student').exists()):
            data = student_data.objects.get(email=str(xuser))
            calendar_x = calendar_d.objects.all()
            return render(request,"calendar.html",{"data":data,"calendar_x":calendar_x})
        
        elif(xuser.groups.filter(name='faculty').exists()):
            data = teacher_data.objects.get(email=str(xuser))           
            calendar_x = calendar_d.objects.all()
            return render(request,"calendar.html",{"data":data,"calendar_x":calendar_x})
        
        elif(xuser.groups.filter(name='coordinator').exists()):
            data = {'name':"Crd " + xuser.first_name + " " + xuser.last_name}
            calendar_x = calendar_d.objects.all()
            return render(request,"calendar_c.html",{"data":data,"calendar_x":calendar_x})
        
        else:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")


def send_mail_password(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data_from_post = (json.load(request)['post_data']).split(",")
  
        email_x =  data_from_post[0]
        xgroup = data_from_post[1]
        temp = User.objects.filter(username = email_x)
        if(temp.exists()) and (temp[0].groups.filter(name = xgroup).exists()):
            UPPERCASE = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'M', 'N', 'O', 'p', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
            LOWERCASE = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',  'i', 'j', 'k', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
            DIGITS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
            SPECIAL = ['@', '#', '$', '=', ':', '?', '.', '/', '|', '~', '>', '*', '<']
            COMBINED_LIST = DIGITS + UPPERCASE + LOWERCASE + SPECIAL
            password = "".join(random.sample(COMBINED_LIST,13))
            temp_otp_d = otp_d.objects.get_or_create(user_o = email_x)
            if(temp_otp_d[1] == False):
                if(temp_otp_d[0].count_o > 2):
                    if(temp_otp_d[0].date_o.date() == datetime.now().date()):
                        data = {'my_data':"count"}
                        return JsonResponse(data)
                    else:
                        temp_otp_d[0].count_o = 0
            temp_otp_d[0].count_o = temp_otp_d[0].count_o + 1
            temp_otp_d[0].otp_o = password
            temp_otp_d[0].date_o = datetime.now()
            temp_otp_d[0].save()
            send_mail('Password Reset (SMS)', "OTP: " + password, 'asianman78607@gmail.com', [email_x])
            data = {
                    'my_data':"yes",
                    'n':temp_otp_d[0].count_o
                }
        else:
            data = {
                    'my_data':"no"
                }
            
        return JsonResponse(data)
        
    else:
        return HttpResponseRedirect("/")
    
def get_mail_password(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data_from_post = (json.load(request)['post_data']).split(",")
  
        otp_x =  data_from_post[0]    
        email_x =  data_from_post[1]    
        print(otp_x,email_x)
        temp  = otp_d.objects.filter(user_o = email_x, otp_o = otp_x)
        if(temp.exists()):
            data = {
                    'my_data':"yes",
                }
        else:
            data = {
                    'my_data':"no",
                }
        return JsonResponse(data)
    else:
        return HttpResponseRedirect("/") #no user
    
def set_password(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data_from_post = (json.load(request)['post_data']).split(",")
  
        p_x =  data_from_post[0]    
        email_x =  data_from_post[1]    
        temp  = User.objects.filter(username = email_x)
        if(temp.exists()):
            temp = User.objects.get(username = email_x)
            temp.set_password(p_x)
            temp.save()
            data = {
                    'my_data':"yes",
                }
        else:
            data = {
                    'my_data':"no",
                }
        return JsonResponse(data)
    else:
        return HttpResponseRedirect("/") #no user
