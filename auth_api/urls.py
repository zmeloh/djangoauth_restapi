from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('resetpassword/', views.resetpassword, name='resetpassword'),
    path('forgetpassword/', views.forgetpassword, name='forgetpassword'),
    path('logout/', views.logout, name='logout'),
    path('token/', views.token, name='token'),
]
