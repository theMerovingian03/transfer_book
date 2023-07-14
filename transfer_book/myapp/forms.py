from django import forms

# Reording Form and View

class PositionForm(forms.Form):
    position = forms.CharField()