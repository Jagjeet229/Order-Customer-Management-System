from django import forms
from myapp.models import Order, Client

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['client', 'product', 'num_units']
        widgets = {'client': forms.RadioSelect}
        labels = {'num_units': u'Quantity', 'client': u'Client Name'}


class InterestForm(forms.Form):
    interested = forms.BooleanField(label="Interested", widget=forms.RadioSelect(choices=[(1, 'Yes'), (0, 'No'), ]), required=False)
    quantity = forms.IntegerField(label="Quantity", min_value=1, initial=1)
    comments = forms.CharField(label="Additional Comments", widget=forms.Textarea, required=False)


class RegisterationForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['username', 'password', 'email', 'first_name', 'last_name', 'interested_in']
        widgets = {'interested_in': forms.CheckboxSelectMultiple, 'password': forms.PasswordInput}
        labels = {'interested_in': 'Select the topics that you are interested in'}

class ForgotPassForm(forms.Form):
    Email = forms.EmailField()

    def __str__(self):
        return self.Email

