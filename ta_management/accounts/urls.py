from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='home'),
    path('signup/<str:role>/', views.signup, name='signup'),  # Separate signup URL for each role
    path('login/<str:role>/', views.role_login, name='login'),  # Separate login URL for each role
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:role>/', views.reset_password, name='reset_password'),

    path('ta_applicant_dashboard/', views.ta_applicant_dashboard, name='ta_applicant_dashboard'),
    path('ta_applicant_dashboard/submit_application/', views.submit_application, name='submit_application'),
    path('ta_applicant_dashboard/track_applications/', views.track_applications, name='track_applications'),
    path('ta_applicant_dashboard/respond_to_offer/', views.respond_to_offer, name='respond_to_offer'),  # New URL

    path('ta_committee_dashboard/', views.ta_committee_dashboard, name='ta_committee_dashboard'),
    path('assign_ta_to_course/<int:application_id>/', views.assign_ta_to_course, name='assign_ta_to_course'),

    path('logout/', views.custom_logout, name='logout'),
    path('department_staff/dashboard/', views.department_staff_dashboard, name='department_staff_dashboard'),
    path('department_staff/view-applications/', views.department_staff_view_applications, name='department_staff_view_applications'),
    path('department_staff/recommend/<int:application_id>/', views.department_staff_recommend_application, name='department_staff_recommend_application'),
    path('department_staff/view-application-details/<int:application_id>/', views.department_staff_view_application_details, name='department_staff_view_application_details'),
    path('department_staff/forwarded-applications/', views.department_staff_forwarded_applications, name='department_staff_forwarded_applications'),
    path('department_staff/view-performance/', views.department_staff_performance, name='department_staff_performance'),

    path('ta_committee/dashboard/', views.ta_committee_dashboard, name='ta_committee_dashboard'),
    path('ta_committee/view_application/<int:application_id>/', views.ta_committee_view_application_details, name='ta_committee_view_application_details'),
    path('notify_application/<int:application_id>/', views.notify_application, name='notify_application'),
    path('accept_reject_offer/<int:application_id>/', views.accept_reject_offer, name='accept_reject_offer'),

    
    path('instructor_dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('provide_feedback/<int:application_id>/', views.provide_feedback, name='provide_feedback'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)