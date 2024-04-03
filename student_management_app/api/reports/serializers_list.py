from ..serializers import *
from school_apps.courses.api.serializers import *
from school_apps.events.api.serializers import *
from school_apps.spis.serializers import *
from school_apps.attendance.api.serializers import *
from school_apps.courses.models import selectedcourses, studentgrades
from ...models import SubjectTeacher, Subject

serializers_list = {
    "Branch":BranchSerializer,
    "Student":StudentSerializer,
    "Campus":CampusSerializer,
    "School":SchoolSerializer,
    "Staff":StaffSerializer,
    "ExtraUser":ExtraUserSerializer,
    "Subject":SubjectSerializer,
    "Course":CourseSerializer,
    "Training":TrainingSerializer,
    "Campus":CampusSerializer,
    "School":SchoolSerializer,
    "CourseCategory":CourseCategorySerializer,
    "Department":DepartmentSerializer,
    "Batch":BatchSerializer,
    "CustomUser":CustomUserSerializer,
    "SubjectTeacher":SubjectTeacherSerializer,
    "DocumentFile":DocumentFileSerializer,
    "Awards":AwardsSerializer,
    "awards_recipent":awards_recipientSerializer,
    "Parent":ParentSerializer,
    
    "EducationHistory":EducationHistorySerializer,
    "EmploymentHistory":EmploymentHistorySerializer,
    "ResearchAndConsultancy":ResearchAndConsultancySerializer,
    "GraduateResearchSupervision":GraduateResearchSupervisionSerializer,
    "GraduateProjectSupervision":GraduateProjectSupervisionSerializer,
    "WorkshopSeminarConference":WorkshopSeminarConferenceSerializer,
    "FellowshipAwardsStudyvisit":FellowshipAwardsStudyvisitSerializer,
    "PublicationAndCopyrights":PublicationAndCopyrightsSerializer,

    "Permission":PermissionSerializer,
    "Group":GroupSerializer,

    "Term":TermSerializer,
    "Exams":ExamsSerializer,
    "application_form":application_formSerializer,
    "studentgrades":studentgradesSerializer,
    "term_ranking":term_rankingSerializer,
    "selectedcourses":selectedcoursesSerializer,
    
    "EventCategory":EventCategorySerializer,
    "Event":EventSerializer,
    "event_participants":event_participantsSerializer,
    
    "Vacancy":VacancySerializer,
    
    "StudentAttendance":StudentAttendanceSerializer,
    "TeacherAttendance":TeacherAttendanceSerializer,
    "StaffAttendance":StaffAttendanceSerializer

}

ranges_list = {
    "Student":["dob"],
    "Staff":["dob", "join_date"],
    "ExtraUser":["dob", "join_date"],
    "Subject":["semester"],
    "Term":["start_date", "end_date"],
    "Exams":["date", "semester"],
    "application_form":["application_date"],
    "studentgrades":["marks", "rank"],
    "Event":["start_date", "end_date"],
    "StudentAttendance":["attendance_date"],
    "TeacherAttendance":["attendance_date"],
    "StaffAttendance":["attendance_date"],
}

additional_fields = {
    "Student":[
        {
            "model":selectedcourses,
            "name":"selectedcourses",
            "queries":['selectedcourses'],
            "display_name":"Selected Courses",
            "is_relation":True,
            "field":"ForeignKey",
            "fk_field":"subject_id_id",
            "fk_dropdown":Subject,
            "object_field":"student_id"
        }
    ],
    "Exams":[
        {
            "model":studentgrades,
            "name":"studentgrades",
            "queries":['studentgrades', 'studentgrades__gte', 'studentgrades__lte'],
            "display_name":"Marks",
            "is_relation":False,
            "field":"IntegerField",
            "fk_field":"marks"
        }
    ],
    "Staff":[
        {
            "model":SubjectTeacher,
            "name":"SubjectTeacher",
            "display_name":"Subject",
            "is_relation":True,
            "field":"ForeignKey",
            "fk_field":"subject_id",
            "fk_dropdown":Subject,
            "object_field":"teacher"
        }
    ],
    "Subject":[
        {
            "model":SubjectTeacher,
            "name":"SubjectTeacher",
            "display_name":"Subject",
            "relation":True,
            "field":"ForeignKey",
            "fk_field":"teacher_id",
            "fk_dropdown":Staff,
            "object_field":"subject"
        }
    ]
}

csv_fields ={
    "CourseCategory":"course_name",
    "Course":"course_name",
    "Subject":"subject_code",
    "Batch":"year"
}