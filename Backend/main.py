from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from google.auth import compute_engine

from pydantic import BaseModel
import requests
import ee  # Earth Engine
import pandas as pd
import datetime
import asyncio

import json
import os
import shutil  # Add this line to import shutil
from dotenv import load_dotenv
from typing import List

# Cargar variables de entorno
load_dotenv()


# Inicializar la API de Earth Engine
try:
    ee.Initialize(project='ee-luisfernandordzdmz')
except Exception as e:
    ee.Authenticate()
    ee.Initialize(project='ee-luisfernandordzdmz')


app = FastAPI(
    title="Chinampa API",
    description="API para proporcionar información agrícola basada en datos meteorológicos y satelitales",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas las URLs, cambiar a lista específica de dominios en producción
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos HTTP (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los headers
)


# Directorio donde se almacenarán las imágenes
IMAGE_DIR = "uploaded_images"
MAX_IMAGES = 10  # Número máximo de imágenes permitidas

# Crear el directorio si no existe
os.makedirs(IMAGE_DIR, exist_ok=True)

# Clase para recibir la ubicación
class Location(BaseModel):
    latitude: float
    longitude: float

# API Key de OpenWeatherMap (asegúrate de mantenerla segura)
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Cargar el archivo CSV de evapotranspiración al iniciar la aplicación
try:
    forecast_df = pd.read_csv('evapotranspiration_forecast_2023-2024.csv', parse_dates=['Unnamed: 0'])
    forecast_df.rename(columns={'Unnamed: 0': 'date'}, inplace=True)
    forecast_df.set_index('date', inplace=True)
except Exception as e:
    raise RuntimeError(f"Error al cargar el archivo CSV de evapotranspiración: {e}")


def initialize_earth_engine():
    """Inicializa Earth Engine en el contexto actual."""
    try:
        ee.Initialize()
    except Exception as e:
        print(f"Earth Engine ya está inicializado o falló al inicializar: {e}")


def get_weather_data(lat, lon, start_date_str, end_date_str):
    """
    Obtiene datos meteorológicos históricos y actuales.

    Args:
        lat (float): Latitud.
        lon (float): Longitud.
        start_date_str (str): Fecha de inicio en formato 'YYYY-MM-DD'.
        end_date_str (str): Fecha de fin en formato 'YYYY-MM-DD'.

    Returns:
        dict: Diccionario con los datos meteorológicos.
    """
    try:
        # Datos históricos de Open-Meteo
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
            raise Exception("Error al obtener datos históricos de Open-Meteo.")

        daily_data = historical_data['daily']
        temps_max = daily_data.get('temperature_2m_max', [])
        temps_min = daily_data.get('temperature_2m_min', [])
        precipitations = daily_data.get('precipitation_sum', [])

        # Calcular temperatura promedio y precipitación total
        avg_temps = [
            (max_temp + min_temp) / 2
            for max_temp, min_temp in zip(temps_max, temps_min)
            if max_temp is not None and min_temp is not None
        ]
        avg_temp_last_days = sum(avg_temps) / len(avg_temps) if avg_temps else None
        total_precip_last_days = sum(p for p in precipitations if p is not None) if precipitations else None

        # Datos actuales de OpenWeatherMap
        openweather_url = (
            f"https://api.openweathermap.org/data/2.5/weather?"
            f"lat={lat}&lon={lon}&units=metric&appid={OPENWEATHER_API_KEY}"
        )
        openweather_response = requests.get(openweather_url)
        openweather_data = openweather_response.json()

        if openweather_response.status_code != 200:
            raise Exception("Error al obtener datos actuales de OpenWeatherMap.")

        current_temp = openweather_data['main']['temp']
        current_precip = openweather_data.get('rain', {}).get('1h', 0)

        return {
            "current_temperature_centigrades": round(current_temp, 2),
            "current_precipitation_mm": round(current_precip, 2),
            "average_temperature_last_5days_centigrades": round(avg_temp_last_days, 2) if avg_temp_last_days else None,
            "total_precipitation_last_5days_mm": round(total_precip_last_days, 2) if total_precip_last_days else None
        }

    except Exception as e:
        return {'error': f'Error al obtener datos meteorológicos: {e}'}


def get_soil_moisture_data(lat, lng, date_str, buffer=1):
    """
    Obtiene la humedad del suelo promedio en un área específica.

    Args:
        lat (float): Latitud.
        lng (float): Longitud.
        date_str (str): Fecha en formato 'YYYY-MM-DD'.
        buffer (float): Tamaño del área alrededor del punto (en grados).

    Returns:
        dict: Diccionario con la humedad del suelo promedio.
    """
    try:
        initialize_earth_engine()

        # Definir fechas
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        start_date = (date - datetime.timedelta(days=6)).strftime('%Y-%m-%d')
        end_date = (date - datetime.timedelta(days=2)).strftime('%Y-%m-%d')

        # Colección de imágenes de SMAP
        dataset = ee.ImageCollection('NASA/SMAP/SPL3SMP_E/006') \
            .filter(ee.Filter.date(start_date, end_date))
        soil_moisture_surface = dataset.select('soil_moisture_am')

        # Región de interés
        region = ee.Geometry.Rectangle([lng - buffer, lat - buffer, lng + buffer, lat + buffer])

        # Reducir región para obtener el promedio
        stats = soil_moisture_surface.mean().reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=region,
            scale=10000,
            maxPixels=1e9
        )
        soil_moisture_value = stats.getInfo()
        mean_soil_moisture = soil_moisture_value.get('soil_moisture_am', None)

        return {'mean_soil_moisture': mean_soil_moisture}

    except Exception as e:
        return {'error': f'Error al obtener datos de humedad del suelo: {e}'}


