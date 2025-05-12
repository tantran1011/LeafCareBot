import requests
import os
from dotenv import load_dotenv

load_dotenv()
weather_api = os.getenv("WEATHER_API")

def get_weather(city: str, api_key: str = weather_api) -> dict:
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200:
            return {"error": data.get("message", "Failed to get weather")}
        
        weather_info = {
        "Địa điểm": city,
        "Mô tả": data["weather"][0]["description"],
        "Nhiệt độ (K)": data["main"]["temp"],
        "Độ ẩm (%)": data["main"]["humidity"],
        "Tốc độ gió (km/h)": data["wind"]["speed"]
        }

        return weather_info
    
    except Exception as e:
        return {"error": str(e)}