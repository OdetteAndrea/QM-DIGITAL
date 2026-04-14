from django import forms
from .models import Producto, Direccion


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'categoria',
                  'descripcion', 'precio', 'stock', 'imagen']

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio is not None and precio <= 0:
            raise forms.ValidationError(
                "El precio del producto debe ser mayor a 0.")
        return precio

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is not None and stock < 0:
            raise forms.ValidationError(
                "El stock no puede ser un número negativo.")
        return stock


class DireccionForm(forms.ModelForm):
    class Meta:
        model = Direccion
        fields = ['alias', 'calle', 'comuna', 'telefono_contacto']
