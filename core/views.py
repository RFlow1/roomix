from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy, reverse
from django.views import View
from django.shortcuts import render, redirect
from .models import Listing, Profile, ListingImage
from .utils import compatibility_score
from django.contrib import messages


class ListingListView(ListView):
    model = Listing
    template_name = 'core/listing_list.html'
    context_object_name = 'listings'
    paginate_by = 12

    def get_queryset(self):
        qs = Listing.objects.select_related('owner').prefetch_related('images')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(title__icontains=q) | qs.filter(location__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            viewer_profile = self.request.user.profile
            scores = {}
            for listing in context['listings']:
                try:
                    score, disqualified = compatibility_score(viewer_profile, listing.owner.profile)
                    scores[listing.pk] = {'score': score, 'disqualified': disqualified}
                except Profile.DoesNotExist:
                    scores[listing.pk] = None
            context['scores'] = scores
        return context


class ListingDetailView(DetailView):
    model = Listing
    template_name = 'core/listing_detail.html'
    context_object_name = 'listing'

    def get_queryset(self):
        return Listing.objects.select_related('owner__profile').prefetch_related('images')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            try:
                score, disqualified = compatibility_score(
                    self.request.user.profile,
                    self.object.owner.profile
                )
                context['compatibility'] = {'score': score, 'disqualified': disqualified}
            except Profile.DoesNotExist:
                context['compatibility'] = None
        return context


class ListingCreateView(LoginRequiredMixin, CreateView):
    model = Listing
    template_name = 'core/listing_form.html'
    fields = ['title', 'description', 'price', 'location', 'available_from']
    login_url = '/accounts/login/'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        for image in self.request.FILES.getlist('images'):
            ListingImage.objects.create(listing=self.object, image=image)
        return response

    def get_success_url(self):
        return reverse('listing-detail', kwargs={'pk': self.object.pk})


class ListingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Listing
    template_name = 'core/listing_form.html'
    fields = ['title', 'description', 'price', 'location', 'available_from']

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in self.request.FILES.getlist('images'):
            ListingImage.objects.create(listing=self.object, image=image)
        return response

    def get_success_url(self):
        return reverse('listing-detail', kwargs={'pk': self.object.pk})

    def test_func(self):
        return self.get_object().owner == self.request.user


class ListingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Listing
    template_name = 'core/listing_confirm_delete.html'
    success_url = reverse_lazy('home')

    def test_func(self):
        return self.get_object().owner == self.request.user


class RegisterView(View):
    def get(self, request):
        form = UserCreationForm()
        return render(request, 'registration/register.html', {'form': form})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
        return render(request, 'registration/register.html', {'form': form})


class ProfileView(LoginRequiredMixin, View):
    LIFESTYLE_FIELDS = [
        ('is_smoker', 'Smoker'),
        ('has_pets', 'Has pets'),
        ('is_student', 'Student'),
    ]

    IMPORTANCE_FIELDS = [
        ('cleanliness_importance', 'Cleanliness'),
        ('sleep_schedule_importance', 'Sleep Schedule'),
        ('budget_importance', 'Budget'),
        ('smoker_importance', 'Smoking'),
        ('pets_importance', 'Pets'),
    ]

    def get(self, request):
        return render(request, 'core/profile.html', {
            'profile': request.user.profile,
            'lifestyle_fields': self.LIFESTYLE_FIELDS,
            'importance_fields': self.IMPORTANCE_FIELDS,
            'importance_choices': Profile.IMPORTANCE_CHOICES,
        })

    def post(self, request):
        profile = request.user.profile
        profile.bio = request.POST.get('bio', '')
        profile.location = request.POST.get('location', '')
        profile.age = request.POST.get('age') or None
        profile.budget_min = request.POST.get('budget_min') or None
        profile.budget_max = request.POST.get('budget_max') or None
        profile.sleep_schedule = request.POST.get('sleep_schedule', '')
        profile.cleanliness = request.POST.get('cleanliness') or None
        for field, _ in self.LIFESTYLE_FIELDS:
            setattr(profile, field, field in request.POST)
        for field, _ in self.IMPORTANCE_FIELDS:
            setattr(profile, field, request.POST.get(field, 1))
        if 'image' in request.FILES:
            profile.image = request.FILES['image']
        profile.full_clean()
        profile.save()
        messages.success(request, 'Profile updated!')
        return redirect('profile')