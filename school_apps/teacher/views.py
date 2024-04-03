
import csv, io
import datetime
from django.contrib import messages
from django.db.models.query import QuerySet
from django.http.response import HttpResponseRedirect, JsonResponse
from django.http.response import HttpResponse
from django.shortcuts import render, get_object_or_404
from school_apps.courses.models import Term, application_form, studentgrades, Exams, Subject, selectedcourses, term_ranking
from student_management_app.models import Student, Staff, CustomUser, SubjectTeacher
from django.urls import reverse
from django.db.models import Q

# def index(request):
#     # if request.method == 'POST':
#     #     request.session['teacherID'] = request.POST['teacherID']
#     teacher = get_object_or_404(Teacher, staff_user = request.user.id)
#     return render (request, 'teacher/index.html', {'teacher':teacher})


def addscore(request):
 
    # teacher = get_object_or_404(Staff, staff_user = request.user.id)
    teacher = get_object_or_404(CustomUser, id = request.user.id)
    print(teacher,'\n')
    staff_user = Staff.objects.get(staff_user=teacher)
    category = staff_user.courses.all()
    print(staff_user,'\n',category,'\n')
    terms = Term.objects.filter(course_category__in = category)
    print(terms)
    today = datetime.date.today()


    print(today)
    if request.method=='GET':
        subject = Subject.objects.all().filter(staff_user=teacher)
        exams = Exams.objects.filter(Q(subject_id__in=subject) & Q(date__lt=today))
        print(exams,"```````````````````````````````````````````")
        return render(request, 'teacher/addscore.html', {'teacher': teacher, 'subject':subject,'exams':exams, 'terms':terms})



def subscore(request):
    teacher = get_object_or_404(CustomUser, id = request.user.id)
    exam_code = request.GET['exam']
    selected_exam = get_object_or_404(Exams, exam_id=exam_code)
    selected_subject=selected_exam.subject_id
    # existing_records = studentgrades.objects.all().filter(exam_id=selected_exam)
    student_data = selectedcourses.objects.all().filter(subject_id = selected_subject)
    
    # form = gradesform()
    context = {'teacher': teacher,  'students':student_data, 'exam':selected_exam}
    return render (request, 'teacher/dump.html', context )

