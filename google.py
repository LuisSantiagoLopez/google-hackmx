from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
import requests
import os

app = Flask(_name_)
client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))

# 1. Endpoint para iniciar la llamada, grabar y avisar al usuario
@app.route('/incoming-call', methods=['POST'])
def incoming_call():
    response = VoiceResponse()
    response.say("Esta llamada está siendo grabada por motivos de seguridad.")
    response.record(transcribe=True, transcribe_callback="/transcription")
    
    # Enviar una alerta cuando el adulto mayor contesta la llamada
    send_alert_contact("El adulto mayor ha contestado una llamada posiblemente fraudulenta.")
    return str(response)

# 2. Endpoint para manejar la transcripción de la llamada
@app.route('/transcription', methods=['POST'])
def handle_transcription():
    transcription_text = request.form.get('TranscriptionText')
    if transcription_text:
        # Llama a la API de OpenAI para analizar la transcripción
        analysis = analyze_text_with_gpt(transcription_text)
        if "fraude" in analysis or "sospechoso" in analysis:
            # Si se detecta lenguaje sospechoso, enviar alerta
            send_alert_contact(f"Posible intento de fraude detectado en la conversación: {transcription_text}")
    return '', 200

# Función para analizar el texto con OpenAI
def analyze_text_with_gpt(text):
    response = requests.post(
        'https://api.openai.com/v1/completions',
        headers={'Authorization': f"Bearer {os.getenv('OPENAI_API_KEY')}"},
        json={
            'model': 'gpt-4',
            'prompt': f"Detecta si este texto contiene lenguaje fraudulento: {text}",
            'max_tokens': 60
        }
    )
    return response.json()['choices'][0]['text'].strip()

# Función para enviar alerta al contacto de confianza
def send_alert_contact(message):
    client.messages.create(
        body=message,
        from_="+<TU_NUMERO_TWILIO>",
        to="+<NUMERO_CONTACTO_CONFIANZA>"
    )

if _name_ == '_main_':
    app.run(port=5000)