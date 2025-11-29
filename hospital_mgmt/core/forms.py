from django import forms

class CSVUploadForm(forms.Form):
    file = forms.FileField(label="Upload Transport Network CSV", help_text="Format: Source, Destination, Capacity")

class FlowSearchForm(forms.Form):
    source_city = forms.CharField(label="Source District", max_length=100, widget=forms.TextInput(attrs={'placeholder': 'e.g. Dhaka'}))
    sink_city = forms.CharField(label="Destination District", max_length=100, widget=forms.TextInput(attrs={'placeholder': 'e.g. Chittagong'}))Q