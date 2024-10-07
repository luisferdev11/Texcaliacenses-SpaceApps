import os
import openai
from llama_index.core.llms import ChatMessage
from llama_index.llms.openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Cargar la clave de API de OpenAI desde las variables de entorno
openai.api_key = os.getenv("OPENAI_API_KEY")
print(os.getenv("OPENWEATHER_API_KEY"))

# Ruta a los archivos de datos
KNOWLEDGE_FILE = './data/knowledgeCorn.txt'
QUESTIONS_FILE = './data/questionsStatics.txt'

# Cargar la base de conocimientos y las preguntas
with open(KNOWLEDGE_FILE, 'r', encoding='utf-8') as fileKnowledge:
    knowledge = fileKnowledge.read()

with open(QUESTIONS_FILE, 'r', encoding='utf-8') as fileQuestions:
    questions = fileQuestions.read().splitlines()

# Función para convertir los datos JSON a texto plano
def json_to_text(weather_data, soil_moisture_data, ndvi_data, average_evapotranspiration):
    current_temp = weather_data["current_temperature_centigrades"]
    current_precip = weather_data["current_precipitation_mm"]
    avg_temp_5days = weather_data["average_temperature_last_5days_centigrades"]
    total_precip_5days = weather_data["total_precipitation_last_5days_mm"]

    mean_soil_moisture = soil_moisture_data["mean_soil_moisture"] * 100
    mean_ndvi = ndvi_data["mean_ndvi"] * 0.0001  # Ajuste según tu escala

    evapotranspiration = average_evapotranspiration

    text = f"""The current temperature is {current_temp:.2f}°C.
The current precipitation is {current_precip:.2f} mm.
The average temperature over the last 5 days is {avg_temp_5days:.2f}°C.
The total precipitation over the last 5 days is {total_precip_5days:.2f} mm.

Soil moisture conditions: the mean soil moisture is {mean_soil_moisture:.2f}%, which is {'slightly below' if mean_soil_moisture < 30 else 'within'} the optimal range.

The average evapotranspiration is {evapotranspiration:.2f}.

NDVI data shows a mean value of {mean_ndvi:.4f}, indicating {'healthy vegetation' if mean_ndvi > 0 else 'stress in the vegetation'}.
"""
    return text

# Función para generar las respuestas a las preguntas
def generate_recommendations(report_data):
    # Convertir los datos JSON a texto
    data_text = json_to_text(
        report_data['weather_data'],
        report_data['soil_moisture_data'],
        report_data['ndvi_data'],
        report_data['average_evapotranspiration']
    )

    # Combinar la base de conocimientos con los datos
    content = knowledge + "\n" + data_text

    recommendations = []
    for question in questions:
        messages = [
            ChatMessage(role="system", content=content),
            ChatMessage(role="user", content=question),
        ]

        try:
            response = OpenAI(model="gpt-4").chat(messages)
            recommendations.append(response)
        except Exception as e:
            print(f"Error al procesar la pregunta: {e}")
            recommendations.append("No response due to error.")

    return recommendations

if __name__ == "__main__":
    # Ejemplo de datos de prueba
    json_data = {
        "weather_data": {
            "current_temperature_centigrades": 13.11,
            "current_precipitation_mm": 0.16,
            "average_temperature_last_5days_centigrades": 13.33,
            "total_precipitation_last_5days_mm": 29.2
        },
        "soil_moisture_data": {
            "mean_soil_moisture": 0.27667937241557594
        },
        "ndvi_data": {
            "mean_ndvi": 3639,
            "retried": 2
        },
        "average_evapotranspiration": 218.90702287880208
    }

    # Generar recomendaciones
    recommendations = generate_recommendations(json_data)
    for i, recommendation in enumerate(recommendations):
        print(f"Pregunta {i+1}: {recommendation}")