def get_closest_available_ndvi(lat, lng, start_date, end_date, max_retries=3):
    """
    Busca el NDVI promedio más cercano hacia atrás si no encuentra un valor en el rango dado.

    Args:
        lat (float): Latitud.
        lng (float): Longitud.
        start_date (str): Fecha de inicio en formato 'YYYY-MM-DD'.
        end_date (str): Fecha de fin en formato 'YYYY-MM-DD'.
        max_retries (int): Máximo número de intentos hacia atrás para buscar un valor NDVI válido.

    Returns:
        dict: Diccionario con el NDVI promedio.
    """
    try:
        initialize_earth_engine()
        # Formatear fechas y restar un año por ahora por falta de datos
        # current_start = datetime.strptime(start_date, '%Y-%m-%d')
        # current_end = datetime.strptime(end_date, '%Y-%m-%d')
        current_start = datetime.datetime.strptime(start_date, '%Y-%m-%d') - datetime.timedelta(days=365)
        current_end = datetime.datetime.strptime(end_date, '%Y-%m-%d') - datetime.timedelta(days=365)

        for retry in range(max_retries):
            # Colección de imágenes de MODIS
            dataset = ee.ImageCollection('MODIS/061/MYD13A1') \
                .filter(ee.Filter.date(current_start.strftime('%Y-%m-%d'), current_end.strftime('%Y-%m-%d'))) \
                .select('NDVI')
            point = ee.Geometry.Point([lng, lat])

            # Reducir para obtener el promedio
            ndvi_mean = dataset.mean().reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=point,
                scale=500,
                maxPixels=1e9
            )
            ndvi_value = ndvi_mean.getInfo()
            mean_ndvi = ndvi_value.get('NDVI', None)

            # Si se encuentra un valor válido, se devuelve
            if mean_ndvi is not None:
                return {'mean_ndvi': mean_ndvi, 'reintentos para obtener nvdi cercano': retry}

            # Si no se encuentra, busca hacia atrás (por ejemplo, 5 días antes)
            current_start -= datetime.timedelta(days=5)
            current_end -= datetime.timedelta(days=5)
            print(f"Retry {retry + 1}: Buscando NDVI en rango {current_start} - {current_end}")

        return {'mean_ndvi': None, 'error': 'No se encontró NDVI en los rangos especificados'}

    except Exception as e:
        return {'error': f'Error al obtener datos de NDVI: {e}'}


