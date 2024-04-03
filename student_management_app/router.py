from django.urls import path, include

from .api.viewsets import *
from school_apps.courses.api.viewsets import *
# from school_apps.teacher.api.viewsets import *
from school_apps.extrausers.api.viewsets import *
from school_apps.attendance.api.viewsets import *
from school_apps.lms.views import *
from school_apps.spis.views import *
from school_apps.events.api.viewsets import *
from school_apps.logs.api.viewsets import *
from school_apps.inventory.api.viewsets import *
# from school_apps.events.api. import

from school_apps.cafeteria.api.viewsets import *
from school_apps.enquiry.api.viewsets import *
from rest_framework import routers

app_name = 'api'
router = routers.DefaultRouter()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~Student Management App~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
router.register('students', StudentViewSet, basename="Students")
router.register('teachers', TeacherViewset, 'Teachers')
router.register('staffs', StaffViewset, basename="Staffs")
router.register('customusers', CustomUserViewSet, 'Customuser')

router.register('subjects', SubjectViewSet, basename="Subjects")
router.register('subjectteacher', SubjectTeacherViewSet, basename="Subjectteacher")
# router.register('semester', SemesterViewSet, basename="Semester")
# router.register('section', SectionViewSet, "Section")
router.register('department', DepartmentViewSet, 'Department')
router.register('branch', BranchViewSet, 'Branch')
router.register('coursecategory', CourseCategoryViewSet, 'CourseCategory')

router.register('campus', CampusViewSet, 'Campus')
router.register('school', SchoolViewSet, 'School')
router.register('courses', CourseViewSet, 'Course')
router.register('files', DocumentFileViewSet, 'files')
router.register('complaint', ComplainViewSet, 'complain')
router.register('certificatetemplate', CertificateTemplateViewSet, 'certificate-templates')

router.register('batches', BatchViewSet, basename="Batch")
router.register('sessionyear', SessionYearViewSet, basename="SessionYear")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~Courses~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
router.register('terms', TermViewSet, 'terms')
router.register('exams', ExamsViewSet, 'exams')
router.register('application-form', application_formViewSet, 'application-forms')
router.register('studentgrades', studentgradesViewSet, 'studentgrades')
router.register('selectedcourses', selectedcoursesViewSet, 'selectedcourses')


#~~~~~~~~~~~~~~~~~~~~~~~~~~~Cafeteria~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
router.register('ingredients', IngredientViewSet, 'ingredients')
router.register('fooditems',FoodItemViewSet, 'fooditems')
router.register('stalls', StallViewSet,'stalls')
router.register('sales', SalesViewSet, 'sales')
router.register('salesitem', sales_itemViewSet, 'sales_item')
# router.register('ingredientassignments', IngredientAssignmentViewSet, 'ingredientassignment')
router.register('stall-ingredients', stall_ingredients_itemViewSet, 'stall_ingredients')
router.register('menu', MenuViewSet, 'menu')
router.register('menu-items', menu_itemsViewSet, 'menu items')
router.register('cafeteria-staff', CafeteriaStaffViewSet, 'cafeteria-staff')


#~~~~~~~~~~~~~~~~~~~~~~~~~~~Enquiry~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
router.register('enquiry', EnquiryViewSet,'enquiry')
router.register('application', ApplicationViewSet, 'application')
router.register('permissions', PermissionsViewSet, 'permissions')
router.register('groups', GroupViewSet, 'groups')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~Library~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
router.register('book-categories',BookCategoryViewset, 'book_categories')
router.register('books', BookViewset, 'books')
router.register('library',LibraryViewset,'library')
router.register('author',AuthorViewset,'author')
router.register('publication',PublicationViewset,'publication')
router.register('addbook', AddBookViewset, 'addbooks')
router.register('book-issues',BookIssueViewset, 'book_issues')
router.register('book-return',BookReturnViewset, 'book_return')
router.register('fine-payment',FinePaymentViewset, 'fine-payment')
router.register('book-renew', BookRenewViewset, 'book_renew')
router.register('library-profile', LibraryProfileViewset, 'library_profile')
router.register('unique-book', UniqueBookViewset, 'unique_book')
router.register('reserve-book', BookReservationViewset, 'reserve_book')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~Attendance~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
router.register('student-attendance', StudentAttendanceViewSet, 'student_attendance')
router.register('teacher-attendance', TeacherAttendanceViewSet, 'teacher_attendance')
router.register('staff-attendance', StaffAttendanceViewSet, 'staff_attendance')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~SPIS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
router.register('vacancyapi', VacancyViewSet, basename='vacancy')
router.register('vacancyviewapi', VacancyReadOnlyModelViewSet, basename='vacancyview')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~events~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
router.register('events', EventViewSet, 'events')
router.register('event-categories', EventCategoryViewSet, 'event_categories')
router.register('awards', AwardsViewSet, 'awards')
router.register('award-recipients', awards_recipientViewSet, 'awards_recipient')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~logs~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
router.register('logs', UserLogViewSet, 'logs')
router.register('report-logs', ReportLogViewSet, 'report_logs')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~inventory~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
router.register('statusoptions', StatusOptionsViewSet, 'statusoptions')
router.register('category', CategoryViewSet, 'category')
router.register('assets', AssetsViewSet, 'assets')
router.register('vendors', VendorViewSet,'vendors')
router.register('procurement-requests', ProcurementRequestViewSet, 'procurementrequests')
router.register('transactions', TransactionViewSet, 'transactions')
router.register('items', ItemViewSet,'items')



