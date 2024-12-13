from django.urls import path

from api.views import LoginView, RegisterView

urlpatterns = [
  
    path('register/',RegisterView.as_view()),
    path('login/',LoginView.as_view()),
    # path('re/',BankView.as_view())
    
]