from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['room_name', 'start_datetime', 'end_datetime', 'status', 'booking_code','n_req','n_ph','h_pr','n_count','n_list','dpm_sd','equipment_list']
        widgets = {
            'start_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        # กำหนดค่าเริ่มต้นให้ฟิลด์ status เป็น 'pending'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].initial = 'pending'  # ค่าเริ่มต้นของฟิลด์ status