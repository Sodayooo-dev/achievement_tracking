from django.urls import path

from roles.views import RolesList, RolesDetail, RolesCreate, RolesUpdate, RolesDelete

urlpatterns = [
    path('roles/', RolesList.as_view()),
    path('roles/<int:pk>/', RolesDetail.as_view()),
    path('roles/new/', RolesCreate.as_view()),
    path('roles/<int:pk>/update/', RolesUpdate.as_view()),
    path('roles/<int:pk>/delete/', RolesDelete.as_view()),
]