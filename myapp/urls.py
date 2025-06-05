from django.urls import path
from myapp import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.index),
    path('about',views.about),
    path('form',views.form),
    path('base',views.base),
    path('edit/<person_id>',views.edit),
    path('delete/<person_id>',views.delete),
    path('home/', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile, name='profile'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('bookings/', views.booking_list, name='booking_list'),  
    path('RoomBooking', views.roombooking_view, name='roombooking'),# ✅ ใช้ชื่อใหม่
    path('bookings/<int:id>/', views.booking_detail, name='booking_detail'), # สำหรับปุ่ม "แสดง" 
    path('book-room/', views.book_room, name='book_room'),
    path('create/', views.booking_create_view, name='booking_create'),
    path('booking/new/', views.booking_create_view, name='booking_create'),  # หากใช้ form แบบ ModelForm
    path('secret/', views.secret_view),

    # -----------------------------------------------

    path('calendar/', views.calendar_view, name='calendar_view'),
    path('calendar/events/', views.calendar_events, name='calendar_events'),
# ปุ่มยกยกเลิก booking _detail
    path('booking/cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
# ปุ่มเเก้ไข booking_detail
    path('booking/edit/<int:booking_id>/', views.edit_booking, name='edit_booking'),
    path('add-equipment/', views.add_equipment, name='add_equipment'),
    path('check_room_availability/', views.check_room_availability, name='check_room_availability')
    
]   + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
