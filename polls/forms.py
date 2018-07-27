from django import forms
from polls.models import User

class UserForm(forms.ModelForm):
    name = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'Name'}))
    email = forms.EmailField(label='', widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    class meta:
        model = User
        fields = '__all__'

class RequiredFormSet(forms.BaseModelFormSet):
    def clean(self):
        if any(self.errors):
            return
        if not self.forms[0].has_changed():
            raise forms.ValidationError('Please add at least one user details.') 

UserFormSet = forms.modelformset_factory(
    User,
    fields=('name', 'email'),
    form = UserForm,
    formset = RequiredFormSet
)
