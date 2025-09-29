from django.urls import path
from events.views import *
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('re-dashboard/', dashboard_redirect, name='dashboard_redirect'),
    path('no-permession', no_permession, name='no-permession'),
    path('participant-dashboard/', participant_dashboard, name='participant-dashboard'),
    # Events
    # path('events/', event_list, name='event_list'),
    path('events/', EventListView.as_view(), name='event_list'),
    # path('events/<int:id>/', event_detail, name='event_detail'),
    path('events/<int:id>/', EventDetailView.as_view(), name='event_detail'),
    # path('events/add/', event_create, name='event_create'),
    path('events/add/', EventCreateView.as_view(), name='event_create'),
    # path('events/<int:id>/edit/', event_update, name='event_update'),
    path('events/<int:id>/edit/', EventUpdateView.as_view(), name='event_update'),
    path('events/<int:id>/delete/', event_delete, name='event_delete'),

    # RSVP (based on User <-> Event M2M)
    path('events/<int:event_id>/rsvp/', rsvp_event, name='rsvp-event'),
    path('cancel-rsvp/<int:event_id>/', cancel_rsvp, name='cancel-rsvp'),

    # Category
    path('categories/', category_list, name='category_list'),
    # path('categories/add/', category_create, name='category_create'),
    path('categories/add/', CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:id>/edit/', category_update, name='category_update'),
    path('categories/<int:id>/delete/', category_delete, name='category_delete'),

    # Participant Dashboard (NEW: shows RSVP'd events for logged-in user)
    path('my-events/', my_rsvped_events, name='my-rsvped-events'),
]



# Serve media files only during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)