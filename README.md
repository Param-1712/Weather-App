🌤 Weather Dashboard Pro

A full-stack weather dashboard application that provides real-time weather insights with an elegant UI and intelligent backend processing.
Built with Flask (backend) and Vanilla JS + HTML/CSS (frontend) using the Open-Meteo API.

📂 Project Structure
weather-proj/
│
├── backend/
│   ├── app.py              # Flask server (API + static file serving)
│   ├── weather_service.py  # WeatherService class (API integration + suggestions)
│
├── frontend/
│   ├── index.html          # Main weather dashboard UI
│
└── README.md

✨ Features
🔹 Frontend

Modern, responsive weather dashboard UI.

City search with real-time weather updates.

Displays:

🌡 Temperature

💨 Wind Speed & Direction

🌧 Rain Probability

🕒 Time awareness (day/night)

Smart suggestions for misspelled or ambiguous city names.

Voice support:

🔊 Read weather aloud.

📥 Download audio as .mp3.

🔹 Backend

Flask API with endpoints:

/api/weather → Get weather for a city.

/api/health → Health check endpoint.

Uses Open-Meteo APIs:

Geocoding API → Resolve city names.

Forecast API → Fetch real-time weather.

Intelligent city matching:

✅ Fuzzy search for misspelled cities.

✅ Predefined aliases for Indian states.

✅ Alternative city suggestions.

Smart time-aware weather suggestions (day/night, rain, heat, cold, wind).
