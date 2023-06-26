from django import forms


class CityWeatherForm(forms.Form):
    city = forms.CharField(label='City weather',
                           max_length=100,
                           required=True,
                           widget=forms.TextInput(attrs={
                             'class': 'form-control',
                             'placeholder': 'Enter a city name...'
                           }))

    def clean_city(self):
        city = self.cleaned_data.get('city')
        city = city.title()
        return city
