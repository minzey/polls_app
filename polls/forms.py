from django import forms
from polls.models import User

class UserForm(forms.ModelForm):
    name = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'Name'}))
    email = forms.EmailField(label='', widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    class meta:
        model = User
        fields = '__all__'

# class NoEmptyFormsAllowedBaseFormSet(forms.BaseFormSet):
#     def clean(self):
#         print('here')
#         if not self.has_changed():
#             print('empty formset!!!!!!!')
#             raise forms.ValidationError("Please enter atleast one user details")

# class RequiredFormSet(BaseFormSet):
#     def __init__(self, *args, **kwargs):
#         super(RequiredFormSet, self).__init__(*args, **kwargs)
#         self.forms[0].empty_permitted = False


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
