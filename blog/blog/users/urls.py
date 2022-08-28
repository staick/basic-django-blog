# for route view of users sub app 
from django.urls import path
from users.views import RegisterView

urlpatterns = {
    # first arg: route
    # second arg: view function name
    path('register/', RegisterView.as_view(), name='register'),
}