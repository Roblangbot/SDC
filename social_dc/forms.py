# forms.py
from django import forms
from .models import ProductTable, ColorTable, ProdNameTable, PriceTable, CustomerTable, SalesAddressTable

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

    productimage = forms.CharField(required=True)

    class Meta:
        model = ProductTable
        fields = ['prodnameid', 'colorid', 'priceid', 'productimage']


class CustomerForm(forms.ModelForm):
    class Meta:
        model = CustomerTable
        fields = ['firstname', 'lastname', 'contactno', 'email']


class AddressForm(forms.ModelForm):
    class Meta:
        model = SalesAddressTable
        fields = [
            'block_number', 'lot_number', 'house_number', 'unit_number',
            'street_name', 'subdivision', 'barangayid', 'postal_code', 'city_municipalityid',
            'provinceid', 'regionid', 'countryid', 'delivery_instructions'
        ]