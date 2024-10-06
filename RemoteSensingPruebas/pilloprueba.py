import ee
import requests
from PIL import Image
from io import BytesIO
from datetime import datetime, timedelta

# Inicializar la API de Earth Engine
ee.Authenticate()
ee.Initialize(project='ee-luisfernandordzdmz')


def create_soil_moisture_static_image(lat, lng, date_str, buffer=1, dimensions=128):
    # Convertir la fecha de string a objeto datetime
    date = datetime.strptime(date_str, '%Y-%m-%d')
    start_date = (date - timedelta(days=6)).strftime('%Y-%m-%d')
    end_date = (date - timedelta(days=2)).strftime('%Y-%m-%d')
    
    # Definir la colección de imágenes
    dataset = ee.ImageCollection('NASA/SMAP/SPL3SMP_E/006') \
        .filter(ee.Filter.date(start_date, end_date))

    # Seleccionar la banda de humedad del suelo
    soil_moisture_surface = dataset.select('soil_moisture_am')

    # Definir los parámetros de visualización
    soil_moisture_surface_vis = {
        'min': 0.0,
        'max': 0.5,
        'palette': ['0300ff', '418504', 'efff07', 'efff07', 'ff0303']
    }

    # Definir una región alrededor de las coordenadas
    region = ee.Geometry.Rectangle([lng - buffer, lat - buffer, lng + buffer, lat + buffer])

    # Generar la URL del thumbnail con la región especificada
    url = soil_moisture_surface.mean().getThumbURL({
        'min': soil_moisture_surface_vis['min'],
        'max': soil_moisture_surface_vis['max'],
        'palette': soil_moisture_surface_vis['palette'],
        'region': region.getInfo()['coordinates'],
        'dimensions': dimensions  # Ajustar las dimensiones para un grid 3x3
    })

    # Descargar la imagen desde la URL
    response = requests.get(url)
    soil_moisture_image = Image.open(BytesIO(response.content))

    # Guardar la imagen de humedad del suelo
    soil_moisture_filename = f'soil_moisture_image_{lat}_{lng}_{start_date}_to_{end_date}.png'
    soil_moisture_image.save(soil_moisture_filename)
    print(f"Imagen de humedad del suelo guardada como {soil_moisture_filename}")


def get_soil_moisture_data(lat, lng, date_str, buffer=1):
    # Convertir la fecha de string a objeto datetime
    date = datetime.strptime(date_str, '%Y-%m-%d')
    start_date = (date - timedelta(days=6)).strftime('%Y-%m-%d')
    end_date = (date - timedelta(days=2)).strftime('%Y-%m-%d')
    
    # Definir la colección de imágenes
    dataset = ee.ImageCollection('NASA/SMAP/SPL3SMP_E/006') \
        .filter(ee.Filter.date(start_date, end_date))

    # Seleccionar la banda de humedad del suelo
    soil_moisture_surface = dataset.select('soil_moisture_am')

    # Definir una región alrededor de las coordenadas (en grados)
    region = ee.Geometry.Rectangle([lng - buffer, lat - buffer, lng + buffer, lat + buffer])

    # Reducir la región usando una estadística (mean)
    stats = soil_moisture_surface.mean().reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=region,
        scale=10000,  # Escala en metros (ajustar según la precisión deseada)
        maxPixels=1e9  # Permitir más píxeles para una mayor región
    )

    # Obtener el valor promedio de la humedad del suelo
    soil_moisture_value = stats.getInfo()

    # Devolver los datos como diccionario
    data = {
        'latitude': lat,
        'longitude': lng,
        'buffer': buffer,
        'start_date': start_date,
        'end_date': end_date,
        'mean_soil_moisture': soil_moisture_value.get('soil_moisture_am', 'No data')
    }
    
    return data


# Ejemplo de uso con fecha dinámica
# Ejemplo de uso Texcalyacac
latitude = 19.127083333333  # Latitud de entrada
longitude = -99.49475  # Longitud de entrada

# Ejemplo Chiapas
# latitude = 16.040960
# longitude = -92.457438

date_str = '2024-10-06'  # Fecha de referencia (año-mes-día)

# Crear imagen de humedad del suelo
create_soil_moisture_static_image(latitude, longitude, date_str, buffer=1, dimensions=128)

# Obtener datos estructurados de humedad del suelo
soil_moisture_data = get_soil_moisture_data(latitude, longitude, date_str, buffer=1)
print(soil_moisture_data)