def get_average_et(start_date, end_date):
    """
    Obtiene la evapotranspiración promedio entre dos fechas utilizando el archivo CSV.

    Args:
        start_date (str): Fecha de inicio en formato 'YYYY-MM-DD'.
        end_date (str): Fecha de fin en formato 'YYYY-MM-DD'.

    Returns:
        float: Valor promedio de evapotranspiración.
    """
    try:
        # Convertir fechas a datetime
        start_date_dt = pd.to_datetime(start_date)
        end_date_dt = pd.to_datetime(end_date)

        # Ajustar fechas al índice más cercano
        start_date_adjusted = forecast_df.index[forecast_df.index.get_indexer([start_date_dt], method='nearest')][0]
        end_date_adjusted = forecast_df.index[forecast_df.index.get_indexer([end_date_dt], method='nearest')][0]

        # Filtrar y calcular promedio
        filtered_df = forecast_df.loc[start_date_adjusted:end_date_adjusted]
        avg_et = filtered_df['mean'].mean()

        return avg_et

    except Exception as e:
        return {'error': f'Error al obtener datos de evapotranspiración: {e}'}

@app.post("/get_report")
async def get_report(location: Location):
    """
    Endpoint que genera un reporte agrícola basado en múltiples fuentes de datos.

    Args:
        location (Location): Objeto con latitud y longitud.

    Returns:
        dict: Reporte con datos meteorológicos, humedad del suelo, NDVI y evapotranspiración.
    """
    try:
        lat = location.latitude
        lon = location.longitude

        # Fechas actuales y rango de fechas
        date = datetime.datetime.utcnow()
        date_str = date.strftime('%Y-%m-%d')
        start_date = (date - datetime.timedelta(days=5)).strftime('%Y-%m-%d')
        end_date = (date - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        print(f"Fecha inicial: {start_date}, Fecha final: {end_date}")
        print(f"Fecha actual: {date_str}")
        print(f"Fecha final: {end_date}")

        # Crear tareas asíncronas para paralelizar
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(None, get_weather_data, lat, lon, start_date, end_date),
            loop.run_in_executor(None, get_soil_moisture_data, lat, lon, date_str, 1),
            loop.run_in_executor(None, get_closest_available_ndvi, lat, lon, start_date, end_date ),
            loop.run_in_executor(None, get_average_et, start_date, end_date)
        ]

        # Esperar a que todas las tareas completen
        weather_data, soil_moisture_data, ndvi_data, average_et = await asyncio.gather(*tasks)

        # Construir el reporte final
        report = {
            'weather_data': weather_data,
            'soil_moisture_data': soil_moisture_data,
            'ndvi_data': ndvi_data,
            'average_evapotranspiration': average_et
        }

        return report

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



def save_image(file: UploadFile):
    """
    Guarda la imagen en el directorio temporal.

    Args:
        file (UploadFile): La imagen subida por el usuario.

    Returns:
        str: La ruta de la imagen guardada.
    """
    # Generar la ruta de almacenamiento
    file_path = os.path.join(IMAGE_DIR, file.filename)
    
    # Guardar la imagen en el directorio temporal
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_path

def manage_image_queue():
    """
    Mantiene solo las últimas `MAX_IMAGES` imágenes en el directorio.
    Si se supera el límite, elimina la imagen más antigua.
    """
    # Obtener la lista de imágenes en el directorio
    images = sorted(os.listdir(IMAGE_DIR), key=lambda x: os.path.getctime(os.path.join(IMAGE_DIR, x)))
    
    # Si hay más de `MAX_IMAGES`, eliminar las más antiguas
    if len(images) > MAX_IMAGES:
        for image in images[:-MAX_IMAGES]:
            os.remove(os.path.join(IMAGE_DIR, image))


@app.post("/upload_image")
async def upload_image(file: UploadFile = File(...)):
    """
    Endpoint para cargar una imagen y realizar la detección de enfermedades.
    
    Args:
        file (UploadFile): La imagen a subir.

    Returns:
        dict: Resultado de la inferencia y detalles de la imagen.
    """
    try:
        # Verificar que el archivo es una imagen
        if file.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(status_code=400, detail="Solo se permiten imágenes JPEG o PNG.")

        # Guardar la imagen
        file_path = save_image(file)

        # Gestionar la cola de imágenes
        manage_image_queue()

        # Realizar la "inferencia" (placeholder)
        # Aquí deberías implementar tu lógica de inferencia real con el modelo de visión
        disease_detected = "No disease detected"  # Placeholder

        return {
            "filename": file.filename,
            "path": file_path,
            "disease": disease_detected
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
