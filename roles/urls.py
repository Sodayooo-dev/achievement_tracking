from django.urls import path

from roles.views import RolesList, RolesDetail, RolesCreate

urlpatterns = [
    path('roles/', RolesList.as_view()),
    path('roles/<int:pk>/', RolesDetail.as_view()),
    path('roles/new/', RolesCreate.as_view()),
]