def submitscore(request):
    teacher = get_object_or_404(CustomUser, id = request.user.id)
    exam = get_object_or_404(Exams, exam_id=request.GET['exam_id'])
    selected_subject = exam.subject_id
    print("subject: " + selected_subject.__str__())
    students = studentgrades.objects.filter(exam_id__subject_id=selected_subject)
    # print(list(request.GET.items()))
    
    failed_attempts=[]
    entries=0;
    if (students):
        for student in students:
            try:
                marks=int(request.GET[student.application_id.student.student_user.full_name])
                student.marks = marks
                student.save()
                entries+=1
            except:
                failed_attempts.append(student.application_id.student)
    else:
        print("Error")

    for item in studentgrades.objects.filter(exam_id=exam):
        item.rank = studentgrades.objects.filter(exam_id =exam, marks__gt=item.marks).count()+1
        item.save()
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #term_ranking

    selected_term = exam.term
    term_students = studentgrades.objects.filter(exam_id__term=selected_term)
    
    students_list = application_form.objects.filter(term=selected_term).values_list('student').distinct()

    print('students_list: ', students_list , "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    for item in students_list:
        total_marks = 0
        grades = studentgrades.objects.filter(application_id__student = item, exam_id__term=selected_term)
        print('grades', grades, "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

        for grade in grades:
            total_marks+= grade.marks
        
        obj,created = term_ranking.objects.get_or_create(term=selected_term, student=Student.objects.get(pk=item[0]))
        obj.total_marks=total_marks
        obj.save()

    all_t_ranks = term_ranking.objects.filter(term=selected_term)

    print("\n ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ \n")
    for t_rank in all_t_ranks:
        t_rank.rank = term_ranking.objects.filter(total_marks__gt=t_rank.total_marks).count()+1
        t_rank.save()
        print(t_rank, type(t_rank), t_rank.total_marks, 'rank= ',t_rank.rank, "___________________________________")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    if (len(failed_attempts)==0):
        messages.success(request, "Marks entry for " + str(entries) + " students successful")
        return HttpResponseRedirect(reverse('home'))
        #return HttpResponse("OK")
    else:
        messages.error(request, "Marks entry for " + str(len(failed_attempts)) + " students unsuccessful")
        # return HttpResponse("not ok" + str(len(failed_attempts)))
        return HttpResponseRedirect(reverse('home'))



def studentlist(request):
    teacher = get_object_or_404(CustomUser, id = request.user.id)
    return render (request, 'teacher/studentlist.html', {'teacher':teacher})

    
def checkscore(request):
    teacher = get_object_or_404(CustomUser, id = request.user.id)

    staff_user = Staff.objects.get(staff_user=teacher)
    category = staff_user.courses.all()
    subjects = SubjectTeacher.objects.filter(Q(teacher=teacher) & Q(subject__course_category__in=category)).values_list('subject',flat=True)
    # print(staff_user,'\n',category,'\n')
    # terms = Term.objects.filter(course_category__in = category)
    today = datetime.date.today()
    exams = Exams.objects.all().filter(Q(subject_id__in=subjects) & Q(date__lte=today))

    if request.method=='GET':
        return render(request, 'teacher/checkscore.html', {'exams':exams, 'teacher':teacher})
    else:
        code=1
        selected_exam = get_object_or_404(Exams, exam_id=request.POST['exam_id'])
        studentrecords = studentgrades.objects.filter(exam_id=selected_exam).exclude(marks=-1)
        studentrecords_remaining = studentgrades.objects.filter(exam_id=selected_exam).filter(marks=-1)
        context = {'teacher':teacher,'students':studentrecords, 'exams':exams, 'selected_exam':selected_exam, 'code':code, 'remaining':studentrecords_remaining}
        return render(request, 'teacher/checkscore.html', context)

def examsAjax(request):
    teacher = get_object_or_404(CustomUser, id = request.user.id)
    exam_id = request.GET.get('exam_id')
    selected_exam = get_object_or_404(Exams, exam_id=exam_id)
    subject = selected_exam.subject_id
    subjectobject = SubjectTeacher.objects.filter(teacher=teacher, subject=subject, section__semester=selected_exam.semester)
    section = []

    for item in subjectobject:
        section.append(item.section)
    print("section",section,"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    student_data = studentgrades.objects.filter(Q(exam_id=selected_exam) & Q(application_id__student__section__in=section))

    return render (request, 'teacher/submit_score.html', {'students':student_data, 'exam':selected_exam})

def login(request):
    return render(request, 'teacher/login.html')

def loadExamsAjax(request):
    teacher = get_object_or_404(CustomUser, id = request.user.id)
    term = get_object_or_404(Term, pk=request.GET.get('term_id'))
    subjectteacherlist = SubjectTeacher.objects.filter(teacher=teacher)
    subject = []

    for item in subjectteacherlist:
        subject.append(item.subject)
    today = datetime.date.today()
    print(subject)

    exams = Exams.objects.filter(Q(subject_id__in=subject) & Q(term=term) & Q(date__lte=today))
    return render(request, 'teacher/examslist.html', {'exams':exams})

def exportcsv(request, exam_id):
    selected_exam = get_object_or_404(Exams, exam_id=exam_id)
    student_data = studentgrades.objects.all().filter(exam_id=selected_exam)
    student_data = studentgrades.objects.all().filter(exam_id=selected_exam)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename= "results.csv"'

    writer = csv.writer(response, delimiter=",")
    writer.writerow(['exam_id','application_id', 'name','marks','exam_type'])

    for obj in student_data:
        writer.writerow([obj.exam_id.exam_id, obj.application_id.application_id,obj.application_id.student.student_user.full_name, "", obj.exam_type])
    
    return response

def uploadcsv(request):
    csv_file = request.FILES['file']

    if not csv_file.name.endswith('.csv'):
        messages.error(request, "Invalid file")
    
    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    next(io_string)
    exam_pk = 0

    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
            gradeobj = get_object_or_404(studentgrades, exam_id=column[0], application_id=column[1])
            m_obj = int(column[3])

            if m_obj < -1:
                gradeobj.marks = -1
            elif m_obj > 100:
                gradeobj.marks = 100
            else:
                gradeobj.marks= m_obj
            gradeobj.save()
            exam_pk = column[0]
            
    exam = Exams.objects.get(pk=exam_pk)
    for item in studentgrades.objects.filter(exam_id=exam):
        item.rank = studentgrades.objects.filter(exam_id=exam, marks__gt=item.marks).count()+1
        item.save()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#term_ranking

    exam = Exams.objects.get(pk=exam_pk)
    selected_term = exam.term 
    students_list = application_form.objects.filter(term=selected_term).values_list('student').distinct()

    print('students_list: ', students_list , "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    for item in students_list:
        total_marks = 0
        grades = studentgrades.objects.filter(application_id__student = item, exam_id__term=selected_term)
        print('grades', grades, "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

        for grade in grades:
            total_marks+= grade.marks
        
        obj,created = term_ranking.objects.get_or_create(term=selected_term, student=Student.objects.get(pk=item[0]))
        obj.total_marks=total_marks
        obj.save()

    all_t_ranks = term_ranking.objects.filter(term=selected_term)

    print("\n ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ \n")
    for t_rank in all_t_ranks:
        t_rank.rank = term_ranking.objects.filter(total_marks__gt=t_rank.total_marks).count()+1
        t_rank.save()
        print(t_rank, type(t_rank), t_rank.total_marks, 'rank= ',t_rank.rank, "___________________________________")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    messages.success(request,"Marks upload successful")
    return HttpResponseRedirect(reverse('home'))

def logout(request):
    del request.session['user_id']
    return render (request, "teacher/login.html")

def checksubjects(request):
    self = get_object_or_404(CustomUser, id = request.user.id)
    subjects = SubjectTeacher.objects.filter(teacher=self)

    context={
        'subjects':subjects
    }
    return render(request, 'teacher/checksubjects.html', context)



def checkstudents(request):
    
    self = get_object_or_404(CustomUser, id = request.user.id)
    subjects = SubjectTeacher.objects.filter(teacher=self)

    if request.method == "GET":
        context={
            'subjects':subjects
        }    
        return render(request, 'teacher/checkstudents.html', context)
    else:
        selected_subject=SubjectTeacher.objects.get(pk=request.POST["class_id"])
        students = selectedcourses.objects.filter(subject_id = selected_subject.subject)

        context = {
            'students':students,
            'subjects':subjects
        }
        return render(request, 'teacher/checkstudents.html', context)