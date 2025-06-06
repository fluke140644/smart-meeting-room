from datetime import datetime
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.db.models import Q
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from .models import Person, Booking, Equipment, Holiday
from .forms import BookingForm
import threading


# Create your views here.
@login_required
def secret_view(request):
    print("is_authenticated:", request.user.is_authenticated)
    return HttpResponse("คุณต้อง login ก่อนถึงจะเห็นหน้านี้")

# หน้าหลัก 
def index(request):
    return render(request,"index.html")

#หลัง login
@login_required
def home(request):
    return render(request, 'home.html')


# ฟังก์ชันนี้จะใช้ในการแสดงหน้า Login
def login_page(request):
    return render(request, 'login.html')

# ฟังก์ชันนี้ใช้ในการตรวจสอบการเข้าสู่ระบบ
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            return redirect('/')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    
    return render(request, 'login.html')

@login_required
def profile(request):
    return render(request, 'profile.html', {'user': request.user})




#P' หน้าเกี่ยวกับ
@login_required
def about(request):
    return render(request,"about.html")

#Form กรอกข้อมูล
@login_required
def form(request):
    if request.method == "POST":
        #รับข้อมูล
        name = request.POST["name"]
        surname = request.POST["surname"]
        age = request.POST["age"]
        email = request.POST.get("email")
        if email :
            messages.success(request, f'Your Email is : {email}')
        else:
            messages.error(request,'no email provided.')
        #บันทึกข้อมูล
        person = Person.objects.create(
            name=name,
            surname=surname,
            age=age,
            email=email
        )
        person.save()
        messages.success(request,"บันทึกข้อมูลเรียบร้อย")
        #เปลี่ยนเส้นทาง
        return redirect("/test1") 
    else : 
        return render(request,"form.html")
    
#edit
@login_required
def edit(request,person_id):
    if request.method == "POST":
        person = Person.objects.get(id=person_id)
        person.name = request.POST["name"]
        person.surname = request.POST["surname"]
        person.age = request.POST["age"]
        person.email = request.POST["email"]
        person.save()
        messages.success(request,"อัพเดชข้อมูลเรียบร้อย")
        return redirect("/test1") 
    else:
    #ดึงข้อมูลประชากรที่ต้องการแก้ไข
        person = Person.objects.get(id=person_id)
        return render(request,"edit.html",{"person":person})
    
def delete(request,person_id):
    person = Person.objects.get(id=person_id)
    person.delete()
    messages.success(request,"ลบข้อมูลเรียบร้อย")
    return redirect("/test1")


@login_required
def base(request):
    return render(request,"base.html")

#-------------------------------------------------
@login_required
def booking_list(request):
    bookings = Booking.objects.all()  

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    status = request.GET.get('status')
    keyword = request.GET.get('keyword')

    if start_date:
        bookings = bookings.filter(start_datetime__date__gte=start_date)
    if end_date:
        bookings = bookings.filter(end_datetime__date__lte=end_date)
    if status and status != 'all':
        bookings = bookings.filter(status=status)
    if keyword:
        bookings = bookings.filter(
            Q(room_name__icontains=keyword) |
            Q(topic__icontains=keyword) |
            Q(booking_code__icontains=keyword)
        )

    context = {
        'bookings': bookings.order_by('-start_datetime'),
    }
    return render(request, 'booking_list.html', context)

@login_required
def booking_detail(request, id):
    booking = Booking.objects.get(id=id)

    equipment_data = []
    if booking.equipment_list.exists():
        equipment_data = booking.equipment_list.all() 

    return render(request, 'booking_detail.html', {
        'booking': booking,
        'equipment_data': equipment_data,
    })

