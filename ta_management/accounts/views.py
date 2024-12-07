from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from .forms import CustomUserCreationForm
from django.contrib.auth import logout  # Import the logout function


def home(request):
    return render(request, 'accounts/home.html')


def signup(request, role):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = role  # Assign the role selected during signup
            user.save()
            return redirect('login', role=role)
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'role': role, 'form': form})


from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

User = get_user_model()

def role_login(request, role):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Check if the user's role matches the selected role
            if user.role == role:
                auth_login(request, user)
                # Redirect based on the user's role
                if role == 'ta_applicant':
                    return redirect('ta_applicant_dashboard')
                elif role == 'department_staff':
                    return redirect('department_staff_dashboard')
                elif role == 'ta_committee':
                    return redirect('ta_committee_dashboard')
                elif role == 'instructor':
                    return redirect('instructor_dashboard')
            else:
                form.add_error(None, "Invalid role for this user.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'role': role, 'form': form})


def forgot_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            # Redirect to the reset password page with the role as a query parameter
            return redirect('reset_password', role=user.role)
        except User.DoesNotExist:
            error = "User does not exist"
            return render(request, 'accounts/forgot_password.html', {'error': error})
    return render(request, 'accounts/forgot_password.html')

from django.contrib.auth.forms import SetPasswordForm

def reset_password(request, role):
    if request.method == 'POST':
        form = SetPasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            # Redirect to the login page with the role after successful password reset
            return redirect('login', role=role)
    else:
        form = SetPasswordForm(request.user)

    return render(request, 'accounts/reset_password.html', {'form': form, 'role': role})


# Role-based dashboards after login
from .forms import ApplicationForm
from .models import User, Application

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Application
from .forms import ApplicationForm

@login_required
def ta_applicant_dashboard(request):
    return render(request, 'accounts/ta_applicant_dashboard.html')

def submit_application(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            form.save_m2m()  # Save Many-to-Many relationships
            
            messages.success(request, "Track your submitted application!")
            return redirect('submit_application')
    else:
        form = ApplicationForm()

    return render(request, 'accounts/submit_application.html', {
        'form': form,
    })

def track_applications(request):
    applications = Application.objects.filter(user=request.user)
    return render(request, 'accounts/track_applications.html', {
        'applications': applications,
    })

from .forms import ApplicationForm, OfferResponseForm
from django.http import HttpResponse
from .models import Application

# New view for responding to offer
def respond_to_offer(request):
    application = Application.objects.filter(user=request.user, ta_committee_status='approved').first()

    if not application:
        return render(request, 'accounts/respond_to_offer.html', {
            'message': "You have no approved applications to respond.",
        })

    if application.ta_applicant_response:  # If a response has already been given
        response = application.ta_applicant_response.title() if application.ta_applicant_response else "No response"
        return render(request, 'accounts/respond_to_offer.html', {
            'message': f"Your response: {response} has already been recorded.",
            'application': application,  # Include the application for context
        })
    
    if request.method == 'POST':
        form = OfferResponseForm(request.POST, instance=application)
        if form.is_valid():
            response = form.cleaned_data['ta_applicant_response']
            form.save()
            messages.success(request, "Your response: {response.title()} has been recorded.")
            # Render the page with the submitted response
            return render(request, 'accounts/respond_to_offer.html', {
                'message': f"Your response: {response.title()} has been recorded.",
                'application': application,  # Include the application for context
            })
    else:
        form = OfferResponseForm(instance=application)

    return render(request, 'accounts/respond_to_offer.html', {
        'form': form,
        'application':application
    })



from .forms import ApplicationForm
from .models import User, Application, Course
from django.shortcuts import render, get_object_or_404
from .models import Application

# Department Staff Dashboard - Display and manage courses
from django.shortcuts import render, redirect
from .models import Course

def department_staff_dashboard(request):
    # Ensure only department staff can access this page
    if request.user.role != 'department_staff':
        return redirect('home')
    
    # Handle form submission
    if request.method == 'POST':
        if 'add_course' in request.POST:
            course_name = request.POST.get('course_name').strip()
            if course_name:
                if not Course.objects.filter(name=course_name).exists():
                    Course.objects.create(name=course_name, description='')  
            
        elif 'remove_course' in request.POST:
            course_id = request.POST.get('course_id')
            if course_id:
                Course.objects.filter(id=course_id).delete()  # Remove course 
    
    # Get all courses
    courses = Course.objects.all()

    return render(request, 'accounts/department_staff_dashboard.html', {'courses': courses})


# Department Staff - View applications of TA applicants
def department_staff_view_applications(request):
    if request.user.role != 'department_staff':
        return redirect('home')

    # Fetch applications based on recommendation status
    non_recommended_applications = Application.objects.filter(recommended_to_ta_committee=False)
    forwarded_applications = Application.objects.filter(recommended_to_ta_committee=True)

    return render(request, 'accounts/department_staff_view_applications.html', {
        'non_recommended_applications': non_recommended_applications,
        'forwarded_applications': forwarded_applications
    })


# Department Staff - View individual application details
from django.shortcuts import get_object_or_404

def department_staff_view_application_details(request, application_id):
    if request.user.role != 'department_staff':
        return redirect('home')  # Redirect to home if not department staff
    
    # Get the application by ID or show 404 if it doesn't exist
    application = get_object_or_404(Application, id=application_id)
    
    # Render the application details page
    return render(request, 'accounts/department_staff_view_application_details.html', {
        'full_name': application.full_name,
        'z_number': application.z_number,
        'previous_experience': application.previous_experience,
        'status': application.status,  # You can pass the status as well
        'courses': application.courses.all(),  # Courses applied for  # Pass the application details
        'resume': application.resume  # Include the resume URL if it exists
    })

# Department Staff - Recommend applications to TA Committee
def department_staff_recommend_application(request, application_id):
    if request.user.role != 'department_staff':
        return redirect('home')  # Redirect to home if not department staff

    application = Application.objects.get(id=application_id)
    application.recommended_to_ta_committee = True
    application.save()

    return redirect('department_staff_forwarded_applications')

# Forwarded Applications Tab
def department_staff_forwarded_applications(request):
    if request.user.role != 'department_staff':
        return redirect('home')

    # Get applications forwarded to the TA Committee
    applications = Application.objects.filter(recommended_to_ta_committee=True).select_related('user')

    return render(request, 'accounts/department_staff_forwarded_applications.html', {'applications': applications})


from django.core.mail import send_mail
from django.conf import settings
from .models import PerformanceEvaluation, Application, User

# Department Staff View for Performance Metrics
def department_staff_performance(request):
    if request.user.role != 'department_staff':
        return redirect('home')  # Redirect to home if not Department Staff

    # Fetch all performance evaluations
    evaluations = PerformanceEvaluation.objects.all().order_by('-submitted_at')

    if request.method == 'POST':
        evaluation_id = request.POST.get('evaluation_id')
        action = request.POST.get('action')

        try:
            evaluation = PerformanceEvaluation.objects.get(id=evaluation_id)
            application = evaluation.application
            ta_applicant = application.user

            if action == 'send_email':
                if evaluation.decision == 'approved':
                    subject = f"TA Performance: {ta_applicant.username} Approved"
                    message = f"Dear {ta_applicant.username},\n\nYour performance as a TA has been good. Please submit an application to continue further."
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [ta_applicant.email]
                    )
                    application.status_notified = True  # Set this field if you have it
                    application.save()
                    return redirect('department_staff_performance')  # Redirect after sending email
        except PerformanceEvaluation.DoesNotExist:
            pass

    return render(request, 'accounts/department_staff_performance.html', {
        'evaluations': evaluations
    })


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .forms import TAAssignmentForm
from .models import Application, TAAssignment
from .models import PerformanceEvaluation
from django.http import HttpResponse
from django.db.models import Q

@login_required
def ta_committee_dashboard(request):
    if request.user.role != 'ta_committee':
        return redirect('home')  # Redirect to home if not TA Committee

    # Fetch all courses for the filter dropdown
    all_courses = Course.objects.all()

    # Get selected course ID from the query parameters
    selected_course_id = request.GET.get('course')

    # Filter applications based on selected course
    if selected_course_id:
        applications = Application.objects.filter(
            recommended_to_ta_committee=True,
            courses__id=selected_course_id
        ).distinct()
    else:
        applications = Application.objects.filter(recommended_to_ta_committee=True)

    # Filter assignments based on selected course
    if selected_course_id:
        assignments = TAAssignment.objects.filter(course__id=selected_course_id)
    else:
        assignments = TAAssignment.objects.all()

    # Filter performance evaluations based on selected course
    if selected_course_id:
        evaluations = PerformanceEvaluation.objects.filter(application__courses__id=selected_course_id).order_by('-submitted_at')
    else:
        evaluations = PerformanceEvaluation.objects.order_by('-submitted_at')

    if request.method == "POST":
        # Handle approve/reject action
        evaluation_id = request.POST.get('evaluation_id')
        decision = request.POST.get('decision')
        try:
            evaluation = PerformanceEvaluation.objects.get(id=evaluation_id)
            if decision in ['approved', 'rejected']:
                evaluation.decision = decision
                evaluation.save()

                # Update the Application status based on the decision
                application = evaluation.application
                if decision == 'approved':
                    application.status = 'approved'
                    application.ta_committee_status = 'approved'
                else:
                    application.status = 'rejected'
                    application.ta_committee_status = 'rejected'
                application.save()

                # Return success response
                return redirect('ta_committee_dashboard')
        except PerformanceEvaluation.DoesNotExist:
            return HttpResponse("Evaluation not found.", status=404)

    return render(request, 'accounts/ta_committee_dashboard.html', {
        'applications': applications,
        'evaluations': evaluations,
        'assignments': assignments,
        'all_courses': all_courses,
        'selected_course_id': selected_course_id,
    })

@login_required
def assign_ta_to_course(request, application_id):
    if request.user.role != 'ta_committee':
        return redirect('home')

    application = get_object_or_404(Application, id=application_id)
    available_courses = Course.objects.all()  # Get courses managed by Department Staff

    if request.method == 'POST':
        course_id = request.POST.get('course')
        course = get_object_or_404(Course, id=course_id)

        # Create a TA Assignment
        TAAssignment.objects.create(ta=application.user, course=course, ta_committee=request.user)

        # Update application status
        application.ta_committee_status = 'approved'
        application.save()

        # Redirect with success message
        messages.success(request, f"{application.full_name} has been assigned to {course.name}.")
        return redirect('ta_committee_dashboard')

    return render(request, 'accounts/assign_ta_to_course.html', {
        'application': application,
        'available_courses': available_courses,
    })


# View Application Details
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

def ta_committee_view_application_details(request, application_id):
    if request.user.role != 'ta_committee':
        messages.error(request, "You do not have permission to view this application.")
        return redirect('home')

    application = get_object_or_404(Application, id=application_id)

    # Check if the application is already reviewed
    if application.ta_committee_status in ['approved', 'rejected']:
        messages.info(request, "This application has already been processed.")
        return render(request, 'accounts/ta_committee_view_application_details.html', {
            'application': application
        })

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['approved', 'rejected']:
            application.ta_committee_status = new_status
            application.save()
            # Redirect to the TA Committee dashboard with success message
            messages.success(request, f"Application has been {new_status}.")
            return redirect('ta_committee_dashboard')

    return render(request, 'accounts/ta_committee_view_application_details.html', {
        'application': application
    })



from .models import Course, TAAssignment
from .models import Application, Course, PerformanceEvaluation
from django.utils.timezone import now


@login_required
def instructor_dashboard(request):
    # Get all courses that the instructor is associated with
    courses = Course.objects.all()

    selected_course_id = request.GET.get('course_filter')  # Get the selected course filter from query params

    if selected_course_id:
        # Filter applications by selected course
        applications = Application.objects.filter(courses__id=selected_course_id)
    else:
        # If no course is selected, show all applications
        applications = Application.objects.all()

    return render(request, 'accounts/instructor_dashboard.html', {
        'courses': courses,
        'selected_course_id': selected_course_id,
        'applications': applications,
    })

def provide_feedback(request, application_id):
    application = get_object_or_404(Application, id=application_id)

    # Check if feedback already exists for this application by this instructor
    feedback_exists = PerformanceEvaluation.objects.filter(
        instructor=request.user,
        application=application
    ).first()

    if request.method == 'POST' and not feedback_exists:
        feedback = request.POST.get('feedback')
        rating = request.POST.get('rating')

        # Save performance evaluation
        PerformanceEvaluation.objects.create(
            instructor=request.user,
            application=application,
            feedback=feedback,
            rating=rating,
            decision='pending'
        )

        return render(request, 'accounts/provide_feedback.html', {'success_message': 'Feedback submitted successfully!', 'feedback_submitted': True,'feedback_data': {'rating': rating, 'feedback': feedback}})
    #If feedback already exists, show the existing feedback
    if feedback_exists:
        return render(request, 'accounts/provide_feedback.html', {
            'feedback_submitted': True,
            'feedback_data': {'rating': feedback_exists.rating, 'feedback': feedback_exists.feedback}
        })
    
    return render(request, 'accounts/provide_feedback.html', {'application': application,'feedback_submitted': feedback_exists})



@login_required
def custom_logout(request):
    logout(request)
    return redirect('/')



from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages
from .models import Application

def notify_application(request, application_id):
    try:
        application = Application.objects.get(id=application_id)
        recipient_email = application.user.email

        if not recipient_email:
            raise ValueError("No email associated with the user.")

        # Update the application and user statuses
        application.status = application.ta_committee_status  # Update application status
        application.user.application_status = application.ta_committee_status  # Update user's dashboard status
        application.status_notified = True
        application.user.save()
        application.save()

        # Send the email
        send_mail(
            'TA Committee Decision',
            f"Dear {application.full_name}, your application status is: {application.ta_committee_status}.",
            settings.DEFAULT_FROM_EMAIL,  # Use email from settings
            [recipient_email],
        )

        messages.success(request, f"Notification sent to {recipient_email}.")
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")

    return redirect('department_staff_forwarded_applications')


def accept_reject_offer(request, application_id):
    if request.method == "POST":
        application = get_object_or_404(Application, id=application_id)

        if application.user != request.user:
            messages.error(request, "You are not authorized to modify this application.")
            return redirect('ta_applicant_dashboard')

        response = request.POST.get('response')
        if response not in ['accepted', 'rejected']:
            messages.error(request, "Invalid response.")
            return redirect('ta_applicant_dashboard')

        application.ta_applicant_response = response
        application.save()

        messages.success(request, f"You have successfully {response} the offer.")
        return redirect('ta_applicant_dashboard')
