from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.models import Group

# Create your views here.
# signup class based view
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import SignUpForm

class SignUpView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'
    
    # pass message using message framework
    def form_valid(self, form):
         # Save the user object
        response = super().form_valid(form)

        # Add the user to the desired group
        group = Group.objects.get(name='Library Members')
        group.user_set.add(self.object)

        messages.success(self.request, 'Your account was created successfully')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Your account could not be created')
        return super().form_invalid(form)
    
