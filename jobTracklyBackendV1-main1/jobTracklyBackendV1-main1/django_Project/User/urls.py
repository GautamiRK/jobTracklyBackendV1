from django.urls import path
from .views import (
    UserRegistrationView, 
    LoginView, 
    CreateJobApplicationView, 
    GetUserApplicationsView
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', LoginView.as_view(), name='user-login'),
    path('addeditjobdetails/', CreateJobApplicationView.as_view(), name='add-edit_job_details'),
    path('getjobdetails/', GetUserApplicationsView.as_view(), name='get-user-applications'),
] 