from django.shortcuts import render
from django.views import generic,View
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
import requests
import os
class WeatherView(View):
    template_name = 'weatherapp/weather.html'
    error_template_name = 'weatherapp/error.html'

    def get_weather_data(self, city_name):

        api_key = 'c440da393b5c4c3c9de165437231812'
        api_endpoint = f'http://api.weatherapi.com/v1/current.json?key={api_key}&q={city_name}'
        api_endpoint2 = f'http://api.weatherapi.com/v1/astronomy.json?key={api_key}&q={city_name}'
        response = requests.get(api_endpoint)
        response2 = requests.get(api_endpoint2)
        print(api_key,'hey')
        if response.status_code == 200 and response.status_code == 200:
            data = response.json()

            temperature = data['current']['temp_c']
            weather_description =data['current']['condition']['text']
            country = data['location']['country']
            local_time = data['location']['localtime'][11:]
            city_name = data['location']['name']
            region = data['location']['region']
            feels_like = data['current']['feelslike_c']
            ''' getting atro data from a different request '''

            astro_data = response2.json()
            sunrise = astro_data['astronomy']['astro']['sunrise']
            sunset = astro_data['astronomy']['astro']['sunset']

            return {
                'data':data,
                'region':region,
                'feels_like':feels_like,
                'city_name':city_name,
                'country':country,
                'local_time':local_time,
                'temperature':temperature,
                'weather_description':weather_description,
                'sunrise':sunrise,
                'sunset':sunset,
            }
        
        else:
            return None
        
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    
    def post(self, request, *args, **kwargs):
        city_name = request.POST.get('city_name')
        
        if len(city_name) < 1:
           city_name = get_location(request)
        weather_data = self.get_weather_data(city_name)
        
        if weather_data:
            return render(request,self.template_name, context=weather_data)
        else:
            return render(request,self.error_template_name)

class ForecastView(View):
    template_name = 'weatherapp/forecast.html'
    error_template_name = 'weatherapp/error.html'

    def get_forecast(self,city_name,no_days):
        api_key = 'c440da393b5c4c3c9de165437231812' 
        api_endpoint = f'http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={city_name}&days={no_days}'
        response = requests.get(api_endpoint)

        if response.status_code == 200:
            data = response.json()
            forecast_data = {
            'location': f"{data['location']['name']}, {data['location']['country']}",
            'current_conditions': {
                'temperature': data['current']['temp_c'],
                'feels_like': data['current']['feelslike_c'],
                'condition': data['current']['condition']['text'],
                'wind_speed': data['current']['wind_kph'],
                'wind_direction': data['current']['wind_dir'],
                'humidity': data['current']['humidity'],
                'pressure': data['current']['pressure_mb'],
            },
            'hourly_forecast': data['forecast']['forecastday'][0]['hour'],  # Assuming hourly data for the first day
            'daily_forecast': data['forecast']['forecastday'],
            'extended_forecast': data['forecast']['forecastday'][1:],  # Exclude the first day
        }

            return {'data': forecast_data}
        
        return None
    
    def get(self,request,*args,**kwargs):
        return render(request,self.template_name)
    
    def post(self,request,*args,**kwargs):
        city_name = request.POST.get('city_name')
        no_days = request.POST.get('no_days')
        weather_data = self.get_forecast(city_name=city_name,no_days=no_days)
        if weather_data:
            return render(request,self.template_name,context=weather_data)
        return render(request,self.error_template_name)

class HomeView(generic.TemplateView):
    template_name = 'weatherapp/home.html'

class AboutUsView(generic.TemplateView):
    template_name = 'weatherapp/aboutus.html'

class SIgnUpView(generic.CreateView):
    template_name = 'Registration/signup.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('login')

class ThanksView(generic.TemplateView):
    template_name = 'weatherapp/thanks.html'

def get_client_ip(request):
    x_forwarded_for = request.headers.get('X-Forwarded-For')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_location(request):
    api_key = 'c052961846134a719b5386f834e47cd4'
    client_ip = get_client_ip(request)
    api_endpoint = f'https://ipgeolocation.abstractapi.com/v1/?api_key={api_key}&ip_address={client_ip}'
    response = requests.get(api_endpoint)
    location_data = response.json()
    print(location_data['city'],'city')
    if location_data['city']:
        return (location_data['city'].split(" ")[0])
    return None
