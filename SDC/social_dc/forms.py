# forms.py
from django import forms
from .models import ProductTable, ColorTable, ProdNameTable, PriceTable

class ProductForm(forms.ModelForm):
    prodnameid = forms.ModelChoiceField(
        queryset=ProdNameTable.objects.all().order_by('-prodnameid'),  # newest first
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    colorid = forms.ModelChoiceField(
        queryset=ColorTable.objects.all().order_by('colorname'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    priceid = forms.ModelChoiceField(
        queryset=PriceTable.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = ProductTable
        fields = ['prodnameid', 'colorid', 'priceid', 'productimage']