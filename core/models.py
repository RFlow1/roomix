from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)  

    
    budget_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    location = models.CharField(max_length=255, blank=True)  
    is_smoker = models.BooleanField(default=False)
    has_pets = models.BooleanField(default=False)
    is_student = models.BooleanField(default=True)

    CLEANLINESS_CHOICES = [
        (1, 'Messy'),
        (2, 'Average'),
        (3, 'Very Clean'),
    ]
    cleanliness = models.IntegerField(choices=CLEANLINESS_CHOICES, null=True, blank=True)

    SLEEP_CHOICES = [
        ('early', 'Early Bird'),
        ('night', 'Night Owl'),
    ]
    sleep_schedule = models.CharField(max_length=10, choices=SLEEP_CHOICES, blank=True)
    image = models.ImageField(upload_to='profile_pics/', default='default_profile.jpg')
    created_at = models.DateTimeField(auto_now_add=True)  

    IMPORTANCE_CHOICES = [
        (0 , 'Not Important'),
        (1 , 'Somewhat Important'),
        (2 , 'Very Important'),
        (3 , 'Must Match'),

    ]
    cleanliness_importance = models.IntegerField(choices=IMPORTANCE_CHOICES , default=1)
    sleep_schedule_importance = models.IntegerField(choices=IMPORTANCE_CHOICES , default=1)
    budget_importance = models.IntegerField(choices=IMPORTANCE_CHOICES , default=1)
    smoker_importance = models.IntegerField(choices=IMPORTANCE_CHOICES , default=1)
    pets_importance = models.IntegerField(choices=IMPORTANCE_CHOICES , default=1)
    



    def clean(self):
        # Validate budget range makes sense
        if self.budget_min and self.budget_max:
            if self.budget_min > self.budget_max:
                raise ValidationError("budget_min cannot be greater than budget_max.")

    def __str__(self):
        return self.user.username


class Listing(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='listings'  
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  
    location = models.CharField(max_length=255)
    available_from = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  

    class Meta:
        ordering = ['-created_at']  
    def get_absolute_url(self):
        return reverse('listing-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title


class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='listing_pics/')
    order = models.PositiveSmallIntegerField(default=0)  
    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Image for {self.listing.title}"