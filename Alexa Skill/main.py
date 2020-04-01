from __future__ import print_function
import boto3

client = boto3.resource('dynamodb')
table = client.Table('precios_luz')

def build_speechlet_response(output, should_end_session):
    return {
        'outputSpeech': { 'type': 'PlainText', 'text': output },
        'shouldEndSession': should_end_session
    }
    
def build_response(speechlet_response):
    return { 'version': '1.0', 'response': speechlet_response }

# Defino un mensaje de bienvenida y anticipo lo que hace la skill.
def WelcomeHandler():
    speech_output = "¡Bienvenido a la skill que te ayuda a ahorrar en la factura de la luz!"
    shouldEndSession = False
    
    return build_response(build_speechlet_response(speech_output, shouldEndSession))
    
def MinHandler(intent):
    last_fare = intent['slots']['fare']['value']
    
    getItem = table.get_item(Key = { 'fare': last_fare })
    price = float(getItem['Item']['price'])
    
    minimum = min((price, 2)
    
    speech_output = "El precio más económico para cargar tu coche hoy en " + last_fare + " es " + str(minimum)
    shouldEndSession = True
    
    return build_response(build_speechlet_response(speech_output, shouldEndSession))
    
# Defino una función de ayuda para guiar al usuario en las peticiones que puede ejecutar.
def HelpHandler():
    speech_output = "Puedes pedirme cosas como: el precio más barato para hoy para cargar mi coche eléctrico, ó precio mas bajo para hoy en tarifa normal. Dime, ¿En qué puedo ayudarle?"
    should_end_session = False
    
    return build_response(build_speechlet_response(speech_output, should_end_session))
    
def handle_session_end_request():
    speech_output = "¡Nos vemos pronto, gracias por ahorrar un poco más en tu tarifa de la luz!" 
    should_end_session = True
    
    return build_response(build_speechlet_response(speech_output, should_end_session))

def on_session_started(session_started_request, session):
    pass

def on_launch(launch_request, session):
    return WelcomeHandler()
    
def find_intent(intent_name):
    for i in range(len(intents)):
        if intent_name == intents[i][0]:
            return i
    return -1

def on_intent(intent_request, session):
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    
    index = find_intent(intent_name)
    if index != -1:
        current_intent = intents[index][1]
        return current_intent(intent)
    else:
        if intent_name == "AMAZON.HelpIntent":
            return HelpHandler()
        elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
            return handle_session_end_request()
        else:
            raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    print("on_session_ended requestId=" + session_ended_request['requestId'] + ", sessionId=" + session['sessionId'])

def lambda_handler(event, context):
    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},event['session'])
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])

intents = [
    ["minimum", minimumHandler]
]

#Las tarifas que he puesto en la base de datos.
fares = [
    "coche_electrico",
    "normal",
    "discriminación"
]
