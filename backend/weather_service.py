import requests
from datetime import datetime, timezone
import pytz

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

            # Get timezone info if available
            timezone_info = geo_response["results"][0].get("timezone", "Asia/Kolkata")

            # Add precipitation probability to request
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current_weather": True,
                "hourly": ["precipitation_probability"],
                "timezone": timezone_info
            }

            weather_response = requests.get(self.base_weather_url, params=params, timeout=10).json()
            current = weather_response["current_weather"]

            # Get precipitation probability for the current hour
            current_time = current["time"]
            precip_prob = None
            try:
                idx = weather_response["hourly"]["time"].index(current_time)
                precip_prob = weather_response["hourly"]["precipitation_probability"][idx]
            except (ValueError, KeyError, IndexError):
                precip_prob = 0

            # Determine if it's day or night
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
            # Parse the time string (format: "2024-01-01T15:00")
            dt = datetime.fromisoformat(current_time_str.replace('Z', '+00:00'))
            
            # Convert to local timezone
            if timezone_str:
                try:
                    local_tz = pytz.timezone(timezone_str)
                    local_time = dt.astimezone(local_tz)
                except:
                    # Fallback to Asia/Kolkata if timezone parsing fails
                    local_tz = pytz.timezone('Asia/Kolkata')
                    local_time = dt.astimezone(local_tz)
            else:
                # Default to Asia/Kolkata
                local_tz = pytz.timezone('Asia/Kolkata')
                local_time = dt.astimezone(local_tz)
            
            hour = local_time.hour
            # Consider 6 AM to 6 PM as daytime
            return 6 <= hour < 18
            
        except Exception:
            # Fallback: assume daytime if we can't determine
            return True

    def give_time_aware_suggestion(self, temp, windspeed, precip_prob, is_daytime):
        """Enhanced suggestion function that considers time of day"""
        
        # Rain suggestions (same for day/night)
        if precip_prob is not None and precip_prob > 70:
            return "🌧 High chance of rain. Carry an umbrella!"
        
        # Temperature-based suggestions
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
        
        # Wind-based suggestions
        elif windspeed > 30:
            if is_daytime:
                return "💨 Strong winds during the day. Be cautious outdoors and secure loose items."
            else:
                return "🌙💨 Strong winds at night. Stay indoors and ensure windows are secure."
        
        # Pleasant weather suggestions
        else:
            if is_daytime:
                return "🌤 Weather looks pleasant. Great time for outdoor activities!"
            else:
                return "🌙✨ Pleasant evening/night. Perfect for a peaceful walk or outdoor relaxation."

# Alternative version without pytz dependency (simpler approach)
class SimpleWeatherService:
    def _init_(self):
        self.base_geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        self.base_weather_url = "https://api.open-meteo.com/v1/forecast"
    
    def get_weather(self, city_name):
        """Simplified version without external timezone libraries"""
        try:
            geo_url = f"{self.base_geo_url}?name={city_name}&count=1"
            geo_response = requests.get(geo_url, timeout=10).json()

            if "results" not in geo_response or not geo_response["results"]:
                return {"error": f"City '{city_name}' not found"}

            latitude = geo_response["results"][0]["latitude"]
            longitude = geo_response["results"][0]["longitude"]
            location_name = geo_response["results"][0]["name"]

            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current_weather": True,
                "hourly": ["precipitation_probability"],
                "timezone": "Asia/Kolkata"  # You can change this based on your needs
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

            # Simple day/night detection based on hour
            hour = int(current_time.split('T')[1].split(':')[0])
            is_daytime = 6 <= hour < 18

            return {
                "success": True,
                "city": location_name,
                "temperature": current["temperature"],
                "wind_speed": current["windspeed"],
                "wind_direction": current["winddirection"],
                "precipitation_probability": precip_prob,
                "time": current_time,
                "hour": hour,
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

    def give_time_aware_suggestion(self, temp, windspeed, precip_prob, is_daytime):
        """Time-aware suggestions without external dependencies"""
        
        if precip_prob is not None and precip_prob > 70:
            return "🌧 High chance of rain. Carry an umbrella!"
        
        if temp > 35:
            if is_daytime:
                return "🥵 Very hot outside. Stay hydrated and avoid peak sun hours (11 AM - 4 PM)."
            else:
                return "🌙🥵 Hot night ahead. Stay hydrated and use fans or AC for comfort."
        
        elif temp < 10:
            if is_daytime:
                return "🧣 Cold day. Wear warm clothes and enjoy some winter sunshine."
            else:
                return "🌙❄ Cold night. Bundle up in warm layers and stay cozy indoors."
        
        elif windspeed > 30:
            if is_daytime:
                return "💨 Windy day. Be careful with outdoor activities and secure loose items."
            else:
                return "🌙💨 Windy night. Best to stay indoors and keep windows secured."
        
        else:
            if is_daytime:
                return "🌤 Pleasant day. Perfect weather for outdoor activities!"
            else:
                return "🌙✨ Beautiful night. Great for evening walks or stargazing."

# Example usage:
# For full timezone support (requires: pip install pytz)
weather_service = WeatherService()

# For simple version (no additional dependencies)
# weather_service = SimpleWeatherService()

result = weather_service.get_weather("Delhi")
print(result)