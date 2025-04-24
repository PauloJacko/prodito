from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['titulo', 'descripcion', 'fecha', 'hora', 'etiquetas']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'etiquetas': forms.CheckboxSelectMultiple(),
        }