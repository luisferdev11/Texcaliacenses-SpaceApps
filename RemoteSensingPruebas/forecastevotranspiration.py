import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt

# Cargar el dataset corregido
et_df = pd.read_csv('evapotranspiration_weekly_clean.csv')

# Convertir las columnas a enteros
et_df['year'] = et_df['year'].astype(int)
et_df['week'] = et_df['week'].astype(int)

# Crear una columna de fecha combinando año y semana (ISO)
et_df['date'] = pd.to_datetime(et_df['year'].astype(str) + et_df['week'].astype(str) + '1', format='%G%V%u')

# Filtrar los datos hasta septiembre de 2023
cutoff_date = pd.to_datetime('2023-09-30')
et_df = et_df[et_df['date'] <= cutoff_date]

# Establecer la columna de fecha como índice
et_df.set_index('date', inplace=True)

# Verificar el DataFrame corregido
print(et_df.tail())

# Ajustar el modelo SARIMA (configura los parámetros según sea necesario)
model = sm.tsa.statespace.SARIMAX(et_df['et_value'], order=(1, 1, 1), seasonal_order=(1, 1, 1, 52))
model_fit = model.fit(disp=False)

# Hacer el pronóstico desde la última fecha de datos hasta las 52 semanas de 2024
forecast = model_fit.get_forecast(steps=52 + len(pd.date_range(cutoff_date, '2023-12-31', freq='W')))
forecast_df = forecast.summary_frame()

# Crear una serie de fechas para el pronóstico que continúe desde la última fecha de datos reales
forecast_index = pd.date_range(start=cutoff_date + pd.DateOffset(weeks=1), periods=forecast_df.shape[0], freq='W')

# Ajustar el índice del DataFrame de pronóstico
forecast_df.index = forecast_index

# Guardar el pronóstico
forecast_df.to_csv('evapotranspiration_forecast_2023-2024.csv')
print("Pronóstico guardado como 'evapotranspiration_forecast_2023-2024.csv'")

# Visualizar el pronóstico comparando con los datos reales
plt.figure(figsize=(10, 5))
plt.plot(et_df['et_value'], label='Histórico', color='blue')
plt.plot(forecast_df.index, forecast_df['mean'], label='Forecast', color='red')
plt.fill_between(forecast_df.index, forecast_df['mean_ci_lower'], forecast_df['mean_ci_upper'], color='pink', alpha=0.3)
plt.axvline(cutoff_date, color='black', linestyle='--', label='Inicio del pronóstico')
plt.xlabel('Fecha')
plt.ylabel('Evapotranspiración')
plt.title('Pronóstico de Evapotranspiración desde Octubre 2023 hasta 2024')
plt.legend()
plt.show()
