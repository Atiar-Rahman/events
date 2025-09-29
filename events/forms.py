
from django import forms
from django.contrib.auth.models import User
from events.models import Event, Category


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'date', 'time', 'location', 'category','asset']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter event name', 'class': 'w-full border rounded px-3 py-2'}),
            'description': forms.Textarea(attrs={'placeholder': 'Enter event description', 'class': 'w-full border rounded px-3 py-2', 'rows': 3}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full border rounded px-3 py-2'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'w-full border rounded px-3 py-2'}),
            'location': forms.TextInput(attrs={'placeholder': 'Enter location', 'class': 'w-full border rounded px-3 py-2'}),
            'category': forms.Select(attrs={'class': 'w-full border rounded px-3 py-2'}),
        }


class RSVPForm(forms.Form):
    event = forms.ModelChoiceField(
        queryset=Event.objects.all(),
        widget=forms.Select(attrs={'class': 'w-full border rounded px-3 py-2'})
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_event(self):
        event = self.cleaned_data['event']
        if self.user in event.participants.all():
            raise forms.ValidationError("You have already RSVP'd to this event.")
        return event


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter category name', 'class': 'w-full border rounded px-3 py-2'}),
            'description': forms.Textarea(attrs={'placeholder': 'Enter description', 'class': 'w-full border rounded px-3 py-2', 'rows': 3}),
        }
