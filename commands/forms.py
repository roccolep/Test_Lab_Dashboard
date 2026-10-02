from django import forms
from .models import Command

class CommandForm(forms.ModelForm):
    class Meta:
        model = Command
        fields = ['name', 'payload', 'priority']

    def clean_payload(self):
        payload = self.cleaned_data.get('payload')
        if payload is None:
            raise forms.ValidationError("Payload is required.")
        if not isinstance(payload, dict):
            raise forms.ValidationError("Payload must be a JSON object.")
        return payload