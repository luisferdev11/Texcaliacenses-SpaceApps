from llama_index.core.llms import ChatMessage
from llama_index.llms.openai import OpenAI
import os
import openai

openai.api_key = os.environ["OPENAI_API_KEY"]

#abrimos base de conocimientos y preguntas ya establecidas
with open('./data/knowledgeCorn.txt','r',encoding='utf-8') as fileKnowledge:
    knowledge = fileKnowledge.read()

with open('./data/questionsStatics.txt', 'r', encoding='utf-8') as fileQuestions:
    questions = fileQuestions.read().splitlines()


def json_to_text(weather_data, soil_moisture_data, ndvi_data, average_evapotranspiration):
    current_temp = weather_data["current_temperature_centigrades"]
    current_precip = weather_data["current_precipitation_mm"]
    avg_temp_5days = weather_data["average_temperature_last_5days_centigrades"]
    total_precip_5days = weather_data["total_precipitation_last_5days_mm"]

    mean_soil_moisture = soil_moisture_data["mean_soil_moisture"] * 100 
    mean_ndvi = ndvi_data["mean_ndvi"] * 0.0001 

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

# aqui el json donde se recibira la data de un edponint para generar texto plano
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

data = json_to_text(json_data["weather_data"], json_data["soil_moisture_data"], json_data["ndvi_data"], json_data["average_evapotranspiration"])

# juntar la base de conocimientos con la data para el contenido de OpenAI
content = knowledge + "\n" + data   


#funcion que me genera un arreglo de todas las respuestas a las preguntas 
def ask_questions():
    i = 0  
    responses = []
    while i < len(questions):
        question = questions[i]
        # print(question)
        messages = [
            ChatMessage(role="system", content=content),
            ChatMessage(role="user", content=question),
        ]
        
        try:
            response = OpenAI(model="gpt-4o-mini").chat(messages)
            print(response) 
            responses.append(response)  
            
        except Exception as e:
            print(f"Error al procesar la pregunta: {e}")
        i += 1
    
    return responses  

data_responses = []
data_responses = ask_questions()
print (data_responses)  


# print("\nRespuestas obtenidas:")
# for idx, resp in enumerate(data_responses):  # Usa la variable correcta aquí
#     print(f"Pregunta {idx+1}: {questions[idx]}")
#     print(f"Respuesta {idx+1}: {resp}\n")
