import json
from openai import OpenAI
import funciones_basicas as fn
import funciones_bot as fn_bot
#################################


# CARGAR FICHERO DE CREDENCIALES
TOKENFILE = '.botkeys.json'
with open(TOKENFILE, 'r') as f:
        creds = json.load(f)
#################################


# INICIALIZAR BOT Y CLIENTE DE OPENAI
bot = fn.logging_bot(TOKENFILE)
openai_client = OpenAI(api_key=creds.get('OPENAI_API_KEY'))
primer_mensaje = True
#####################################


# Inicialización del diccionario de usuarios y otros parámetros
with open('saludos.txt', 'r') as file:
    saludos_iniciales = [line.strip() for line in file]
    
clase_usuario = fn.User()
    
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    fn_bot.callback_query(call, bot, clase_usuario)

@bot.message_handler(commands=['ajustes'])
def ajustes(message):
    fn_bot.ajustes(message.chat.id, bot, clase_usuario)

@bot.message_handler(commands=['modo'])
def modo(message):
    fn_bot.modo_command(message, bot, clase_usuario)
            
@bot.message_handler(commands=['travesura'])
def travesura(message):
    fn_bot.travesura_command(message, bot, clase_usuario)
    
@bot.message_handler(commands=['user'])
def user(message):
    fn_bot.back_to_user_mode(message, bot, clase_usuario)
    
# @bot.message_handler(func=lambda message: True)
# def cambiar_modo(message):
#     fn_bot.cambiar_modo(message, bot, clase_usuario)
        
@bot.message_handler(commands=['dev'])
def dev(message):
    fn_bot.dev(message, bot, clase_usuario)
    
@bot.message_handler(commands=['historial'])
def historial(message):
    fn_bot.historial(message, bot, clase_usuario)
                
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    global primer_mensaje
    if primer_mensaje:
        fn_bot.primer_mensaje(message, bot, saludos_iniciales, clase_usuario)
        primer_mensaje = False
    else:
        fn_bot.handle_message(message, bot, openai_client, clase_usuario)
        
@bot.message_handler(content_types=['voice'])
def voice_handler(message):
    fn_bot.voice_handler(message, bot, openai_client, clase_usuario)
    

# Inicio del bot
bot.infinity_polling()


# IDEAS DE FEATURES:

# Cosas a explicar:
#  - Gestionar bienvenidas
#  - Logear usuarios e historial de mensajes
#  - Posibilidad de cambiar el modo de respuesta del bot (texto o audio)
#  - Posibilidad de cambiar el nivel de travesura del bot (0 a 3)
#  - Posibilidad de interactuar tanto con texto como con voz automáticamente
#  - Posibilidad de ver tu historial de mensajes
