from django import forms
from .models import Attendee, Company

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'contact_email', 'contact_phone']


class AttendeeForm(forms.ModelForm):
    class Meta:
        model = Attendee
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone',
            'company',
            'position',
            'participant_type',
        ]

# Formulario para inscripción grupal (varios asistentes para una empresa)
AttendeeFormSet = forms.modelformset_factory(
    Attendee,
    form=AttendeeForm,
    extra=3,  # Por defecto, 3 asistentes, se puede ajustar
    can_delete=True
)
