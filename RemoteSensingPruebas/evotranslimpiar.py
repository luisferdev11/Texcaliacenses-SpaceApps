import pandas as pd

# Cargar los datos CSV
et_df = pd.read_csv('evapotranspiration_weekly.csv')

# Interpolación lineal para rellenar los valores faltantes
et_df['et_value'] = et_df['et_value'].interpolate(method='linear')

# Verificar si quedan valores vacíos
print(et_df.isnull().sum())

# Guardar el dataset corregido
et_df.to_csv('evapotranspiration_weekly_clean.csv', index=False)