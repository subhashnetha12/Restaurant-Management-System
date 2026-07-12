from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory

from .models import Inventory, PurchaseOrder, PurchaseOrderItem, PurchasePayment, StockMovement, Vendor


class InventoryItemChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.item_name


class DateInput(forms.DateInput):
    input_type = 'date'


class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['item_name', 'quantity', 'min_quantity', 'unit']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['quantity'].help_text = 'Changing this creates a stock adjustment audit entry.'


class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['name', 'contact_person', 'phone_number', 'email', 'address', 'gst_number', 'is_active']


class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['number', 'vendor', 'purchase_date', 'status', 'notes']
        widgets = {'purchase_date': DateInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vendor'].queryset = Vendor.objects.filter(is_active=True) | Vendor.objects.filter(pk=getattr(self.instance, 'vendor_id', None))
        self.fields['status'].choices = [choice for choice in PurchaseOrder.STATUS_CHOICES if choice[0] != 'received']
        self.fields['number'].help_text = 'Automatically generated; you can replace it with the supplier invoice or PO number.'

class PurchaseOrderItemForm(forms.ModelForm):
    inventory_item = InventoryItemChoiceField(queryset=Inventory.objects.none(), label='Stock item')

    class Meta:
        model = PurchaseOrderItem
        fields = ['inventory_item', 'quantity_ordered', 'quantity_received', 'unit', 'unit_cost']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['inventory_item'].queryset = Inventory.objects.all()
        self.fields['inventory_item'].help_text = 'Select the stock master item; enter only the quantity being purchased below.'

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('quantity_received', 0) > cleaned.get('quantity_ordered', 0):
            raise ValidationError('Quantity received cannot exceed quantity ordered.')
        if self.instance.pk and cleaned.get('quantity_received', 0) < self.instance.quantity_posted:
            raise ValidationError('Quantity received cannot be lower than stock already posted.')
        return cleaned


PurchaseOrderItemFormSet = inlineformset_factory(
    PurchaseOrder,
    PurchaseOrderItem,
    form=PurchaseOrderItemForm,
    extra=3,
    can_delete=True,
)


class PurchasePaymentForm(forms.ModelForm):
    class Meta:
        model = PurchasePayment
        fields = ['payment_date', 'amount', 'payment_method', 'reference_number', 'notes']
        widgets = {'payment_date': DateInput()}


class MovementForm(forms.Form):
    movement_type = forms.ChoiceField(choices=[choice for choice in StockMovement.MOVEMENT_CHOICES if choice[0] in (
        StockMovement.KITCHEN_ISSUE, StockMovement.WASTAGE, StockMovement.RETURN_VENDOR,
    )])
    quantity = forms.DecimalField(max_digits=12, decimal_places=3, min_value=0.001)
    reference_number = forms.CharField(max_length=100, required=False)
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
