import ee
import pandas as pd
from datetime import datetime, timedelta

# Inicializar Earth Engine
ee.Authenticate()
ee.Initialize(project='ee-luisfernandordzdmz')

def get_weekly_et_data(lat, lng, start_year, end_year):
    # Definir la colección de imágenes de evapotranspiración
    dataset = ee.ImageCollection('MODIS/061/MOD16A2GF').select('ET')

    # Definir la región de interés
    point = ee.Geometry.Point([lng, lat])

    # Crear un DataFrame para almacenar los resultados
    et_data = []

    # Iterar por cada año y semana
    for year in range(start_year, end_year + 1):
        start_date = datetime(year, 1, 1)
        for week in range(1, 53):  # 52 semanas en un año
            # Definir el rango de fechas para la semana
            week_start = start_date + timedelta(weeks=week - 1)
            week_end = week_start + timedelta(days=6)

            # Filtrar la colección por el rango de fechas
            weekly_dataset = dataset.filter(ee.Filter.date(week_start.strftime('%Y-%m-%d'), week_end.strftime('%Y-%m-%d')))

            # Reducir la colección para obtener el promedio ET
            et_mean = weekly_dataset.mean().reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=point,
                scale=500,
                maxPixels=1e9
            ).getInfo()

            # Guardar los datos
            et_value = et_mean.get('ET', None)
            et_data.append({'year': year, 'week': week, 'et_value': et_value})
            print(f"Año {year}, Semana {week}, ET: {et_value}")

    return pd.DataFrame(et_data)

# Parámetros de entrada
latitude = 19.127083  # Latitud de entrada
longitude = -99.49475  # Longitud de entrada
start_year = 2015  # Año inicial
end_year = 2023  # Año final

# Obtener datos semanales de evapotranspiración
et_df = get_weekly_et_data(latitude, longitude, start_year, end_year)

# Guardar como CSV
et_df.to_csv('evapotranspiration_weekly.csv', index=False)
print("Datos de evapotranspiración guardados como CSV")
