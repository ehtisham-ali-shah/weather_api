from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.templating import Jinja2Templates
import httpx

app = FastAPI()
templates = Jinja2Templates(directory="templates")
weather_data_global = []

city_coordinates = {
    'Karachi': (24.8607, 67.0011), # (latitude, longitude)
    'Lahore': (31.5497, 74.3436),
    'Faisalabad': (31.4504, 73.1350),
    'Rawalpindi': (33.6844, 73.0479),
    'Multan': (30.1575, 71.5249),
    'Peshawar': (34.0150, 71.5249),
    'Quetta': (30.1798, 66.9750),
    'Sialkot': (32.5358, 74.3359),
    'Islamabad': (33.6844, 73.0479),
    'Gujranwala': (32.1617, 74.1883)
}

@app.get("/search_weather")
async def search_weather(query: str = ""):
    try:
        query = query.lower()
        filtered_data = [entry for entry in weather_data_global if query in f"{entry['latitude']},{entry['longitude']}"]
        return filtered_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/weather_data")
async def weather_data(cities: list[str] = Query([], title="List of Cities"), request: Request=None):
    url = "https://api.open-meteo.com/v1/forecast"
    cities = [q_city for q_city in cities if q_city in city_coordinates.keys()]
    default_cities = set(['Karachi', 'Lahore'] + cities)
    weather_data = []

    async with httpx.AsyncClient() as client:
        for city, coordinates in city_coordinates.items():
            if city in default_cities:
                lat, lon = coordinates
                params = {
                    "latitude": lat,
                    "longitude": lon,
                    "daily": "temperature_2m_min,temperature_2m_max,wind_speed_10m_max,wind_direction_10m_dominant,sunrise,sunset",
                    "timezone": "Asia/Karachi"
                }
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    data.update({'city': city})
                    weather_data.append(data)

    return templates.TemplateResponse("weather_list.html", {"request": request, "weather_data": weather_data,
                                    'selectable_cities': [city for city in city_coordinates.keys() if city not in default_cities],
                                    'selected_cities': list(set(cities))})
