from django.urls import path
from .apiviews import DepartmentList, DepartmentDetail, TicketList, TicketDetail, FormList, FormDetail
from .views import DepartmentListView, DepartmentDetailView, DepartmentAddView, DepartmentEditView, DepartmentDeleteView,TicketListView, TicketAddView, TicketDetailView, TicketEditView, TicketDeleteView, PrintFormView

urlpatterns = [
    # API url start
    path('api/department/', DepartmentList.as_view(), name = 'api-department-list'),
    path('api/department/<int:id>/', DepartmentDetail.as_view(), name = 'api-department-detail'),
    path('api/form/', FormList.as_view(), name = 'api-form-list'),
    path('api/form/<int:id>/', FormDetail.as_view(), name = 'api-form-detail'),
    path('api/ticket/', TicketList.as_view(), name = 'api-ticket-list'),
    path('api/ticket/<int:id>/', TicketDetail.as_view(), name = 'api-ticket-detail'),
    # API url end

    path('printform/', PrintFormView.as_view(), name = 'ticket-printform'),

    path('department/add/', DepartmentAddView.as_view(), name = 'department-add'),
    path('department/edit/<int:id>/', DepartmentEditView.as_view(), name = 'department-edit'),
    path('department/delete/<int:id>/', DepartmentDeleteView.as_view(), name = 'department-delete'),
    path('department/', DepartmentListView.as_view(), name = 'department-list'),
    path('department/<int:id>/', DepartmentDetailView.as_view(), name = 'department-detail'),

    path('ticket/', TicketListView.as_view(), name = 'ticket-list'),
    path('ticket/<int:id>/', TicketDetailView.as_view(), name = 'ticket-detail'),
    path('ticket/edit/<int:id>/', TicketEditView.as_view(), name = 'ticket-edit'),
    path('ticket/delete/<int:id>/', TicketDeleteView.as_view(), name = 'ticket-delete'),
]