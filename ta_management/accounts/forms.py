from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User  # Import the custom User model
from .models import Application, Course
from django.core.exceptions import ValidationError


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User  # Use the custom User model
        fields = ['username','email', 'password1', 'password2']  # Specify the fields you want to include
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email is required.")
        return email


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['full_name', 'z_number','previous_experience', 'courses','resume']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['courses'].queryset = Course.objects.all()  # Populate courses dynamically

    courses = forms.ModelMultipleChoiceField(queryset=Course.objects.all(), widget=forms.CheckboxSelectMultiple,required=False)
    resume = forms.FileField(required=False)  # Optional resume field

    def clean_previous_experience(self):
        data = self.cleaned_data.get('previous_experience')

        # Ensure no HTML tags are entered
        if '<' in data or '>' in data:
            raise ValidationError("HTML tags are not allowed in Previous Experience.")

        # Optional: Strip leading/trailing spaces and limit length
        data = data.strip()
        if len(data) > 500:  # Example length validation
            raise ValidationError("Previous Experience must be less than 500 characters.")

        return data

class CourseForm(forms.Form):
    course_name = forms.CharField(max_length=255)



from django import forms
from .models import TAAssignment, Course, User

class TAAssignmentForm(forms.ModelForm):
    class Meta:
        model = TAAssignment
        fields = ['ta', 'course', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit TA selection to users with the 'ta_applicant' role
        self.fields['ta'].queryset = User.objects.filter(role='ta_applicant')
        # Populate courses dynamically
        self.fields['course'].queryset = Course.objects.all()
        # Status choices can be set explicitly if needed
        self.fields['status'].choices = TAAssignment._meta.get_field('status').choices


from django import forms
from .models import Application

class OfferResponseForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['ta_applicant_response']
        widgets = {
            'ta_applicant_response': forms.RadioSelect(),
        }