@login_required
def roombooking_view(request):
    bookings = Booking.objects.all() 

    # รับค่าจาก GET
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    status = request.GET.get('status')
    query = request.GET.get('q')

    # กรองตามวันที่
    if start_date:
        bookings = bookings.filter(start_datetime__date__gte=start_date)
    if end_date:
        bookings = bookings.filter(end_datetime__date__lte=end_date)

    # กรองตามสถานะ
    if status:
        bookings = bookings.filter(status=status)

    # กรองคำค้นหา (ชื่อห้อง, เลขใบจอง)
    if query:
        bookings = bookings.filter(
            Q(room_name__icontains=query) |
            Q(booking_code__icontains=query)
        )

    context = {
        'bookings': bookings,
        'selected_status': status, 
    }
    return render(request, 'roombooking_list.html', context)



@login_required
def room_booking_list(request):
    bookings = Booking.objects.all()  

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    status = request.GET.get('status')
    q = request.GET.get('q')

    if start_date:
        bookings = bookings.filter(start_datetime__date__gte=start_date)
    if end_date:
        bookings = bookings.filter(end_datetime__date__lte=end_date)
    if status:
        bookings = bookings.filter(status=status)
    if q:
        bookings = bookings.filter(
            Q(room_name__icontains=q) | Q(booking_code__icontains=q)
        )

    selected_status = request.GET.get('status', '')
    context = {
        'bookings': bookings,
        'selected_status': selected_status,
    }
    return render(request, 'roombooking_list.html', context)

# ฟังก์ชันการจองห้อง


@login_required
def book_room(request):
    if request.method == 'POST':
        room_name = request.POST['room_name']
        start_datetime = request.POST['start_datetime']
        end_datetime = request.POST['end_datetime']
        topic = request.POST['topic']
        description = request.POST['description']
        n_req = request.POST['n_req']
        n_ph = request.POST['n_ph']
        h_pr = request.POST['h_pr']
        n_count = request.POST['n_count']
        n_list = request.POST['n_list']
        dpm_sd = request.POST['dpm_sd']
        equipment_list_json = request.POST.get('equipment_list')  

        
        if not start_datetime or not end_datetime:
            messages.error(request, "กรุณาระบุวันและเวลาเริ่มต้น/สิ้นสุดให้ครบถ้วน")
            return render(request, 'book_room.html', {
                'room_name': room_name,
                'topic': topic,
                'description': description,
                'n_req': n_req,
                'n_ph': n_ph,
                'h_pr': h_pr,
                'n_count': n_count,
                'n_list': n_list,
                'dpm_sd': dpm_sd,
            })

        start_datetime_obj = datetime.strptime(start_datetime, '%Y-%m-%dT%H:%M')
        end_datetime_obj = datetime.strptime(end_datetime, '%Y-%m-%dT%H:%M')

        
        existing_booking = Booking.objects.filter(
            room_name=room_name,
            start_datetime__lt=end_datetime_obj,
            end_datetime__gt=start_datetime_obj
        ).exists()

        if existing_booking:
            return render(request, 'book_room.html', {
                'conflict': True,
                'room_name': room_name,
                'start_datetime': start_datetime,
                'end_datetime': end_datetime,
                'topic': topic,
                'description': description,
                'n_req': n_req,
                'n_ph': n_ph,
                'h_pr': h_pr,
                'n_count': n_count,
                'n_list': n_list,
                'dpm_sd': dpm_sd,
                'equipment_list': equipment_list_json
            })

        # บันทึกการจอง (ยังไม่ใส่อุปกรณ์)
        booking = Booking(
            room_name=room_name,
            start_datetime=start_datetime_obj,
            end_datetime=end_datetime_obj,
            topic=topic,
            description=description,
            n_req=n_req,
            n_ph=n_ph,
            h_pr=h_pr,
            n_count=int(n_count),
            n_list=n_list,
            dpm_sd=dpm_sd
        )
        booking.save()

        equipment_text = "ไม่มี"

        
        if equipment_list_json:
            equipment_data = json.loads(equipment_list_json)  
            equipment_ids = []

            for item in equipment_data:
                name = item['name']
                quantity = item['quantity']

                # หรือลองสร้างใหม่ถ้าไม่มี
                equipment_obj, created = Equipment.objects.get_or_create(name=name, defaults={'quantity': quantity})

                if not created:
                
                    equipment_obj.quantity = quantity
                    equipment_obj.save()

                equipment_ids.append(equipment_obj.id)

            booking.equipment_list.set(equipment_ids)

            
            if equipment_data:
                equipment_text = ""
                for item in equipment_data:
                    equipment_text += f"- {item['name']} จำนวน {item['quantity']}\n"
            else:
                equipment_text = "ไม่มี"

        threading.Thread(target=send_email_async, args=(booking, equipment_text)).start()


        # ส่งอีเมลยืนยันการจอง
        # send_mail(
        #     subject='ยืนยันการจองห้องประชุม',
        #     message=f'คุณได้จองห้อง {booking.room_name} \n เวลา {booking.start_datetime} - {booking.end_datetime}\n\nหัวข้อ : {booking.topic}\nแผนก : {booking.dpm_sd}\nชื่อผู้ขอใช้ : {booking.n_req} \nเบอร์ติดต่อ : {booking.n_ph}\nจำนวนผู้เข้าประชุม : {booking.n_count}\nรายชื่อผู้เข้าประชุม : \n{booking.n_list}\nรายละเอียด : {booking.description}\nรายการอุปกรณ์ : \n{equipment_text}\n',
        #     from_email=settings.DEFAULT_FROM_EMAIL,
        #     recipient_list=['fook165@gmail.com','nnasuxinthr@gmail.com'],
        #     fail_silently=False,
        # )

        # ส่ง success
        return render(request, 'book_room.html', {
            'success': True,
            'room_name': room_name,
            'start_datetime': start_datetime,
            'end_datetime': end_datetime,
            'topic': topic,
            'description': description,
            'n_req': n_req,
            'n_ph': n_ph,
            'h_pr': h_pr,
            'n_count': n_count,
            'n_list': n_list,
            'dpm_sd': dpm_sd,
        })

    return render(request, 'book_room.html')

