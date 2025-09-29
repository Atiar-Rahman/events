from django.urls import reverse_lazy
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Count
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from events.models import Event, Category
from .forms import EventForm, CategoryForm
from django.views.generic import ListView,DetailView,CreateView,UpdateView
from django.contrib.auth.mixins import PermissionRequiredMixin
# Group checkers (for RBAC)
def is_user(user):
    return user.groups.filter(name='user').exists()

def is_organizer(user):
    return user.groups.filter(name='organizer').exists()

# Home page (latest events)
def home(request):
    events = Event.objects.select_related('category').prefetch_related('participants').all()[:9]
    return render(request, 'events/home.html', {'events': events})


# Event list with search/filter
class EventListView(ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'

    def get_queryset(self):
        queryset = Event.objects.select_related('category').prefetch_related('participants').all()

        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | Q(location__icontains=search_query)
            )

        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])

        return queryset

# Event detail
class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'
    pk_url_kwarg = 'id'

    def get_queryset(self):
        return Event.objects.select_related('category').prefetch_related('participants')

# Event create

class EventCreateView(PermissionRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    success_url = reverse_lazy('event_list')

    # PermissionRequiredMixin settings
    permission_required = 'events.add_event'
    login_url = 'no-permession'  # your custom no-permission page

    def form_valid(self, form):
        form.save()  # Explicit save
        return super().form_valid(form)
# Event update

class EventUpdateView(PermissionRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    success_url = reverse_lazy('event_list')
    permission_required = 'events.change_event'
    login_url = 'no-permession'
    pk_url_kwarg = 'id'  # So it matches your URL param

    def form_valid(self, form):
        form.save()  # Explicit save
        return super().form_valid(form)
# Event delete
@permission_required('events.delete_event', login_url='no-permession')
def event_delete(request, id):
    event = get_object_or_404(Event, id=id)
    if request.method == 'POST':
        event.delete()
        return redirect('event_list')
    return render(request, 'events/event_confirm_delete.html', {'event': event})


# Dashboard
@permission_required('events.view_event', login_url='no-permession')
def dashboard(request):
    today = timezone.now().date()
    counts = {
        'events': Event.objects.aggregate(
            total=Count('id'),
            upcoming=Count('id', filter=Q(date__gte=today)),
            past=Count('id', filter=Q(date__lt=today)),
        ),
        'categories': Category.objects.aggregate(total=Count('id')),
        'users': {
            'total': Event.participants.through.objects.count()  # number of RSVP entries
        }
    }

    data = Event.objects.select_related('category').prefetch_related('participants')
    type = request.GET.get('type', 'all')
    data_type = 'events'

    if type == 'upcoming':
        data = data.filter(date__gte=today)
        data_type = 'upcoming_events'
    elif type == 'past':
        data = data.filter(date__lt=today)
        data_type = 'past_events'
    elif type == 'categories':
        data = Category.objects.annotate(event_count=Count('events'))
        data_type = 'categories'

    return render(request, 'events/dashboard.html', {
        'counts': counts,
        'data': data,
        'data_type': data_type,
    })


# RSVP to Event
@login_required
def rsvp_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.user in event.participants.all():
        messages.warning(request, "You have already RSVP’d to this event.")
    else:
        event.participants.add(request.user)
        messages.success(request, "RSVP successful. A confirmation email has been sent.")

        # Send email
        send_mail(
            subject="RSVP Confirmation",
            message=f"Hi {request.user.username},\n\nYou've successfully RSVP’d for '{event.name}'.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[request.user.email],
            fail_silently=True
        )

    return redirect('event_detail', id=event.id)


# RSVP'd Events
@login_required
def my_rsvped_events(request):
    rsvped_events = request.user.rsvped_events.all()
    return render(request, 'events/my_events.html', {'events': rsvped_events})

@login_required
def cancel_rsvp(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.user in event.participants.all():
        event.participants.remove(request.user)
    return redirect('participant-dashboard') 

# Category list
def category_list(request):
    categories = Category.objects.annotate(event_count=Count('events'))
    return render(request, 'events/category_list.html', {'categories': categories})


# Category create

class CategoryCreateView(PermissionRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'events/category_form.html'
    success_url = reverse_lazy('category_list')

    permission_required = 'events.add_category'
    login_url = 'no-permession'

    def form_valid(self, form):
        form.save()  # Explicit form save as in FBV
        return super().form_valid(form)

# Category update
@permission_required('events.change_category', login_url='no-permession')
def category_update(request, id):
    category = get_object_or_404(Category, id=id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'events/category_form.html', {'form': form})


# Category delete
@permission_required('events.delete_category', login_url='no-permession')
def category_delete(request, id):
    category = get_object_or_404(Category, id=id)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')
    return render(request, 'events/category_confirm_delete.html', {'category': category})


# No permission page
def no_permession(request):
    return render(request, 'no_permession.html')


@login_required
def participant_dashboard(request):
    user = request.user
    rsvped_events = user.rsvped_events.all()  #rsvped_events the related name m2m
    return render(request, 'participant_dashboard.html', {'events': rsvped_events})




@login_required
def dashboard_redirect(request):
    user = request.user

    if user.groups.filter(name='admin').exists():
        return redirect('admin-dashboard')
    elif user.groups.filter(name='organizer').exists():
        return redirect('dashboard')
    else:
        return redirect('participant-dashboard')
    
