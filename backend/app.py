from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import requests
from datetime import datetime, timezone
import pytz
import os

app = Flask(__name__)
CORS(app)

class WeatherService:
    def __init__(self):
        self.base_geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        self.base_weather_url = "https://api.open-meteo.com/v1/forecast"
    
    def get_weather(self, city_name):
        """Enhanced function with time-aware suggestions"""
        try:
            geo_url = f"{self.base_geo_url}?name={city_name}&count=1"
            geo_response = requests.get(geo_url, timeout=10).json()

            if "results" not in geo_response or not geo_response["results"]:
                return {"error": f"City '{city_name}' not found"}

            latitude = geo_response["results"][0]["latitude"]
            longitude = geo_response["results"][0]["longitude"]
            location_name = geo_response["results"][0]["name"]

            timezone_info = geo_response["results"][0].get("timezone", "Asia/Kolkata")

            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current_weather": True,
                "hourly": ["precipitation_probability"],
                "timezone": timezone_info
            }

            weather_response = requests.get(self.base_weather_url, params=params, timeout=10).json()
            current = weather_response["current_weather"]

            current_time = current["time"]
            precip_prob = None
            try:
                idx = weather_response["hourly"]["time"].index(current_time)
                precip_prob = weather_response["hourly"]["precipitation_probability"][idx]
            except (ValueError, KeyError, IndexError):
                precip_prob = 0

            is_daytime = self.is_daytime(current_time, timezone_info)

            return {
                "success": True,
                "city": location_name,
                "temperature": current["temperature"],
                "wind_speed": current["windspeed"],
                "wind_direction": current["winddirection"],
                "precipitation_probability": precip_prob,
                "time": current_time,
                "is_daytime": is_daytime,
                "suggestion": self.give_time_aware_suggestion(
                    current["temperature"], 
                    current["windspeed"], 
                    precip_prob, 
                    is_daytime
                )
            }

        except requests.exceptions.RequestException as e:
            return {"error": f"Network error: {str(e)}"}
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}

    def is_daytime(self, current_time_str, timezone_str):
        """Determine if it's currently daytime or nighttime"""
        try:
            dt = datetime.fromisoformat(current_time_str.replace('Z', '+00:00'))
            
            if timezone_str:
                try:
                    local_tz = pytz.timezone(timezone_str)
                    local_time = dt.astimezone(local_tz)
                except:
                    local_tz = pytz.timezone('Asia/Kolkata')
                    local_time = dt.astimezone(local_tz)
            else:
                local_tz = pytz.timezone('Asia/Kolkata')
                local_time = dt.astimezone(local_tz)
            
            hour = local_time.hour
            return 6 <= hour < 18
            
        except Exception:
            return True

    def give_time_aware_suggestion(self, temp, windspeed, precip_prob, is_daytime):
        """Enhanced suggestion function that considers time of day"""
        
        if precip_prob is not None and precip_prob > 70:
            return "🌧 High chance of rain. Carry an umbrella!"
        
        if temp > 35:
            if is_daytime:
                return "🥵 Very hot outside. Stay hydrated and avoid going out during peak hours (11 AM - 4 PM)."
            else:
                return "🌙 Still quite hot even at night. Stay hydrated and consider light, breathable clothing."
        
        elif temp < 10:
            if is_daytime:
                return "🧣 It's quite cold. Wear warm clothes and enjoy some sunshine if possible."
            else:
                return "🌙❄ Very cold night. Wear extra layers and stay warm indoors."
        
        elif windspeed > 30:
            if is_daytime:
                return "💨 Strong winds during the day. Be cautious outdoors and secure loose items."
            else:
                return "🌙💨 Strong winds at night. Stay indoors and ensure windows are secure."
        
        else:
            if is_daytime:
                return "🌤 Weather looks pleasant. Great time for outdoor activities!"
            else:
                return "🌙✨ Pleasant evening/night. Perfect for a peaceful walk or outdoor relaxation."

# Initialize weather service
weather_service = WeatherService()

# Read the HTML file content (you'll need to paste your HTML here)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weather Dashboard</title>
    <!-- Paste your CSS and HTML content here -->
    <style>
        /* Your CSS from index.html */
    </style>
</head>
<body>
    <!-- Your HTML body content from index.html -->
    <script>
        // Update the fetch URL to use relative path
        async function fetchWeatherData(city) {
            try {
                console.log(`Fetching weather for: ${city}`);
                const response = await fetch(`/api/weather?city=${encodeURIComponent(city)}`);
                const data = await response.json();
                
                console.log('Backend response:', data);
                
                if (!response.ok) {
                    throw new Error(data.error || 'Failed to fetch weather data');
                }
                
                return {
                    "City": data.city,
                    "Temperature (°C)": data.temperature,
                    "Wind Speed (km/h)": data.wind_speed,
                    "Wind Direction (°)": data.wind_direction,
                    "Precipitation Probability (%)": data.precipitation_probability
                };
            } catch (error) {
                console.error('API Error:', error);
                throw new Error(error.message || 'Failed to fetch weather data');
            }
        }
        
        // Rest of your JavaScript code
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """Serve the main dashboard page"""
    # For now, return a simple response. You'll need to embed your HTML here
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/weather', methods=['GET'])
def get_weather_api():
    """API endpoint for weather data"""
    city = request.args.get('city', '').strip()
    
    if not city:
        return jsonify({"error": "City name is required"}), 400
    
    result = weather_service.get_weather(city)
    
    if "error" in result:
        return jsonify(result), 404
    
    return jsonify(result)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "Weather API is running"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
