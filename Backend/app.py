from fastapi import FastAPI, HTTPException
import requests
from pydantic import BaseModel
import datetime

app = FastAPI(
    title="Asistente Agrícola",
    description="API para proporcionar información agrícola basada en datos meteorológicos",
    version="1.0.0"
)

class Location(BaseModel):
    latitude: float
    longitude: float

# Configura tu API Key de OpenWeatherMap
OPENWEATHER_API_KEY = '72e74dde0bf1d5edd318eb3acfbd7350'

@app.post("/get_report")
def get_report(location: Location):
    try:
        lat = location.latitude
        lon = location.longitude

        # Fechas para datos históricos
        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=5)
        end_date = today - datetime.timedelta(days=1)  # Hasta ayer para garantizar datos completos

        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        # URL para datos históricos diarios de Open-Meteo
        historical_url = (
            f"https://archive-api.open-meteo.com/v1/archive?"
            f"latitude={lat}&longitude={lon}"
            f"&start_date={start_date_str}&end_date={end_date_str}"
            f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
            f"&timezone=UTC"
        )

        historical_response = requests.get(historical_url)
        historical_data = historical_response.json()

        if 'daily' not in historical_data:
            raise HTTPException(status_code=400, detail="Error al obtener datos históricos.")

        daily_data = historical_data['daily']

        # Verificar que los datos estén presentes y manejar posibles None
        temps_max = daily_data.get('temperature_2m_max', [])
        temps_min = daily_data.get('temperature_2m_min', [])
        precipitations = daily_data.get('precipitation_sum', [])

        # Filtrar valores None en temperaturas y calcular promedio
        avg_temps = []
        for max_temp, min_temp in zip(temps_max, temps_min):
            if max_temp is not None and min_temp is not None:
                avg_temp = (max_temp + min_temp) / 2
                avg_temps.append(avg_temp)

        if avg_temps:
            avg_temp_last_days = sum(avg_temps) / len(avg_temps)
        else:
            avg_temp_last_days = None

        # Filtrar valores None en precipitaciones y calcular total
        valid_precipitations = [p for p in precipitations if p is not None]
        if valid_precipitations:
            total_precip_last_days = sum(valid_precipitations)
        else:
            total_precip_last_days = None

        # Usar OpenWeatherMap para obtener la precipitación actual
        openweather_url = (
            f"https://api.openweathermap.org/data/2.5/weather?"
            f"lat={lat}&lon={lon}&units=metric&appid={OPENWEATHER_API_KEY}"
        )

        openweather_response = requests.get(openweather_url)
        openweather_data = openweather_response.json()

        if openweather_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Error al obtener datos actuales de OpenWeatherMap.")

        current_temp = openweather_data['main']['temp']

        # Obtener la precipitación actual si está disponible
        current_precip = 0
        if 'rain' in openweather_data and '1h' in openweather_data['rain']:
            current_precip = openweather_data['rain']['1h']

        # Construir el reporte
        report = {
            "current_temperature_centigrades": round(current_temp, 2),
            "current_precipitation_mm": round(current_precip, 2),
            "average_temperature_last_5days_centigrades": round(avg_temp_last_days, 2) if avg_temp_last_days is not None else None,
            "total_precipitation_last_5days_mm": round(total_precip_last_days, 2) if total_precip_last_days is not None else None
        }

        return report

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
