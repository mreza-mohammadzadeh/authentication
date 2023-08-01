from django.urls import path
from .views import UserVerify, UserUpdate, UserList, UserRegister, UserGet, UserLogin

urlpatterns = [
    path("user_list", UserList.as_view()),
    path("user_login", UserLogin.as_view()),
    path("user_verify_login", UserVerify.as_view()),
    path("user_register", UserRegister.as_view()),
    path("user_update", UserUpdate.as_view()),
    path("user_get", UserGet.as_view())
]
