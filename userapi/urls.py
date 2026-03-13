
from django.urls import path
from . import views

urlpatterns = [
    path('signup',views.Signup,name='signup')
]