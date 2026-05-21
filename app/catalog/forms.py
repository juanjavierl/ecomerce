from django import forms
from PIL import Image, UnidentifiedImageError
from app.catalog.models import *
from django.core.exceptions import ValidationError
import phonenumbers

class ClientFormOrder(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['names'].widget.attrs['autofocus'] = True

    class Meta:
        model = Client
        exclude = ('gender','date_joined',)
        #fields = '__all__'

    def clean_mobile(self):
        mobile = self.cleaned_data['mobile']
        try:
            parsed = phonenumbers.parse(mobile, None)
            if not phonenumbers.is_valid_number(parsed):
                raise ValidationError("Número de teléfono inválido.")
        except:
            raise ValidationError("Ingrese un número válido con su código de país.")
        
        return mobile

class formUpdateProducto(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['autofocus'] = True
    
    def clean_image(self):
        image = self.cleaned_data.get('image')

        if image:
            try:
                # Intentar abrir con Pillow para verificar si realmente es una imagen
                img = Image.open(image)
                img.verify()  # Lanza error si no es una imagen válida

                # Validar el formato permitido
                formato_permitido = ['JPEG', 'JPG', 'PNG', 'WEBP']
                if img.format.upper() not in formato_permitido:
                    raise forms.ValidationError("Formato de imagen no permitido. Solo se permiten JPG, PNG o WEBP.")

            except UnidentifiedImageError:
                raise forms.ValidationError("El archivo no es una imagen válida.")
            except Exception:
                raise forms.ValidationError("Error al procesar la imagen.")
        return image

    class Meta:
        model = Product
        exclude = ['company', 'salida', 'date_joined', 'stock']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea({'class': 'form-control', 'rows': 2, 'cols': 3}),
           
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'price_before': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'})
        }

class formProducto(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['autofocus'] = True

    class Meta:
        model = Product
        exclude = ['company', 'salida', 'date_joined']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea({'class': 'form-control', 'rows': 2, 'cols': 3}),
           
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'price_before': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'})
        }

class formCategory(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['autofocus'] = True

    class Meta:
        model = Category
        #exclude = ('gender','date_joined','email',)
        fields = '__all__'

class FormLike(forms.ModelForm):
    class Meta:
        model = Like
        exclude = ('company','date_joined')

class FormImgProducto(forms.ModelForm):
    class Meta:
        model = Imagen
        exclude = ('items',)