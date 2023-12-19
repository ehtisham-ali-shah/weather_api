from fastapi import FastAPI, Request,HTTPException
from fastapi.templating import Jinja2Templates
import httpx

app = FastAPI()
templates = Jinja2Templates(directory="templates")
weather_data_global = []

@app.get("/search_weather")
async def search_weather(query: str = ""):
    try:
        query = query.lower()
        filtered_data = [entry for entry in weather_data_global if query in f"{entry['latitude']},{entry['longitude']}"]
        return filtered_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/weather_data")
async def weather_data(request: Request):
    url = "https://api.open-meteo.com/v1/forecast"
    latitudes = [24.8607, 31.5204] # and other latitudes
    longitudes = [67.0011, 74.3587] # and other longitudes
    weather_data_global = []

    async with httpx.AsyncClient() as client:
        for lat, lon in zip(latitudes, longitudes):
            params = {
                "latitude": lat,
                "longitude": lon,
                "daily": "temperature_2m_min,temperature_2m_max,wind_speed_10m_max,wind_direction_10m_dominant,sunrise,sunset",
                "timezone": "Asia/Karachi"
            }
            response = await client.get(url, params=params)
            if response.status_code == 200:
                weather_data_global.append(response.json())

    return templates.TemplateResponse("weather_list.html", {"request": request, "weather_data": weather_data_global})
