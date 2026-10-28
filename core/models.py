from django.db import models

class Owner(models.Model):
    name = models.CharField(max_length=100)
    hostel_business_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=10)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.name

class Tenant(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=10)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=150)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name

class Hostel(models.Model):
    GENDER_PREF_CHOICES = [
        ('B', 'Boys'),
        ('G', 'Girls'),
        ('C', 'Co-ed'),
    ]
    INCREASE_FREQ_CHOICES = [
        ('N', 'No increase'),
        ('Y', 'Yearly'),
        ('M', 'Monthly'),
    ]
    CLEANING_CHOICES = [
        ('D', 'Daily'),
        ('2D', 'Every 2 days'),
        ('W', 'Weekly'),
        ('O', 'Other'),
    ]

    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    address = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    gender_preference = models.CharField(max_length=1, choices=GENDER_PREF_CHOICES)

    rent = models.PositiveIntegerField()
    rent_increase_frequency = models.CharField(max_length=1, choices=INCREASE_FREQ_CHOICES, default='N')
    rent_increase_amount = models.PositiveIntegerField(blank=True, null=True)

    bond_required = models.BooleanField(default=False)
    bond_months = models.PositiveIntegerField(blank=True, null=True)

    food_included = models.BooleanField(default=False)
    meal_timings = models.TextField(blank=True)

    tiffin_available = models.BooleanField(default=False)
    tiffin_timing = models.CharField(max_length=100, blank=True)

    gate_opening_time = models.CharField(max_length=20)
    gate_closing_time = models.CharField(max_length=20)

    visitors_policy = models.TextField(blank=True)
    guest_stay_policy = models.TextField(blank=True)

    amenities = models.CharField(max_length=255, blank=True)
    facilities = models.TextField(blank=True)
    cleaning_frequency = models.CharField(max_length=2, choices=CLEANING_CHOICES, blank=True)

    electricity_included = models.BooleanField(default=False)
    policies = models.TextField(blank=True)

    contact_number = models.CharField(max_length=10)
    cover_photo = models.ImageField(upload_to='hostel_photos/', blank=True, null=True)
    last_updated = models.DateField(auto_now=True)

    def __str__(self):
        return self.name

class Room(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE)
    room_number = models.CharField(max_length=10)
    is_vacant = models.BooleanField(default=True)
    expected_vacancy_date = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='room_photos/', blank=True, null=True)
    last_updated = models.DateField(auto_now=True)

    def __str__(self):
        return f"Room {self.room_number} - {self.hostel.name}"
# Create your models here.
