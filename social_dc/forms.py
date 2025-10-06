# forms.py
from django import forms
from .models import ProductTable, ColorTable, ProdNameTable, PriceTable, CustomerTable, SalesAddressTable, PaymentTable, SalesTable

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
            'full_address',
            'latitude',
            'longitude',
            'delivery_instructions',
        ]

class CombinedStatusForm(forms.Form):
    itemstatusid = forms.ModelChoiceField(
        queryset=SalesTable._meta.get_field('itemstatusid').related_model.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    paystatid = forms.ModelChoiceField(
        queryset=PaymentTable._meta.get_field('paystatid').related_model.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    salesid = forms.IntegerField(widget=forms.HiddenInput())
    paymentid = forms.IntegerField(widget=forms.HiddenInput())

class ProdNameForm(forms.ModelForm):
    class Meta:
        model = ProdNameTable
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter product name'}),
        }
