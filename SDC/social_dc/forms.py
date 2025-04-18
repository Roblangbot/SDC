# forms.py
from django import forms
from .models import ProductTable, BeigeTable, RedTable, BlueTable, GrayTable, BrownTable, YellowTable, WhiteTable, OrangeTable

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