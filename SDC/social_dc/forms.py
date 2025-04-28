# forms.py
from django import forms
from .models import ProductTable, BeigeTable

class ProductForm(forms.ModelForm):
    class Meta:
        model = ProductTable
        fields = ['productname', 'productimage', 'beigeid', 'yellowid', 'redid', 'blueid', 'orangeid', 'whiteid', 'brownid', 'grayid', ]  # and other color FKs

        widgets = {
            'productname': forms.TextInput(attrs={'class': 'form-control'}),
            'productimage': forms.TextInput(attrs={'class': 'form-control'}),
            'beigeid': forms.Select(attrs={'class': 'form-select d-none'}),  # hidden visually
            'yellowid': forms.Select(attrs={'class': 'form-select d-none'}),  # hidden visually
            'redid': forms.Select(attrs={'class': 'form-select d-none'}),  # hidden visually
            'blueid': forms.Select(attrs={'class': 'form-select d-none'}),  # hidden visually
            'orangeid': forms.Select(attrs={'class': 'form-select d-none'}),  # hidden visually
            'whiteid': forms.Select(attrs={'class': 'form-select d-none'}),  # hidden visually
            'brownid': forms.Select(attrs={'class': 'form-select d-none'}),  # hidden visually
            'grayid': forms.Select(attrs={'class': 'form-select d-none'}),  # hidden visually
        }

class variantForm(forms.Form):
    name = forms.CharField(max_length=999)  # Name of the variant
    gray_image = forms.CharField(max_length=999, required=False)  # Image URL for gray variant
    blue_image = forms.CharField(max_length=999, required=False)  # Image URL for blue variant
    red_image = forms.CharField(max_length=999, required=False)   # Image URL for red variant
    brown_image = forms.CharField(max_length=999, required=False) # Image URL for brown variant
    white_image = forms.CharField(max_length=999, required=False) # Image URL for white variant
    yellow_image = forms.CharField(max_length=999, required=False) # Image URL for yellow variant
    orange_image = forms.CharField(max_length=999, required=False) # Image URL for orange variant
    beige_image = forms.CharField(max_length=999, required=False) # Image URL for beige variant