from django import forms
from .models import Task, Meta, Etiqueta

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['titulo', 'descripcion', 'fecha', 'hora', 'etiquetas', 'meta']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'etiquetas': forms.CheckboxSelectMultiple(),
        }

class MetaForm(forms.ModelForm):
    class Meta:
        model = Meta
        fields = ['titulo', 'descripcion', 'fecha_limite', 'completada']

class EtiquetaForm(forms.ModelForm):
    class Meta:
        model = Etiqueta
        fields = ['nombre', 'color']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
        }