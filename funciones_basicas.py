import telebot
import json
import time
import os
from gtts import gTTS 
import whisper
import torch
import numpy as np


def logger(text):
    print(f'{time.strftime("%H:%M:%S")} - {text}')
    
def logging_bot(creds):
    creds = json.load(open(creds, 'r'))
    try:
        bot = telebot.TeleBot(creds.get('TOKEN'))
        logger(f'Se han cargado las credenciales para el canal {creds.get("CHANNEL")}.')
    except Exception as e:
        logger(f'Error al iniciar el bot: {e}')
        exit()
        
    return bot

# Clase User para guardar la información de los usuarios
class User:
    def __init__(self, modo_respuesta='texto', travesura=0):
        if not os.path.exists('logs'):
            os.mkdir('logs')
        self.user_id = None
        self.name = None
        self.username = None
        self.first_name = None
        self.last_name = None
        self.language_code = None
        self.chat_id = None
        self.modo_bot = 'user'
        self.modo_respuesta = modo_respuesta
        self.travesura = travesura
        self.path = None
        
    def update_user_info(self, message):
        self.user_id = message.from_user.id
        self.first_name = message.from_user.first_name
        self.last_name = message.from_user.last_name
        self.username = message.from_user.username
        self.language_code = message.from_user.language_code
        self.chat_id = message.chat.id
        if self.path is None:
            self.path = os.path.join('logs', f"log_{self.user_id}.json")


    def save_to_log(self):
            user_info = {
                'user_id': self.user_id,
                'name': self.name,
                'username': self.username,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'language_code': self.language_code,
                'chat_id': self.chat_id,
                'path': self.path
            }

            with open(self.path, 'w') as log_file:
                json.dump(user_info, log_file)

# Función que abre el fichero de log del usuario y guarda el mensaje y la fecha en JSON   
def log_user_message(message, user, response=None):
    try:
        log_filename = user.path
        user_message = {
            'date': message.date,  # Serialize datetime to string
            'modo_bot': user.modo_bot,  # Assuming modo_bot is an attribute of User
            'text': message.text,
            'response': response
        }
        with open(log_filename, 'a') as log_file:
            log_file.write('\n' + json.dumps(user_message))
    except Exception as e:
        print(f"Error writing to log file: {e}")
        
def leer(texto):
    lectura = gTTS(text=texto, lang='es', slow=False) 
    return lectura

def escuchar_whisper(input_audio, model_size='tiny'):
    torch.cuda.is_available()
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    MODEL = model_size

    model = whisper.load_model(MODEL, device=DEVICE)

    print(
        f"Loading Whisper model '{MODEL}' with device '{DEVICE}'. "
        f"Model is {'multilingual' if model.is_multilingual else 'English-only'} "
        f"and has {sum(np.prod(p.shape) for p in model.parameters()):,} parameters."
    )
        
    # load audio file
    audio = whisper.load_audio(input_audio)

    text = model.transcribe(audio)['text']
    
    os.remove(input_audio)
    
    return text