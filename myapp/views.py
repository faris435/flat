from datetime import datetime

from django.contrib import messages
from django.contrib.auth.models import User,Group
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from myapp.models import *

# Create your views here.

def login_page(request):
    return render(request, 'login_page.html')


def login_post(request):
    username = request.POST['username']
    password = request.POST['password']
    ob = authenticate(username=username, password=password)
    if ob is not None:
        if ob.groups.filter(name='admin').exists():
            login(request, ob)
            return redirect('/myapp/admin_home/')
        elif ob.groups.filter(name='Service provider').exists():
            ss=Service_Provider.objects.get(LOGIN=ob)
            if ss.Status == 'Approved':
                login(request, ob)
                return redirect('/myapp/service_home/')
            else:
                messages.warning(request, 'Your registration is still pending approval.')
                return redirect('/myapp/login/')
        elif ob.groups.filter(name='user').exists():
            login(request, ob)
            return redirect('/myapp/user_home/')
        else:
            messages.error(request, 'Invalid username or password')
        return redirect('/myapp/login/')
    else:
        messages.error(request, 'Invalid username or password')
    return redirect('/myapp/login/')

def admin_home(request):
    return render(request, 'admin/admin_home.html')

def verify_occupants(request):
    ob=User_Table.objects.all()
    return render(request, 'admin/verify_occupants.html',{'data': ob})

def approve_occupant(request, id):
    ob = User_Table.objects.get(id=id)
    ob.status = 'Approved'
    ob.save()
    return redirect('/myapp/verify_occupants/')

def reject_occupant(request, id):
    ob = User_Table.objects.get(id=id)
    ob.status = 'Rejected'
    ob.save()
    return redirect('/myapp/verify_occupants/')


def add_category(request):
    return render(request, 'admin/add_category.html')

def category_post(request):
    name = request.POST['category']
    ob = Category_Table()
    ob.category = name
    ob.save()
    messages.success(request, 'Category added successfully.')
    return redirect('/myapp/view_category/')



def view_room(request):
    ob=Room_Table.objects.all()
    return render(request, 'admin/view_room.html', {'rooms': ob})

def add_room(request):
    return render(request, 'admin/add_room.html')

def add_room_post(request):
    floor=request.POST['floor']
    room_no=request.POST['room_no']
    details=request.POST['details']
    image=request.FILES['image']
    ob=Room_Table()
    ob.floor=floor
    ob.roomnumber=room_no
    ob.details=details
    ob.image=image
    ob.save()
    return redirect('/myapp/view_room/')

def edit_room(request,id):
    ob=Room_Table.objects.get(id=id)
    if request.method == 'POST':
        floor=request.POST['floor']
        room_no=request.POST['room_no']
        details=request.POST['details']
        ob.floor=floor
        ob.roomnumber=room_no
        ob.details=details
        if 'image' in request.FILES:
            image=request.FILES['image']
            ob.image=image
        ob.save()
        return redirect('/myapp/view_room/')
    return render(request, 'admin/edit_room.html',{'data': ob})

def delete_room(request, id):
    ob = Room_Table.objects.get(id=id)
    ob.delete()
    return redirect('/myapp/view_room/')





def view_category(request):
    categories = Category_Table.objects.all()
    return render(request, 'admin/view_category.html', {'categories': categories})

def delete_category(request, id):
    ob = Category_Table.objects.get(id=id)
    ob.delete()
    messages.success(request, 'Category deleted successfully.')
    return redirect('/myapp/view_category/')



def send_reply(request):
    return render(request, 'admin/send_reply.html')

from django.shortcuts import render, redirect
from .models import Service_Provider

def verify_servicesprovider(request):
    ob = Service_Provider.objects.filter(Status='pending')
    return render(request, 'admin/verify_serviceprovider.html', {'data': ob})

def approve_provider(request, id):
    ob = Service_Provider.objects.get(id=id)
    ob.Status = 'Approved'
    ob.save()
    return redirect('/myapp/verify_servicesprovider/')

def reject_provider(request, id):
    ob = Service_Provider.objects.get(id=id)
    ob.Status = 'Rejected'
    ob.save()
    return redirect('/myapp/verify_servicesprovider/')




