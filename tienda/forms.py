from __future__ import annotations

import datetime

from django import forms

from .models import Alquiler, Categoria, Cliente, Pelicula


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nombre", "descripcion"]


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["nombre", "email", "telefono"]


class PeliculaForm(forms.ModelForm):
    class Meta:
        model = Pelicula
        fields = ["titulo", "anio", "categoria", "precio_alquiler"]


class AlquilerCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["cliente"].queryset = Cliente.objects.filter(activo=True)

    class Meta:
        model = Alquiler
        fields = ["cliente", "pelicula"]


class MarcarPagadoForm(forms.Form):
    fecha_devolucion = forms.DateField(
        required=False,
        label="Fecha de devolución (opcional)",
        widget=forms.DateInput(attrs={"type": "date"}),
    )


class SimularVentasForm(forms.Form):
    numero_ventas = forms.IntegerField(min_value=1, max_value=200, label="Cantidad de ventas a simular")
    desde = forms.DateField(required=False, label="Desde (opcional)", widget=forms.DateInput(attrs={"type": "date"}))
    hasta = forms.DateField(required=False, label="Hasta (opcional)", widget=forms.DateInput(attrs={"type": "date"}))

    def clean(self):
        cleaned = super().clean()
        desde = cleaned.get("desde")
        hasta = cleaned.get("hasta")

        if desde and hasta and desde > hasta:
            raise forms.ValidationError("La fecha 'Desde' no puede ser posterior a 'Hasta'.")

        if not desde and not hasta:
            today = datetime.date.today()
            cleaned["desde"] = today
            cleaned["hasta"] = today

        return cleaned