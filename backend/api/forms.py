from django import forms
from .models import Asistente, Empresa

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['nombre_empresa', 'email_contacto', 'celular_contacto']


class AttendeeForm(forms.ModelForm):
    class Meta:
        model = Asistente
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone',
            'profile_type',
        ]

class CargaPreacreditacionForm(forms.Form):
    archivo = forms.FileField(
        label="Archivo PREACREDITACION EMPRESAS.xlsx",
        help_text="Seleccione un archivo oficial de Excel (.xlsx) con un tamaño máximo de 5MB.",
        widget=forms.FileInput(attrs={
            'accept': '.xlsx, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'style': 'padding: 8px; border: 1px solid #ccc; border-radius: 6px; width: 100%; max-width: 500px;'
        })
    )

    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if archivo:
            if not archivo.name.lower().endswith('.xlsx'):
                raise forms.ValidationError("El archivo debe tener extensión exclusivamente .xlsx.")
            if archivo.size > 5 * 1024 * 1024:
                raise forms.ValidationError("El tamaño del archivo no puede superar los 5MB.")
        return archivo
