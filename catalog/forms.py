import datetime
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from catalog.models import Author, Book, BookInstance

class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(help_text="Enter a date between now and 4 weeks (default 3).")

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']

        # Check if a date is not in the past.
        if data < datetime.date.today():
            raise ValidationError('Invalid date - renewal in past')

        # Check if a date is in the allowed range (+4 weeks from today).
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError('Invalid date - renewal more than 4 weeks ahead')
        return data
    
# author class that inherit from modelform
class AuthorForm(ModelForm):
    class Meta:
        model = Author
        fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
        labels = {'first_name': 'First Name', 'last_name': 'Last Name', 'date_of_birth': 'Date of Birth', 'date_of_death': 'Date of Death'}
        widgets = {'date_of_birth': forms.DateInput({'type': 'date'}), 'date_of_death': forms.DateInput({'type': 'date'})}
    
    # check if date_of_birth is less than date_of_death
    def clean_date_of_death(self):
        data = self.cleaned_data['date_of_death']
        if data < self.cleaned_data['date_of_birth']:
            raise ValidationError('Invalid date - death date before birth date')
        # check if it is the same dob and dod
        if data == self.cleaned_data['date_of_birth']:
            raise ValidationError('Invalid date - death date is the same as birth date')
        return data

class BookForm(ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']

class BookInstanceForm(ModelForm):
    class Meta:
        model = BookInstance
        fields = ['book', 'imprint', 'status']
        widgets = {'due_back': forms.DateInput({'type': 'date'})}