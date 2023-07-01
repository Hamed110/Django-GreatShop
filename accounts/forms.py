from typing import Any, Dict
from django import forms
from django.contrib import messages

from .models import Account


class RegisterationForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'',
        'class': 'form-control'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'',
        'class': 'form-control'
    }))
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'password',]


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

        self.fields['first_name'].widget.attrs['autofocus'] = 'autofocus'
        self.fields['email'].widget.attrs['placeholder'] = 'Will be used as your username'


    def clean(self):
        cleaned_data = super().clean()
    
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                'password does not match.'
            )
        
