from django import forms

class AskForm(forms.Form):
    title  = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'size' : 80, 'autocomplete' : 'off'}))
    text   = forms.CharField(widget=forms.Textarea(attrs={'id':'editor'}))
    tags   = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'size' : 60, 'autocomplete' : 'off'}))
    openid = forms.CharField(required=False, max_length=255, widget=forms.TextInput(attrs={'size' : 40, 'class':'openid-input'}))
    user   = forms.CharField(required=False, max_length=255, widget=forms.TextInput(attrs={'size' : 35}))
    email  = forms.CharField(required=False, max_length=255, widget=forms.TextInput(attrs={'size' : 35}))
    
class AnswerForm(forms.Form):
    text   = forms.CharField(widget=forms.Textarea(attrs={'id':'editor'}))
    openid = forms.CharField(required=False, max_length=255, widget=forms.TextInput(attrs={'size' : 40, 'class':'openid-input'}))
    user   = forms.CharField(required=False, max_length=255, widget=forms.TextInput(attrs={'size' : 35}))
    email  = forms.CharField(required=False, max_length=255, widget=forms.TextInput(attrs={'size' : 35}))