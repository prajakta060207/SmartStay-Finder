from django import forms
from .models import Tenant, Owner, Hostel, Room


class TenantSignupForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = ['name', 'phone', 'gender', 'email', 'password']


class OwnerSignupForm(forms.ModelForm):
    class Meta:
        model = Owner
        fields = ['name', 'hostel_business_name', 'phone', 'email', 'password']


class HostelForm(forms.ModelForm):
    AMENITY_CHOICES = [
        ('Water Cooler', 'Water Cooler'),
        ('Washing Machine', 'Washing Machine'),
        ('Iron/Press', 'Iron/Press'),
        ('Laundry', 'Laundry'),
        ('Geyser', 'Geyser'),
        ('Induction', 'Induction'),
        ('Fridge', 'Fridge'),
        ('WiFi', 'WiFi'),
        ('AC', 'AC'),
    ]
    amenities_list = forms.MultipleChoiceField(
        choices=AMENITY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Amenities',
    )

    class Meta:
        model = Hostel
        fields = [
            'name', 'address', 'latitude', 'longitude', 'gender_preference',
            'rent', 'rent_increase_frequency', 'rent_increase_amount',
            'bond_required', 'bond_months',
            'food_included', 'meal_timings',
            'tiffin_available', 'tiffin_timing',
            'gate_opening_time', 'gate_closing_time',
            'visitors_policy', 'guest_stay_policy',
            'facilities', 'cleaning_frequency',
            'electricity_included', 'policies', 'contact_number',
        ]
        labels = {
            'name': 'Hostel / PG name',
            'address': 'Address (for display)',
            'gender_preference': 'Hostel type',
            'rent': 'Monthly rent (Rs)',
            'rent_increase_frequency': 'Rent increase',
            'rent_increase_amount': 'Increase amount (Rs, only if rent increases)',
            'bond_required': 'Bond period applicable?',
            'bond_months': 'Bond months (only if bond applicable)',
            'food_included': 'Meals included?',
            'meal_timings': 'Meal timings (point-wise, e.g. 1. Breakfast 7-9am)',
            'tiffin_available': 'Tiffin available?',
            'tiffin_timing': 'Tiffin timing',
            'gate_opening_time': 'Gate opening time',
            'gate_closing_time': 'Gate closing time',
            'visitors_policy': 'Visitors policy',
            'guest_stay_policy': 'Guest stay policy (family/friends staying)',
            'facilities': 'Facilities (e.g. pick & drop to bus stand)',
            'cleaning_frequency': 'Cleaning frequency',
            'electricity_included': 'Electricity bill included?',
            'policies': 'Other policies (deposit return etc.)',
            'contact_number': 'Contact number',
        }
        help_texts = {
            'latitude': 'Google Maps: right-click your hostel, click the numbers shown (e.g. 22.7196, 75.8577). Paste the FIRST number here.',
            'longitude': 'Paste the SECOND number here.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs['rows'] = 3

    def save(self, commit=True):
        hostel = super().save(commit=False)
        hostel.amenities = ', '.join(self.cleaned_data.get('amenities_list', []))
        if commit:
            hostel.save()
        return hostel


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_number', 'is_vacant', 'expected_vacancy_date', 'photo']
        labels = {
            'room_number': 'Room number',
            'is_vacant': 'Vacant right now?',
            'expected_vacancy_date': 'Expected vacancy date (only if occupied)',
            'photo': 'Recent room photo',
        }
        widgets = {
            'expected_vacancy_date': forms.DateInput(attrs={'type': 'date'}),
        }