from django.shortcuts import render

# Create your views here.

from django.views import View

# Register view
class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')
