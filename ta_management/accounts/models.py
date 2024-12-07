from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.

class User(AbstractUser):
    ROLE_CHOICES = [
        ('ta_applicant', 'TA Applicant'),
        ('department_staff', 'Department Staff'),
        ('ta_committee', 'TA Committee'),
        ('instructor', 'Instructor'),
    ]
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='ta_applicant')

    is_application_submitted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username


class Course(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()  # Add description field
    instructor = models.ForeignKey(
            User, 
            on_delete=models.CASCADE, 
            limit_choices_to={'role': 'instructor'},
            related_name='courses',null=True,default=1
        )
    def __str__(self):
        return self.name

    
class Application(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="applications")
    full_name = models.CharField(max_length=255, default='')
    z_number=models.CharField(max_length=255,default='')
    previous_experience = models.CharField(max_length=255,default='')
    courses = models.ManyToManyField(Course)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)  # New field for resume
    submission_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=(
            ('under_review', 'Under Review'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ),
        default='under_review',
    )

    status_notified = models.BooleanField(default=False)  # Field to track notification status
    recommended_to_ta_committee = models.BooleanField(default=False) 
    ta_committee_status = models.CharField(
        max_length=20,
        choices=(
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ),
        default='pending',
    )

    ta_applicant_response = models.CharField(
        max_length=20,
        choices=(
            ('accepted', 'Accepted'),
            ('rejected', 'Rejected'),
        ),
        blank=True,
        null=True
    )

    def __str__(self):
        return f"Application of {self.user.username}"


class TAAssignment(models.Model):
    ta = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'ta_applicant'},
        related_name='ta_assignments',  # Unique related_name for TAs
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    ta_committee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'ta_committee'},
        related_name='committee_assignments',  # Unique related_name for TA Committee
    )
    status = models.CharField(
        max_length=20,
        choices=(
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ),
        default='pending',
    )
    assigned_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.ta.username} assigned to {self.course.name} by {self.ta_committee.username}"


class PerformanceEvaluation(models.Model):
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='performance_evaluations'
    )
    application = models.ForeignKey('Application', on_delete=models.CASCADE)
    feedback = models.TextField()
    rating = models.PositiveIntegerField()  # Rating from 1-5 or any scale
    submitted_at = models.DateTimeField(auto_now_add=True)
    # Decision field for TA Committee to approve or reject the TA based on evaluation
    decision = models.CharField(
        max_length=20,
        choices=(
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ),
        default='pending',
    )

    def __str__(self):
        return f"{self.application.full_name} - {self.rating}"
