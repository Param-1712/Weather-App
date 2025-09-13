from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
from weather_service import WeatherService
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

# Initialize weather service
weather_service = WeatherService()

@app.route('/')
def index():
    """Serve the main dashboard page"""
    return send_from_directory('../frontend', 'index.html')

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

# Serve static files (CSS, JS, images)
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('../frontend', filename)

if __name__ == '__main__':
    print("🌤️  Weather Dashboard API Starting...")
    print("📍 Frontend: http://localhost:5001")
    print("🔗 API: http://localhost:5001/api/weather?city=delhi")
    app.run(debug=True, host='0.0.0.0', port=5001)