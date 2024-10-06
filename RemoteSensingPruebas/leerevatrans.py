import pandas as pd

# Cargar el CSV con el pronóstico
forecast_df = pd.read_csv('evapotranspiration_forecast_2023-2024.csv', parse_dates=['Unnamed: 0'])
forecast_df.rename(columns={'Unnamed: 0': 'date'}, inplace=True)
forecast_df.set_index('date', inplace=True)

# Verificar la estructura de los datos
print(forecast_df.head())

# Función para consultar el promedio de evapotranspiración en un rango de fechas
def get_average_et(start_date, end_date):
    # Convertir las fechas de entrada a formato datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Ajustar las fechas al índice más cercano si no existen registros exactos
    start_date_adjusted = forecast_df.index[forecast_df.index.get_indexer([start_date], method='nearest')][0]
    end_date_adjusted = forecast_df.index[forecast_df.index.get_indexer([end_date], method='nearest')][0]
    
    # Filtrar el rango de fechas ajustado
    filtered_df = forecast_df.loc[start_date_adjusted:end_date_adjusted]
    
    # Calcular el promedio de los valores predichos (columna 'mean')
    avg_et = filtered_df['mean'].mean()
    
    return avg_et

# Ejemplo de uso: consultar el promedio de evapotranspiración entre fechas cercanas
start_date = '2024-09-30'
end_date = '2024-10-04'
average_et = get_average_et(start_date, end_date)
print(f"Promedio de evapotranspiración entre {start_date} y {end_date}: {average_et:.2f}")
