import telebot
import funciones_basicas as fn
import os
import time
import json

        
def callback_query(call, bot, user): 
    # Extraer el número de la opción seleccionada
    option_number = int(call.data.split('_')[1])

    if option_number == 1:
        user.modo_bot = "user"
        bot.send_message(call.message.chat.id, 
                         "Has elegido el modo usuario, recuerda que puedes cambiar los ajustes en cualquier momento con el comando /ajustes o conocer las tripas del bot con el comando /dev, despues vuelve al modo usuario con /user")
        
    elif option_number == 2:
        user.modo_bot = "dev"
        # Si la opción es "Modo desarrollador", enviar el comando /dev
        dev(call.message, bot, user)
    
        
    elif option_number == 3:
        user.modo_bot = "settings"
        ajustes(call.message.chat.id, bot, user)

    fn.logger(f'El usuario {user.first_name} ha elegido la opción {user.modo_bot}')
    
def primer_mensaje(message, bot, saludos_iniciales, clase_usuario):
        # Si es el primer mensaje, se guarda la información del usuario en el objeto user
        clase_usuario.update_user_info(message)
        fn.logger(f'El usuario {clase_usuario.first_name} ha iniciado el bot')
        
        # Primer mensaje después de la bienvenida [antes se chequea si ha saludado]
        if message.text.lower() in saludos_iniciales:
            mensaje_inicial = f'Kaixo {clase_usuario.first_name}🤝\nSoy el Bot🤖 del Equipo Morado. Por favor, elige una opción:'
        else:
            mensaje_inicial = f'Hey {clase_usuario.first_name} no vayas tan rapido, yo soy el Bot del Equipo Morado. Antes que nada, por favor, elige una opción:'

        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        botones = ["Modo usuario (/user)", "Modo admin (/dev)", "Ajustes del bot (/ajustes)"]

        for i, texto_boton in enumerate(botones, start=1):
            markup.add(telebot.types.InlineKeyboardButton(texto_boton, callback_data=f'modo_{i}'))
        
        # Envía el mensaje de bienvenida con opciones de botones
        bot.send_message(message.chat.id, mensaje_inicial, reply_markup=markup)
        
        clase_usuario.save_to_log()
        fn.log_user_message(message, clase_usuario)
        
def handle_message(message, bot, openai_client, clase_usuario):
    
    if clase_usuario.modo_bot == 'user':

        # Utiliza la API de OpenAI para generar respuestas
        respuesta_api = openai_client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": 
                            f"""Esta parte del mensaje son tus instrucciones como bot:
                                - Eres el bot que ha creado el Equipo Morado para su canal de Telegram.
                                - Tu objetivo es responder a las preguntas de los usuarios.
                                - Teniendo en cuenta que un 0 es la respuesta más seria y un 3 la más graciosa, chistosa y vacilona, tu nivel de travesura es: {clase_usuario.travesura}
                                - Lo que viene a continuación es el mensaje del usuario: 
                            """ + message.text,
                    }
                ],
                model="gpt-3.5-turbo")
            
        # Envía la respuesta de la API como mensaje
        mensaje_respuesta = respuesta_api.choices[0].message.content
        fn.logger('La respuesta de la API es: ' + mensaje_respuesta)
            
        if clase_usuario.modo_respuesta == 'texto':
                bot.send_message(message.chat.id, mensaje_respuesta)
        elif clase_usuario.modo_respuesta == 'audio':
                if not os.path.exists('temp'):
                    os.mkdir('temp')
                audio_file = os.path.join('temp', 'respuesta.mp3')
                lectura = fn.leer(mensaje_respuesta)
                lectura.save(audio_file)
                time.sleep(1.5)
                bot.send_voice(message.chat.id, open(audio_file, 'rb'))
                os.remove(audio_file)

        # Guarda el mensaje del usuario en el registro
        fn.log_user_message(message, clase_usuario, mensaje_respuesta)
        
 
 
def ajustes(message_id, bot, clase_usuario):
    mensaje_ajustes = """
        ⚙️Estos son los ajustes disponibles para el bot⚙️\nPuedes cambiarlos en cualquier momento (/ajustes). Cuando termines recuerda volver al modo usuario (/user)
        
    -Puedes elegir el formato de las respuestas con el comando /modo [audio | texto].
    -Puedes configurar el nivel de travesura 🤪🤪 del bot con el comando /travesura [0-3].
        """

    clase_usuario.modo_bot = 'settings'
    bot.send_message(message_id, mensaje_ajustes)
    
def modo_command(message, bot, clase_usuario):
    clase_usuario.modo_bot = 'settings'

    fn.logger(f'El usuario {clase_usuario.first_name} ha ejecutado el comando {message.text}')

    # Verificar si se proporciona un argumento después del comando
    if len(message.text.split()) == 2:
        modo_nuevo = message.text.split()[1].lower()
        if modo_nuevo in ['texto', 'audio']:
            clase_usuario.modo_respuesta = modo_nuevo
            bot.send_message(message.chat.id, f"Modo de respuesta cambiado a: {modo_nuevo}")
        else:
            bot.send_message(message.chat.id, "Por favor, proporciona un modo válido: 'texto' o 'audio'.")
    else:
        bot.send_message(message.chat.id, "Por favor, proporciona un modo después del comando. Ejemplo: /modo texto")
        
    fn.log_user_message(message, clase_usuario)
        