def send_email_async(booking, equipment_text):
    try:
        send_mail(
            subject='ยืนยันการจองห้องประชุม',
            message=f'คุณได้จองห้อง {booking.room_name} \n เวลา {booking.start_datetime} - {booking.end_datetime}\n\nหัวข้อ : {booking.topic}\nแผนก : {booking.dpm_sd}\nชื่อผู้ขอใช้ : {booking.n_req} \nเบอร์ติดต่อ : {booking.n_ph}\nจำนวนผู้เข้าประชุม : {booking.n_count}\nรายชื่อผู้เข้าประชุม : \n{booking.n_list}\nรายละเอียด : {booking.description}\nรายการอุปกรณ์ : \n{equipment_text}\n',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['fook165@gmail.com','nnasuxinthr@gmail.com'],
            fail_silently=True,
        )
    except Exception as e:
        print("Email send failed:", e)


@login_required
def booking_create_view(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = BookingForm(initial={'status': 'pending'})  # ค่าเริ่มต้นเป็น 'pending'
    return render(request, 'booking_form.html', {'form': form})

# ปฏืทิน ------------------------

@login_required
def approve_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.status = 'approved'
    booking.save()
    return JsonResponse({'success': True})

# ------***************************************************

def calendar_view(request):
    return render(request, 'calendar.html')

def get_room_color(roomColor):
    return {
        'ห้องประชุมเพรชสมเด็จ': '#0033FF',        
        'ห้องประชุมผาเสวย': '#00A859',           
        'ห้องประชุมย่อย (วัคซีน1)': '#FF3333',   
        'ห้องประชุมภูเงิน': '#A9A9A9'             
    }.get(roomColor, '#808080')  

# ปฏิทิน
# @login_required
def calendar_events(request):
    bookings = Booking.objects.filter(status='approved')  # แสดงเฉพาะที่อนุมัติแล้ว
    events = []
    for booking in bookings:
        events.append({
            "id": booking.id,
            "title": booking.topic,
            "start": booking.start_datetime.isoformat(),
            "end": booking.end_datetime.isoformat(),
            "color": get_room_color(booking.room_name),
            "extendedProps": {
                "room": booking.room_name,
                "description": booking.description,
                "dpm_sd": booking.dpm_sd,
                "attendees": booking.n_count,
                "requester": booking.n_req,
                "phone": booking.n_ph,
                "status": booking.status
            }
        })
    return JsonResponse(events, safe=False)

def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == 'POST':
        # เปลี่ยนสถานะเป็นยกเลิก
        booking.status = 'cancelled'
        booking.save()

        # เตรียมข้อความอุปกรณ์ (ถ้ามี)
        equipment_text = ""
        if hasattr(booking, 'equipment_list'):
            equipment_items = booking.equipment_list.all()
            if equipment_items:
                for item in equipment_items:
                    equipment_text += f"- {item.name} จำนวน {item.quantity}\n"
            else:
                equipment_text = "ไม่มี"
        else:
            equipment_text = "ไม่มีข้อมูล"

        # ส่งอีเมลแจ้งยกเลิก
        send_mail(
            subject='แจ้งยกเลิกการจองห้องประชุม',
            message=f"""การจองห้องประชุมถูกยกเลิกแล้ว

ห้อง: {booking.room_name}
เวลา: {booking.start_datetime} - {booking.end_datetime}
หัวข้อ: {booking.topic}
ผู้ขอใช้: {booking.n_req}
แผนก: {booking.dpm_sd}

รายการอุปกรณ์:
{equipment_text}

ขอบคุณที่แจ้งล่วงหน้า.""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['fook165@gmail.com'],  # หรือ booking.user.email ถ้ามี
            fail_silently=False,
        )

        messages.success(request, "ยกเลิกการจองเรียบร้อยแล้ว")

    return redirect('roombooking')

def edit_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == "POST":
        booking.room_name = request.POST.get("room_name")
        booking.topic = request.POST.get("topic")
        booking.h_pr = request.POST.get("h_pr")
        booking.dpm_sd = request.POST.get("dpm_sd")
        booking.n_req = request.POST.get("n_req")
        booking.n_ph = request.POST.get("n_ph")
        booking.start_datetime = request.POST.get("start_datetime")
        booking.end_datetime = request.POST.get("end_datetime")
        booking.n_list = request.POST.get("n_list")
        booking.description = request.POST.get("description")

        booking.save()
        return redirect('roombooking')  # หรือไปหน้าแสดงรายละเอียด

    return render(request, "edit_booking.html", {"booking": booking})

    # return render(request, 'edit_booking.html', {'form': form, 'booking': booking})



def holiday_events(request):
    holidays = Holiday.objects.all()
    events = [{
        "title": h.title,
        "start": h.date.isoformat(),
        "allDay": True,
        "color": "#FF0000"
    } for h in holidays]
    return JsonResponse(events, safe=False)

def add_equipment(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        quantity = request.POST.get('quantity')
        
        Equipment.objects.create(name=name, quantity=quantity)
        
        return JsonResponse({'message': 'Equipment added successfully!'})
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)
    

@login_required
def check_room_availability(request):
    if request.method == 'POST':
        room_name = request.POST['room_name']
        start_datetime = request.POST['start_datetime']
        end_datetime = request.POST['end_datetime']

        start_datetime_obj = datetime.strptime(start_datetime, '%Y-%m-%dT%H:%M')
        end_datetime_obj = datetime.strptime(end_datetime, '%Y-%m-%dT%H:%M')

        existing_booking = Booking.objects.filter(
            room_name=room_name,
            start_datetime__lt=end_datetime_obj,
            end_datetime__gt=start_datetime_obj
        ).exists()

        return JsonResponse({'conflict': existing_booking})

    return JsonResponse({'error': 'Invalid request'}, status=400)
