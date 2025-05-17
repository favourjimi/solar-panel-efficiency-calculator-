
import streamlit as st
import requests 
import plotly.graph_objs as go
from datetime import datetime

st.set_page_config(page_title="Solar Panel Efficiency Calculator", page_icon="☀️", layout="wide")

st.title("Solar Panel Efficiency Calculator")

st.markdown("Estimate your solar panel efficiency using real-time weather data.")

#--- Inputs ----
city = st.text_input("Enter the city name:", "New York")
api_key = st.text_input("Enter your API key:", type="password")
panel_power = st.number_input("Enter the power of your solar panel (in watts):", min_value=10,max_value=7,value=400, step=0.1)
efficiency = st.slider("Panel Efficiency (%)",10,25,18)

#--- Get Coordinates from city Name---
def get_coordinates(city, api_key):
  url = f"http://api.openweathermap.org/geo/1.0/direct?q={city},{state},US&limit=1&appid={api_key}"
  response = requests.get(url)
  data = response.json()
  if data:
    lat = data[0]['lat']
    lon = data[0]['lon']
    return lat, lon
  else:
    return None, None

#--- GET WEATHER DATA ----
def get_weather_data(lat, lon,  api_key):
  url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
  response = requests.get(url)
  data = response.json()
  return data

#--- Calculate Energy Output ----
def calculate_energy_output(panel_power, efficiency, irradiance,num_panels,sunlight_hours):
  total_kw = (panel_power * num_panels) / 1000
  output = total_kw * efficiency * irradiance * sunlight_hours
  return output
  
#---- Main Exwcution ---
if city and api_key:
  lat, lon = get_coordinates(city, state, api_key)
  if lat is not None and lon is not None:
    weather_data = get_weather_data(city, api_key)
    if weather_data:
      # Approximate daily sunlight hours and irradiance from cloud cover
      cloud_cover = weather_data['clouds']['all']
      temperature = weather_data['main']['temp']
      base_irradiance = 5.0 #Average for moderate sunlight
      irradiance = base_irradiance * (1 - cloud_cover/100) #simple approximation
      sunlight_hours =12*(1-cloud_cover/100)

      daily_output = calculate_energy_output(panel_power, efficiency, irradiance, num_panels, sunlight_hours)
      monthly_output = daily_output * 30
      annual_output = monthly_output * 12
      co2_saved = daily_output * 0.92
      
      #Display Results
      st.header("🔋😊Estimated Output")
      st.write(f"Daily Output: {daily_output:.2f} kWh")
      st.write(f"Monthly Output: {monthly_output:.2f} kWh")
      st.write(f"Annual Output: {annual_output:.2f} kWh")
      st.write(f"CO2 Saved/day: {co2_saved:.2f} kg")

      #visualization
      labels = ['Daily Output', 'Monthly Output', 'Annual Output']
      values = [daily_output, monthly_output, annual_output]
      fig =go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3)])
      fig.add_trace(go.Bar(x=labels, y=values, marker_color='rgb(0, 150, 105)'))
      fig.update_layout(title_text="Energy Output Breakdown")
      st.plotly_chart(fig)
    else:
      st.error("couldn't fetch weather data. Please check your API key and try again.")
  else:
      st.error("Invalid city or state name. Please try again.")
else:
  st.warning("Please enter all required information.")
 
