from django import forms
from .models import UserPost, UserProfile


class UserPostForm(forms.ModelForm):
    class Meta:
        model = UserPost
        fields = ['caption', 'files']  # Specify the fields you want to include in the form
        labels = {
            'files': 'File',  # Customize the label for the 'files' field
        }


class UserProfileForm(forms.ModelForm):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    gender = forms.ChoiceField(choices=GENDER_CHOICES)
    class Meta:
        model = UserProfile
        fields = ['dob', 'location', 'profile_image', 'phn_num', 'gender', 'school', 'bio', 'interest']