from django.db.models import Case, When, Value, IntegerField


def view_complaint(request):
    ob = Complaint_Table.objects.annotate(
        priority=Case(
            When(reply='pending', then=Value(0)),
            default=Value(1),
            output_field=IntegerField(),
        )
    ).order_by('priority', '-date')
    
    total_count = ob.count()
    pending_count = ob.filter(reply='pending').count()
    
    return render(request, 'admin/view_complaint.html', {
        'data': ob,
        'total_count': total_count,
        'pending_count': pending_count
    })

def reply_complaint(request, id):
    ob = Complaint_Table.objects.get(id=id)
    if request.method == 'POST':
        reply = request.POST['reply']
        ob.reply = reply
        ob.save()
        return redirect('/myapp/view_complaint/')
    return render(request, 'admin/send_reply.html', {'data': ob})

def admin_view_facility(request):
    ob=Facility_Table.objects.all()
    return render(request, 'admin/view_facility.html', {'data': ob})


def add_facility(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
    
        photo = request.FILES.get('photo')
        ob = Facility_Table()
        ob.name = name
        ob.description = description
        ob.photo = photo
        ob.Status = 'Active'
        ob.save()
        return redirect('/myapp/admin_view_facility/')
    
    return render(request, 'admin/add_facility.html')

def edit_facility(request, id):
    ob = Facility_Table.objects.get(id=id)
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        status = request.POST.get('status')
        ob.name = name
        ob.description = description
        ob.Status = status 

        if 'photo' in request.FILES:
            ob.photo = request.FILES['photo']
            
        ob.save()
        return redirect('/myapp/admin_view_facility/')
    return render(request, 'admin/edit_facility.html', {'data': ob})

def delete_facility(request, id):
    ob = Facility_Table.objects.get(id=id)
    ob.delete()
    return redirect('/myapp/admin_view_facility/')



def admin_view_rating(request):
    ratings = Rating_Table.objects.select_related('USER', 'SERVICE__PROVIDER').all()

    grouped_data = {}
    for r in ratings:
        provider = r.SERVICE.PROVIDER
        r.star_range = range(r.rating)
        r.empty_star_range = range(5 - r.rating)

        if provider not in grouped_data:
            grouped_data[provider] = []
        grouped_data[provider].append(r)

    return render(request, 'admin/view_rating.html', {'grouped_data': grouped_data})


def service_provider_register(request):
    ob=Category_Table.objects.all()
    return render(request, 'service_provider/register.html',{'category':ob})

def register_post(request):
    name = request.POST['name']
    email = request.POST['email']
    phone = request.POST['phone']
    category=request.POST['category']
    place = request.POST['place']
    post = request.POST['post']
    pin = request.POST['pin']
    photo = request.FILES['photo']
    username = request.POST['username']
    password = request.POST['password']
    proof = request.FILES['proof']
    with transaction.atomic():
    
        objects = User.objects.create_user(username=username, password=password)
        objects.save()
        objects.groups.add(Group.objects.get(name='Service provider'))
        ob=Service_Provider()
        ob.name=name
        ob.email=email
        ob.phone=phone
        ob.CATEGORY_id=category
        ob.place=place
        ob.post=post
        ob.pin=pin
        ob.photo=photo
        ob.LOGIN=objects
        ob.proof=proof
        ob.Status='pending'
        ob.save()
    messages.success(request, 'Registration successful. Please wait for admin approval.')
    return redirect('/myapp/login/')
    
    


       

def service_home(request):
    ob=Service_Provider.objects.get(LOGIN=request.user)
    return render(request, 'service_provider/service_provider_home.html',{'data': ob})
    
def view_services(request):
    ob=Service_Table.objects.filter(PROVIDER__LOGIN=request.user)
    return render(request, 'service_provider/view_service.html',{'data': ob})

def add_service(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        photo = request.FILES.get('photo')
        ob = Service_Table()
        ob.name = name
        ob.description = description
        ob.price = price
        ob.photo = photo
        ob.Status = 'Active'
        ob.PROVIDER_id = Service_Provider.objects.get(LOGIN=request.user).id
        ob.save()
        return redirect('/myapp/view_services/')
    return render(request, 'service_provider/add_service.html')

def edit_service(request,id):
    ob = Service_Table.objects.get(id=id)
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        ob.name = name
        ob.description = description
        ob.price = price
        if 'photo' in request.FILES:
            photo = request.FILES.get('photo')
            ob.photo = photo
        ob.Status = request.POST.get('status')
        ob.save()
        return redirect('/myapp/view_services/')
    return render(request, 'service_provider/edit_service.html',{'ob': ob})

def delete_service(request, id):
    ob = Service_Table.objects.get(id=id)
    ob.delete()
    return redirect('/myapp/view_services/')

def view_fooditem(request):
    ob=Food_Table.objects.filter(SERVICE__LOGIN=request.user)
    return render(request, 'service_provider/view_fooditem.html',{'data': ob})

def add_food(request):
    if request.method == 'POST':
        print(request.POST)
        item = request.POST.get('name')
        description = request.POST.get('details')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        photo = request.FILES.get('photo')
        mfg_date = request.POST.get('mfg_date')
        ob = Food_Table()
        ob.item = item
        ob.description = description
        ob.price = price
        ob.quantity = quantity
        ob.photo = photo
        ob.mfg_date = mfg_date
        ob.SERVICE_id = Service_Provider.objects.get(LOGIN=request.user).id
        ob.save()
        return redirect('/myapp/view_fooditem/')    
    return render(request, 'service_provider/add_food.html')

    

def edit_fooditem(request,id):
    ob = Food_Table.objects.get(id=id)
    if request.method == 'POST':
        item = request.POST.get('name')
        description = request.POST.get('details')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        mfg_date = request.POST.get('mfg_date')
        ob.item = item
        ob.description = description
        ob.price = price
        ob.quantity = quantity
        if 'photo' in request.FILES:
            photo = request.FILES.get('photo')
            ob.photo = photo
        ob.mfg_date = mfg_date
        ob.SERVICE_id = Service_Provider.objects.get(LOGIN=request.user).id
        ob.save()
        return redirect('/myapp/view_fooditem/')
    return render(request, 'service_provider/edit_fooditem.html',{'ob': ob})

def delete_fooditem(request, id):
    ob = Food_Table.objects.get(id=id)
    ob.delete()
    return redirect('/myapp/view_fooditem/')

def edit_profile(request):
    ob=Service_Provider.objects.get(LOGIN=request.user)
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        place = request.POST['place']
        post = request.POST['post']
        pin = request.POST['pin']
        ob.name=name
        ob.email=email
        ob.phone=phone
        ob.place=place
        ob.post=post
        ob.pin=pin
        if 'photo' in request.FILES:
            photo = request.FILES['photo']
            ob.photo=photo
        if 'proof' in request.FILES:
            proof = request.FILES['proof']
            ob.proof=proof
        ob.save()
        return redirect('/myapp/view_profile/')
    return render(request, 'service_provider/edit_profile.html',{'data': ob})


def send_complaint(request):
    return render(request, 'service_provider/send_complaint.html')



def view_profile(request):
    ob=Service_Provider.objects.get(LOGIN=request.user)
    return render(request, 'service_provider/view_profile.html',{'profile': ob})

from django.shortcuts import render
from django.db.models import Avg, Count, Q
from .models import Rating_Table, Service_Table

def view_rating(request):
    # Get ratings for this provider
    ratings = Rating_Table.objects.filter(SERVICE__PROVIDER__LOGIN=request.user)
    
    # Calculate statistics
    avg_rating = ratings.aggregate(Avg('rating'))['rating__avg'] or 0
    total_ratings = ratings.count()
    
    # Rating distribution (count per star)
    rating_counts = {}
    for star in range(1, 6):
        rating_counts[star] = ratings.filter(rating=star).count()
    
    # Get the first service for display (or modify as needed)
    service = Service_Table.objects.filter(PROVIDER__LOGIN=request.user).first()
    
    context = {
        'ratings': ratings,
        'data': ratings,  # for template's {% if data %} check
        'avg_rating': avg_rating,
        'total_ratings': total_ratings,
        'rating_counts': rating_counts,
        'service': service,
    }
    
    return render(request, 'service_provider/view_rating.html', context)


def view_reply(request):
    return render(request, 'service_provider/view_reply.html')

def service_view_bookings(request):
    ob=Booking_Table.objects.filter(SERVICE__PROVIDER__LOGIN=request.user)
    return render(request, 'service_provider/view_bookings.html',{'data': ob})

def confirm_booking(request, id):
    ob = Booking_Table.objects.get(id=id)
    ob.Status = 'Confirmed'
    ob.save()
    return redirect('/myapp/service_view_bookings/')

def reject_booking(request, id):
    ob = Booking_Table.objects.get(id=id)
    ob.Status = 'Rejected'
    ob.save()
    return redirect('/myapp/service_view_bookings/')

def service_view_food_orders(request):
    ob=Food_Order_Table.objects.filter(FOOD__SERVICE__LOGIN=request.user)
    return render(request, 'service_provider/view_food_orders.html',{'data': ob})

def confirm_food_order(request, id):
    ob = Food_Order_Table.objects.get(id=id)
    ob.Status = 'Confirmed'
    ob.save()
    return redirect('/myapp/service_view_food_orders/')

def reject_food_order(request, id):
    ob = Food_Order_Table.objects.get(id=id)
    ob.Status = 'Rejected'
    ob.save()
    return redirect('/myapp/service_view_food_orders/')

#####################################################





def add_quantity(request,id):
    ob=Food_Table.objects.get(id=id)
    if request.method == 'POST':
        dd=Food_Order_Table()
        dd.quantity = request.POST.get('quantity')
        dd.FOOD_id = ob.id
        dd.USER_id = User_Table.objects.get(LOGIN=request.user).id
        dd.date = datetime.today()
        dd.Status = 'ordered'
        dd.save()
        return redirect('/myapp/user_view_fooditem/')
    return render(request, 'user/add_quantity.html',{'food': ob})

def user_edit_profile(request):
    return render(request, 'user/edit_profile.html')

from django.db.models import Q

def user_register(request):
    booked_rooms = User_Table.objects.filter(
        Q(status='pending') | Q(status='Approved')
    ).values_list('ROOM_id', flat=True)

    available_rooms = Room_Table.objects.exclude(id__in=booked_rooms)

    return render(request, 'user/register.html', {'room': available_rooms})



def user_register_post(request):
    name = request.POST['name']
    email = request.POST['email']
    phone = request.POST['phone']
    room=request.POST['room']
    photo = request.FILES['photo']
    username = request.POST['username']
    password = request.POST['password']
    with transaction.atomic():
        objects = User.objects.create_user(username=username, password=password)
        objects.save()
        objects.groups.add(Group.objects.get(name='user'))
        ob=User_Table()
        ob.name=name
        ob.email=email
        ob.phone=phone
        ob.ROOM_id=room
        ob.photo=photo
        ob.LOGIN=objects
        ob.Status='pending'
        ob.save()
    messages.success(request, 'Registration successful. Please wait for admin approval.')
    return redirect('/myapp/login/')
    
    

def send_complaint(request):
    if request.method == 'POST':
        complaint = request.POST['complaint']
        type = request.POST['type']
        ob = Complaint_Table()
        ob.USER_id = User_Table.objects.get(LOGIN=request.user).id
        ob.Complain = complaint
        ob.reply = 'pending'
        ob.type = type
        ob.date = datetime.today()
        ob.save()
        messages.success(request, 'Complaint sent successfully.')
        return redirect('/myapp/user_view_reply/')
    return render(request, 'user/send_complaint.html')

def user_view_booking(request):
    ob=Booking_Table.objects.filter(USER__LOGIN=request.user)
    return render(request, 'user/view_booking.html', {'data': ob})

def service_payment(request,id):
    ob=Booking_Table.objects.get(id=id)
    ob.Status = 'paid'
    ob.save()
    messages.success(request, 'Payment successful.')
    return redirect('/myapp/user_view_booking/')

def view_facility(request):
    ob=Facility_Table.objects.all()
    return render(request, 'user/view_facility.html', {'data': ob})

def user_view_fooditem(request):
    ob=Food_Table.objects.filter(mfg_date=datetime.today())
    return render(request, 'user/view_food_item.html',{'data': ob})

def user_view_profile(request):
    ob=User_Table.objects.get(LOGIN=request.user)
    return render(request, 'user/view_profile.html',{'profile': ob})

def user_edit_profile(request):
    ob=User_Table.objects.get(LOGIN=request.user)
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        ob.name=name
        ob.email=email
        ob.phone=phone
        if 'photo' in request.FILES:
            photo = request.FILES['photo']
            ob.photo=photo
        ob.save()
        return redirect('/myapp/user_view_profile/')
    return render(request, 'user/edit_profile.html',{'data': ob})

def user_view_rating(request,id):
    ob=Rating_Table.objects.filter(SERVICE_id=id)
    return render(request, 'user/view_rating.html',{'data': ob,'service_id': id})

def user_view_reply(request):
    ob=Complaint_Table.objects.filter(USER__LOGIN=request.user)
    return render(request, 'user/view_reply.html',{'data': ob})

def user_view_services(request):
    ob=Service_Table.objects.filter(Status='Active')
    return render(request, 'user/view_service.html', {'data': ob})

def book_service(request,id):
    Booking_Table(
        USER_id=User_Table.objects.get(LOGIN=request.user).id,
        SERVICE_id=id,
        date=datetime.today(),
        Status='pending'
    ).save()
    messages.success(request, 'Service booked successfully. Please wait for confirmation.')
    return redirect('/myapp/user_view_booking/')

def user_home(request):
    ob=User_Table.objects.get(LOGIN=request.user)
    return render(request, 'user/user_home.html',{'data': ob})

def order_history(request):
    ob=Food_Order_Table.objects.filter(USER__LOGIN=request.user)
    return render(request, 'user/order_history.html',{'data': ob})

def pay_order(request, id):
    ob = Food_Order_Table.objects.get(id=id)
    ob.Status = 'paid'
    ob.save()
    messages.success(request, 'Order paid successfully.')
    return redirect('/myapp/order_history/')

def send_service_rating(request,id):
    if request.method == 'POST':
        rating = request.POST['rating']
        review = request.POST['review']
        ob = Rating_Table()
        ob.USER_id = User_Table.objects.get(LOGIN=request.user).id
        ob.SERVICE_id = id
        ob.rating = rating
        ob.review = review
        ob.date = datetime.today()
        ob.save()
        messages.success(request, 'Rating submitted successfully.')
        return redirect('/myapp/user_view_booking/')
    return render(request, 'user/send_rating.html')





def logout_view(request):
    logout(request)
    return redirect('/myapp/login_page/')

def chat_with_user(request, fid, fname):
    return render(request, 'chat_page.html', {'receiver_id': fid, 'receiver_name': fname})


def chat_api(request):
    if request.method == 'POST':
        # 1. SEND MESSAGE LOGIC
        if 'message' in request.POST:
            sid = request.POST.get('sender_id')
            rid = request.POST.get('receiver_id')
            msg = request.POST.get('message')

            ChatTable.objects.create(
                SENDER_id=sid,
                RECEIVER_id=rid,
                message=msg
            )
            return JsonResponse({'status': 'ok'})

        # 2. VIEW MESSAGE LOGIC
        else:
            sid = request.POST.get('sender_id')
            rid = request.POST.get('receiver_id')

            chats = ChatTable.objects.filter(
                (Q(SENDER_id=sid) & Q(RECEIVER_id=rid)) |
                (Q(SENDER_id=rid) & Q(RECEIVER_id=sid))
            ).order_by('date', 'time')

            # Update unread messages
            chats.filter(RECEIVER_id=sid).update(is_read=True)

            data = [{
                'sid': str(c.SENDER.id),
                'msg': c.message,
                'time': c.time.strftime("%I:%M %p")
            } for c in chats]

            return JsonResponse({'status': 'ok', 'data': data})

    return JsonResponse({'status': 'error'})










