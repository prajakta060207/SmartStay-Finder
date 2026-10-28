import math
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from .forms import TenantSignupForm, OwnerSignupForm, HostelForm, RoomForm
from .models import Tenant, Owner, Hostel, Room, Location


def haversine_km(lat1, lon1, lat2, lon2):
    """Distance in km between two latitude/longitude points (Haversine formula)."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def index(request):
    return render(request, 'core/index.html')


def choose_role(request):
    return render(request, 'core/choose_role.html')


# ---------- helpers: who is logged in (stored in session) ----------
def get_logged_in_owner(request):
    owner_id = request.session.get('owner_id')
    if owner_id:
        return Owner.objects.filter(id=owner_id).first()
    return None


def get_logged_in_tenant(request):
    tenant_id = request.session.get('tenant_id')
    if tenant_id:
        return Tenant.objects.filter(id=tenant_id).first()
    return None


# ---------- OWNER ----------
def owner_login(request):
    context = {}
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'signup':
            form = OwnerSignupForm(request.POST)
            if form.is_valid():
                owner = form.save(commit=False)
                owner.password = make_password(form.cleaned_data['password'])
                owner.save()
                context['success'] = True
            else:
                context['signup_error'] = 'Could not create account. This email may already be registered.'
        elif form_type == 'login':
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '')
            owner = Owner.objects.filter(email=email).first()
            if owner and check_password(password, owner.password):
                request.session['owner_id'] = owner.id
                return redirect('owner_dashboard')
            context['login_error'] = 'Invalid email or password'
    return render(request, 'core/owner_login.html', context)


def owner_dashboard(request):
    owner = get_logged_in_owner(request)
    if not owner:
        return redirect('owner_login')
    hostels = Hostel.objects.filter(owner=owner)
    return render(request, 'core/owner_home.html', {'owner': owner, 'hostels': hostels})


def add_hostel(request):
    owner = get_logged_in_owner(request)
    if not owner:
        return redirect('owner_login')
    if request.method == 'POST':
        form = HostelForm(request.POST)
        if form.is_valid():
            hostel = form.save(commit=False)
            hostel.owner = owner
            hostel.save()
            return redirect('owner_dashboard')
    else:
        form = HostelForm()
    return render(request, 'core/add_hostel.html', {'form': form, 'owner': owner})


def manage_rooms(request, hostel_id):
    owner = get_logged_in_owner(request)
    if not owner:
        return redirect('owner_login')
    hostel = get_object_or_404(Hostel, id=hostel_id, owner=owner)
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            room = form.save(commit=False)
            room.hostel = hostel
            room.save()
            return redirect('manage_rooms', hostel_id=hostel.id)
    else:
        form = RoomForm()
    rooms = Room.objects.filter(hostel=hostel).order_by('room_number')
    return render(request, 'core/manage_rooms.html', {'owner': owner, 'hostel': hostel, 'rooms': rooms, 'form': form})


def toggle_room(request, room_id):
    owner = get_logged_in_owner(request)
    if not owner:
        return redirect('owner_login')
    room = get_object_or_404(Room, id=room_id, hostel__owner=owner)
    if request.method == 'POST':
        room.is_vacant = not room.is_vacant
        if room.is_vacant:
            room.expected_vacancy_date = None
        room.save()
    return redirect('manage_rooms', hostel_id=room.hostel.id)


def owner_logout(request):
    request.session.flush()
    return redirect('index')


# ---------- TENANT ----------
def tenant_login(request):
    context = {}
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'signup':
            form = TenantSignupForm(request.POST)
            if form.is_valid():
                tenant = form.save(commit=False)
                tenant.password = make_password(form.cleaned_data['password'])
                tenant.save()
                context['success'] = True
            else:
                context['signup_error'] = 'Could not create account. This email may already be registered.'
        elif form_type == 'login':
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '')
            tenant = Tenant.objects.filter(email=email).first()
            if tenant and check_password(password, tenant.password):
                request.session['tenant_id'] = tenant.id
                return redirect('tenant_home')
            context['login_error'] = 'Invalid email or password'
    return render(request, 'core/tenant_login.html', context)


def tenant_home(request):
    tenant = get_logged_in_tenant(request)
    if not tenant:
        return redirect('tenant_login')

    locations = Location.objects.all().order_by('name')
    results = None
    searched = None
    error = ''

    landmark_id = request.GET.get('landmark')
    radius_text = request.GET.get('radius')
    gender = request.GET.get('gender', '')

    if landmark_id and radius_text:
        try:
            radius = float(radius_text)
            landmark = Location.objects.get(id=landmark_id)
            if radius <= 0:
                raise ValueError
        except (ValueError, Location.DoesNotExist):
            error = 'Please choose a landmark and enter a valid radius in km.'
        else:
            hostels = Hostel.objects.all()
            if gender in ('B', 'G', 'C'):
                hostels = hostels.filter(gender_preference=gender)
            results = []
            for h in hostels:
                d = haversine_km(landmark.latitude, landmark.longitude, h.latitude, h.longitude)
                if d <= radius:
                    rooms = h.room_set.all()
                    results.append({
                        'hostel': h,
                        'distance': round(d, 2),
                        'vacant': rooms.filter(is_vacant=True).count(),
                        'total': rooms.count(),
                    })
            results.sort(key=lambda r: r['distance'])
            searched = {'landmark': landmark, 'radius': radius_text, 'gender': gender}

    return render(request, 'core/tenant_home.html', {
        'tenant': tenant, 'locations': locations, 'results': results,
        'searched': searched, 'error': error,
        'sel_landmark': landmark_id, 'sel_radius': radius_text or '5', 'sel_gender': gender,
    })


def hostel_detail(request, hostel_id):
    tenant = get_logged_in_tenant(request)
    if not tenant:
        return redirect('tenant_login')
    hostel = get_object_or_404(Hostel, id=hostel_id)
    rooms = hostel.room_set.order_by('room_number')
    nearby = []
    for loc in Location.objects.all():
        d = haversine_km(loc.latitude, loc.longitude, hostel.latitude, hostel.longitude)
        if d <= 5:
            nearby.append({'name': loc.name, 'distance': round(d, 2)})
    nearby.sort(key=lambda x: x['distance'])
    amenity_list = [a.strip() for a in hostel.amenities.split(',') if a.strip()]
    return render(request, 'core/hostel_detail.html', {
        'tenant': tenant, 'hostel': hostel, 'rooms': rooms,
        'nearby': nearby, 'amenity_list': amenity_list,
        'vacant': rooms.filter(is_vacant=True).count(), 'total': rooms.count(),
    })


def tenant_logout(request):
    request.session.flush()
    return redirect('index')

def edit_room(request, room_id):
    owner = get_logged_in_owner(request)
    if not owner:
        return redirect('owner_login')
    room = get_object_or_404(Room, id=room_id, hostel__owner=owner)
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES, instance=room)
        if form.is_valid():
            form.save()
            return redirect('manage_rooms', hostel_id=room.hostel.id)
    else:
        form = RoomForm(instance=room)
    return render(request, 'core/edit_room.html', {'form': form, 'room': room, 'hostel': room.hostel})


def delete_room(request, room_id):
    owner = get_logged_in_owner(request)
    if not owner:
        return redirect('owner_login')
    room = get_object_or_404(Room, id=room_id, hostel__owner=owner)
    hostel_id = room.hostel.id
    if request.method == 'POST':
        room.delete()
    return redirect('manage_rooms', hostel_id=hostel_id)