from django.urls import path
from .views import RegisterUserView, LoginUserView, ChangePasswordView, ProfileView, EmployeeListView, EmployeeDetailView, CreateFormView, SubmitFormResponseView

urlpatterns = [

    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('profile/', ProfileView.as_view(), name='profile'),


    path('employees/', EmployeeListView.as_view(), name='employee-list'),
    path('employees/<int:pk>/', EmployeeDetailView.as_view(), name='employee-detail'),


    path('form/create/', CreateFormView.as_view(), name='create-form'),
    path('form/<int:form_id>/submit/', SubmitFormResponseView.as_view(), name='submit-form-response'),

]
