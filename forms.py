from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from . import models

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=20)
    last_name = forms.CharField(max_length=20)

    class Meta:
        model = User
        fields = ["username","first_name","last_name","email","password1","password2"]

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

STATUS=(
    ('P','Pending'),
    ('I','In Progress'),
    ('C','Completed'),
)

class PostForm(forms.ModelForm):
    new_description = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Enter additional description here...'}), required=False)

    class Meta:
        model = models.Problem
        fields = ['description','new_description','assign_to', 'status' ]
        widgets = {
            'description': forms.Textarea(attrs={'readonly': 'readonly'})
        }

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['description'].initial = self.instance.description

class IssueForm(forms.ModelForm):
    class Meta:
        model=models.Problem
        fields=['title','description','assign_to','status','remark']