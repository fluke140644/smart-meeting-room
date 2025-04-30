from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_code', 'room_name', 'n_req', 'status', 'start_datetime', 'end_datetime', 'display_equipment_list')
    list_filter = ('status',)
    search_fields = ('booking_code', 'room_name')

    def display_equipment_list(self, obj):
        return ", ".join([str(equipment) for equipment in obj.equipment_list.all()])
    display_equipment_list.short_description = 'รายการอุปกรณ์'

    # def display_equipment(self, obj):
    #     # Custom display method to show equipment list
    #     return ", ".join([equipment.name for equipment in obj.equipment_list.all()]) if obj.equipment_list.exists() else "No equipment"
    # display_equipment.short_description = 'Equipment List'
# Register your models here.
# admin.site.register(Person)
# admin.site.register(Person2)