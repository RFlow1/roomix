from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('', views.ListingListView.as_view(), name='home'),
    path('listings/', views.ListingListView.as_view(), name='listing-list'),
    path('listings/<int:pk>/', views.ListingDetailView.as_view(), name='listing-detail'),

    # Login required
    path('listings/create/', views.ListingCreateView.as_view(), name='listing-create'),
    path('listings/<int:pk>/edit/', views.ListingUpdateView.as_view(), name='listing-edit'),
    path('listings/<int:pk>/delete/', views.ListingDeleteView.as_view(), name='listing-delete'),

    # Auth
    path('accounts/register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),

    #Messaging
    path('messages/' , views.InboxView.as_view(), name='inbox'),
    path('messages/<int:pk>/', views.ConversationView.as_view(), name='conversation'),
    path('messages/start/<int:listing_pk>/', views.StartConversationView.as_view(), name='start-conversation'),
    path('messages/unread/', views.UnreadCountView.as_view(), name='unread-count'),
    path('messages/<int:pk>/poll/', views.PollMessagesView.as_view(), name='poll-messages'),
]
