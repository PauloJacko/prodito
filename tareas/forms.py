from django import forms

from .models import Etiqueta, Meta, Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "titulo",
            "descripcion",
            "fecha",
            "hora",
            "fecha_fin",
            "hora_fin",
            "etiquetas",
            "meta",
        ]
        widgets = {
            "fecha": forms.TextInput(attrs={"class": "form-control flatpickr-date"}),
            "hora": forms.TextInput(attrs={"class": "form-control flatpickr-time"}),
            "fecha_fin": forms.TextInput(
                attrs={"class": "form-control flatpickr-date"}
            ),
            "hora_fin": forms.TextInput(attrs={"class": "form-control flatpickr-time"}),
            "descripcion": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            "etiquetas": forms.CheckboxSelectMultiple(),
            "meta": forms.Select(attrs={"class": "form-control"}),
        }


class MetaForm(forms.ModelForm):
    class Meta:
        model = Meta
        fields = ["titulo", "descripcion", "fecha_limite", "completada"]


class EtiquetaForm(forms.ModelForm):
    class Meta:
        model = Etiqueta
        fields = ["nombre", "color"]
        widgets = {
            "color": forms.TextInput(attrs={"type": "color"}),
        }
