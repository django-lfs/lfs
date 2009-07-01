# django imports
from django import forms
from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.core.utils import get_default_shop
from lfs.customer.models import Address

class OnePageCheckoutForm(forms.Form):
    """
    """
    invoice_firstname = forms.CharField(label=_(u"Firstname"), max_length=50)
    invoice_lastname = forms.CharField(label=_(u"Lastname"), max_length=50)
    invoice_street = forms.CharField(label=_(u"Street"), max_length=100)
    invoice_zip_code = forms.CharField(label=_(u"Zip Code"), max_length=10)
    invoice_city = forms.CharField(label=_(u"City"), max_length=50)
    invoice_state = forms.CharField(label=_(u"State"), max_length=50)
    invoice_country = forms.ChoiceField(label=_(u"Country"))
    invoice_phone = forms.CharField(label=_(u"Phone"), max_length=20)
    invoice_email = forms.EmailField(label=_(u"E-mail"), required=False, max_length=50)
    
    shipping_firstname = forms.CharField(label=_(u"Firstname"), required=False, max_length=50)
    shipping_lastname = forms.CharField(label=_(u"Lastname"), required=False, max_length=50)
    shipping_street = forms.CharField(label=_(u"Street"), required=False, max_length=100)
    shipping_zip_code = forms.CharField(label=_(u"Zip Code"), required=False, max_length=10)
    shipping_city = forms.CharField(label=_(u"City"), required=False, max_length=50)
    shipping_state = forms.CharField(label=_(u"State"), required=False, max_length=50)
    shipping_country = forms.ChoiceField(label=_(u"Country"), required=False)
    shipping_phone = forms.CharField(label=_(u"Phone"), required=False, max_length=20)

    account_number = forms.CharField(label=_(u"Account Number"), required=False, max_length=30)
    bank_identification_code = forms.CharField(label=_(u"Bank Indentification Code"), required=False, max_length=30)
    bank_name = forms.CharField(label=_(u"Bankname"), required=False, max_length=100)
    depositor = forms.CharField(label=_(u"Depositor"), required=False, max_length=100)
    
    payment_method = forms.CharField(required=False, max_length=1)
    
    # credit_card_type = forms.CharField(required=False, max_length=30)
    # credit_card_owner = forms.CharField(required=False, max_length=100)
    # credit_card_number = forms.CharField(required=False, max_length=30)
    # credit_card_expiration_date_month = forms.IntegerField(required=False)
    # credit_card_expiration_date_year = forms.IntegerField(required=False)
    
    no_shipping = forms.BooleanField(label=_(u"Same as invoice"), initial=True, required=False)
    message = forms.CharField(label=_(u"Your message to us"), widget=forms.Textarea(attrs={'cols':'80;'}), required=False)

    def __init__(self, *args, **kwargs):
        super(OnePageCheckoutForm, self).__init__(*args, **kwargs)
        
        shop = get_default_shop()
        self.fields["invoice_country"].choices = [(c.id, c.name) for c in shop.countries.all()]
        self.fields["shipping_country"].choices = [(c.id, c.name) for c in shop.countries.all()]
        
    def clean(self):
        """
        """
        msg = _(u"This field is required.")
        
        if self.data.get("is_anonymous") == "1" and \
           not self.cleaned_data.get("invoice_email"):
            self._errors["invoice_email"] = ErrorList([msg])

        if not self.cleaned_data.get("no_shipping"):
            if self.cleaned_data.get("shipping_firstname", "") == "":
                self._errors["shipping_firstname"] = ErrorList([msg])

            if self.cleaned_data.get("shipping_lastname", "") == "":
                self._errors["shipping_lastname"] = ErrorList([msg])

            if self.cleaned_data.get("shipping_street", "") == "":
                self._errors["shipping_street"] = ErrorList([msg])

            if self.cleaned_data.get("shipping_zip_code", "") == "":
                self._errors["shipping_zip_code"] = ErrorList([msg])

            if self.cleaned_data.get("shipping_city", "") == "":
                self._errors["shipping_city"] = ErrorList([msg])

            if self.cleaned_data.get("shipping_country", "") == "":
                self._errors["shipping_country"] = ErrorList([msg])
                
        # 1 == Direct Debit
        if self.data.get("payment_method") == "1":
            if self.cleaned_data.get("account_number", "") == "":
                self._errors["account_number"] = ErrorList([msg])
            
            if self.cleaned_data.get("bank_identification_code", "") == "":
                self._errors["bank_identification_code"] = ErrorList([msg])

            if self.cleaned_data.get("bank_name", "") == "":
                self._errors["bank_name"] = ErrorList([msg])

            if self.cleaned_data.get("depositor", "") == "":
                self._errors["depositor"] = ErrorList([msg])
        
        return self.cleaned_data