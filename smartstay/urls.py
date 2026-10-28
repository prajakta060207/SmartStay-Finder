from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('choose-role/', views.choose_role, name='choose_role'),

    path('owner-login/', views.owner_login, name='owner_login'),
    path('owner-dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('add-hostel/', views.add_hostel, name='add_hostel'),
    path('hostel/<int:hostel_id>/rooms/', views.manage_rooms, name='manage_rooms'),
    path('room/<int:room_id>/toggle/', views.toggle_room, name='toggle_room'),
    path('room/<int:room_id>/edit/', views.edit_room, name='edit_room'),
    path('room/<int:room_id>/delete/', views.delete_room, name='delete_room'),
    path('owner-logout/', views.owner_logout, name='owner_logout'),

    path('tenant-login/', views.tenant_login, name='tenant_login'),
    path('tenant-home/', views.tenant_home, name='tenant_home'),
    path('hostel/<int:hostel_id>/', views.hostel_detail, name='hostel_detail'),
    path('tenant-logout/', views.tenant_logout, name='tenant_logout'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)