def travesura_command(message, bot, clase_usuario):
    clase_usuario.modo_bot = 'settings'
    fn.logger(f'El usuario {clase_usuario.first_name} ha ejecutado el comando {message.text}')

    # Verificar si se proporciona un argumento después del comando
    if len(message.text.split()) == 2:
        try:
            nivel_travesura = int(message.text.split()[1])
            if 0 <= nivel_travesura <= 3:
                clase_usuario.travesura = nivel_travesura
                bot.send_message(message.chat.id, f"Nivel de travesura cambiado a: {nivel_travesura}")
            else:
                bot.send_message(message.chat.id, "Por favor, proporciona un nivel de travesura válido entre 0 y 3.")
        except ValueError:
            bot.send_message(message.chat.id, "Por favor, proporciona un nivel de travesura válido como número entero.")
    else:
        bot.send_message(message.chat.id, "Por favor, proporciona un nivel de travesura después del comando. Ejemplo: /travesura 3")
        
    fn.log_user_message(message, clase_usuario)
        
def back_to_user_mode(message, bot, clase_usuario):
    clase_usuario.modo_bot = 'user'
    bot.send_message(message.chat.id, "Modo usuario activado.")
    
    fn.log_user_message(message, clase_usuario)
        
    
def dev(message, bot, clase_usuario):
    clase_usuario.modo_bot = 'dev'
    
    texto_dev = """
    🤖
    Este bot ha sido creado por el Equipo Morado para su canal de Telegram.
    
    Aquí puedes ver las tripas del bot, el cual tiene capacidad para:
    
        1️⃣ Gestionar bienvenidas
        2️⃣ Logear usuarios e historial de mensajes
        3️⃣ Posibilidad de cambiar el modo de respuesta del bot (texto o audio)
        4️⃣ Posibilidad de cambiar el nivel de travesura del bot (0 a 3)
        5️⃣ Posibilidad de interactuar tanto con texto como con voz automáticamente (el bot reconoce si el mensaje es de voz o de texto)
        6️⃣ Posibilidad de enviar tu historial de mensajes
        
    Todo esto es posible gracias a:
        - La API de OpenAI haciendo uso de su modelo GPT-3 Turbo para generar respuestas
        - Whisper (versión tiny para que sea rapido) corriendo en local para convertir voz del usuario en texto
        - El modelo GTTS(Google Text to Speech) corriendo en local para convertir texto en voz
        
        
    Para volver al modo usuario, utiliza el comando /user
    
    Utiliza el comando /historial para obtener tu historial de mensajes.
    🤖
    """
    
    # Posibilidad de ver tu historial de mensajes
    
    bot.send_message(message.chat.id, texto_dev)
    
    fn.log_user_message(message, clase_usuario)
    
def voice_handler(message, bot, openai_client, clase_usuario):
    
    if clase_usuario.modo_bot == 'user':
        
        file_id = message.voice.file_id  # file size check. If the file is too big, FFmpeg may not be able to handle it.
        file = bot.get_file(file_id)

        file_size = file.file_size
        if int(file_size) >= 715000:
            bot.send_message(message.chat.id, 'Fichero demasiado extenso.')
        else:
            download_file = bot.download_file(file.file_path)  # download file for processing
            with open(os.path.join('temp', 'user_voice.ogg'), 'wb') as new_file:
                new_file.write(download_file)
                
        texto = fn.escuchar_whisper(os.path.join('temp', 'user_voice.ogg'))
    

        # Utiliza la API de OpenAI para generar respuestas
        respuesta_api = openai_client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": 
                            f"""Esta parte del mensaje son tus instrucciones como bot:
                                - Eres el bot que ha creado el Equipo Morado para su canal de Telegram.
                                - Tu objetivo es responder a las preguntas de los usuarios.
                                - Teniendo en cuenta que un 0 es la respuesta más seria y un 3 la más graciosa, chistosa y vacilona, tu nivel de travesura es: {clase_usuario.travesura}
                                - Lo que viene a continuación es el mensaje del usuario: 
                            """ + texto,
                    }
                ],
                model="gpt-3.5-turbo")
            
        # Envía la respuesta de la API como mensaje
        mensaje_respuesta = respuesta_api.choices[0].message.content
        fn.logger('La respuesta de la API es: ' + mensaje_respuesta)
            
        if clase_usuario.modo_respuesta == 'texto':
                bot.send_message(message.chat.id, mensaje_respuesta)
        elif clase_usuario.modo_respuesta == 'audio':
                if not os.path.exists('temp'):
                    os.mkdir('temp')
                audio_file = os.path.join('temp', 'respuesta.mp3')
                lectura = fn.leer(mensaje_respuesta)
                lectura.save(audio_file)
                time.sleep(1.5)
                bot.send_voice(message.chat.id, open(audio_file, 'rb'))
                os.remove(audio_file)

        # Guarda el mensaje del usuario en el registro
        fn.log_user_message(message, clase_usuario, mensaje_respuesta)
        
def historial(message, bot, clase_usuario):
    clase_usuario.modo_bot = 'dev'
    
    if os.path.exists(clase_usuario.path):
        fn.logger(f'El usuario {clase_usuario.first_name} ha solicitado su historial de mensajes')
        bot.send_document(message.chat.id, open(clase_usuario.path, 'rb'))
    else:
        bot.send_message(message.chat.id, 'No tienes historial de mensajes.')
        
    bot.send_message(message.chat.id, 'Para volver al modo usuario, utiliza el comando /user')
        
    fn.log_user_message(message, clase_usuario)