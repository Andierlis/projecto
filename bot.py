#Python
import time
import os
import asyncio
import math


#Locales
from cfg import *
from utils import get_filename_media,build_menu,download_of_youtube,proces_upload,upload_file,create_txt
from progress import progressddl,progresswget,progressytdl,progresstwitch,progressupload
from downloader.youtubedl import YoutubeDL
from downloader.wget import download as downloadwget
from downloader.mediafire import get
from zip import split,compressionone,getBytes
from JsonDB import JsonDatabase

#Apps de Terceros
from pyrogram import Client,filters
import tgcrypto
from pyrogram.types import InlineKeyboardButton,InlineKeyboardMarkup,CallbackQuery
from convopyro import Conversation
import nest_asyncio

"""=====================Variables Globales====================="""
nest_asyncio.apply()
yturls = []



bot = Client('Mail',api_id=API_ID,api_hash=API_HASH,bot_token=BOT_TOKEN)
Conversation(bot)


    


"""============Metodo Start============="""
@bot.on_message(filters.private)
def Bienvenido(client,message):
    mensaje = message.text
    admin = 'Wachu985'
    username = message.chat.username
    jdb = JsonDatabase('database')
    jdb.check_create()
    jdb.load()
    user_info = jdb.get_user(username)
    if username == admin or user_info:
        if user_info is None:
            if username == admin:
                jdb.create_admin(username)
            else:
                jdb.create_user(username)
            user_info = jdb.get_user(username)
            jdb.save()         
    else:
        enlace_directo = [
                    [InlineKeyboardButton(
                        'Obtener Acceso',
                        url=f'https://t.me/Wachu985'
                    )
                    ]      
                ]
        reply_botton = InlineKeyboardMarkup(enlace_directo)
        bot.send_message(message.chat.id,'**👹No Tiene permiso para usar el Bot**',reply_markup=reply_botton)
        return
    
    if mensaje == '/start':
        enlace_directo = [
                    [InlineKeyboardButton(
                        '⚙️Soporte',
                        url=f'https://t.me/Wachu985'
                    ),
                    InlineKeyboardButton(
                        '💻GITHUB',
                        url=f'https://github.com/Wachu985/'
                    ),
                    ]      
                ]
        reply_botton = InlineKeyboardMarkup(enlace_directo)
        bot.send_message(message.chat.id,'✉️**Bienvenido al Bot '+message.chat.first_name+'**'+'\n\n__📱Bot de Subida a Correo Fase De Prueba📱__',reply_markup=reply_botton)
        
    elif mensaje == '/info':
        text = '**⚙️Configuracion del Bot**\n\n'
        text += f'**🔌Host:** {user_info["host"]}\n'
        text += f'**🛂Username:** {user_info["username"]}\n'
        text += f'**🔣Password:** {user_info["password"]}\n'
        text += f'**🗜Zips:** {user_info["zips"]}\n'

        options = [
            [
                InlineKeyboardButton('Cambiar Usuario',callback_data='username'),
                InlineKeyboardButton('Cambiar Contraseña',callback_data='password')
            ],
            [
                InlineKeyboardButton('Cambiar Host',callback_data='host'),
                InlineKeyboardButton('Cambiar Zips',callback_data='zips'),
            ],
            [
                InlineKeyboardButton('CANCEL',callback_data='stop')        
            ]
        ]
        reply_botton = InlineKeyboardMarkup(options)
        bot.send_message(message.chat.id,text,reply_markup=reply_botton)
        return
    
    elif '/add' in mensaje:
        user = mensaje.split(' ')[-1]
        jdb.create_user(user)
        bot.send_message(message.chat.id,f'**✳️Usuario @{user} Agregado Correctamente**')
        jdb.save()
    
    elif '/set' in mensaje:
        try:
            user = mensaje.split(' ')[-1].split(',')
            user_info['host'] = user[0]
            user_info['username'] = user[1]
            user_info['password'] = user[2]
            bot.send_message(message.chat.id,f'**✳️Configuracion Registrada Correctamente**')
            jdb.save()
        except:
            bot.send_message(message.chat.id,f'**📛Error al Registrar Configuracion**')
    elif '/ban' in mensaje:
        user = mensaje.split(' ')[-1]
        jdb.create_user(user)
        bot.send_message(message.chat.id,f'**📛Usuario @{user} Eliminado Correctamente**')
        jdb.save()

    elif message.media:
        media_telegram(client,message,user_info)

    elif 'http' in mensaje or 'youtu' in mensaje or 'youtube' in mensaje:
        download(client,message,user_info)
    

"""============Descarga de Archivos de Telegram==========="""
def media_telegram(client,message,user_info):
    try:
        filename = get_filename_media(message)
        msg = bot.send_message(
            message.chat.id,
            "📡**Descargando Archivos... Por Favor Espere**",
            reply_to_message_id=message.id
        )
        start = time.time() 
        #Descarga de Media
        filename=bot.download_media(
            message,
            progress=progressddl,
            progress_args=(msg,bot,filename,start)
        )
        msg.delete()
        msg = bot.send_message(msg.chat.id,'✅Descargado Correctamente',reply_to_message_id=message.id)
        if os.path.getsize(filename)/1048576 > int(user_info['zips']):
            msg.delete()
            file =  ''.join(filename.split('\\')[-1].split('.')[:-1])+ '.zip'
            tama = int(os.path.getsize(filename)/1048576)
            tpart = int(user_info['zips'])
            part = math.ceil(tama/tpart)  
            text = f'📚**Comprimiendo Archivos**\n📝**Nombre**: {file}\n'
            text += f'🗂**Tamaño Total**: {tama} MiB\n📂**Tamaño de Partes**: {tpart}MiB\n'
            text += f'💾**Cantidad de Partes**: {part}'
            msg = bot.send_message(
                msg.chat.id,
                text
            )
            comprimio,partes = split(compressionone(file,filename),f'./downloads/',getBytes(f'{user_info["zips"]}MiB'))
            msg.delete()
            msg = bot.send_message(msg.chat.id,'**📶Uploading....**')
            list_files=[]
            mail = MailClient(user_info['username'],user_info['password'],user_info['host'])
            if comprimio:
                cont = 1
                if mail.login():
                    while cont < partes:
                        filename = file+'.'+str('%03d' % (cont))
                        fileup=upload_file(user_info,f'./downloads/{filename}',progressupload,msg,bot,mail)
                        if fileup:
                            list_files.append(fileup)
                            cont += 1
                        else:
                            msg = bot.send_message(msg.chat.id,'Error de Subida')
                            return
                        list_files.append(fileup)
                        cont += 1
                else:
                    msg = bot.send_message(msg.chat.id,'Error al Iniciar Sesion')
                    return
            text = '**Files:**\n\n'
            for f in list_files:
                text+=f+'\n\n'
            msg.delete()
            name = create_txt(file,list_files)
            msg = bot.send_message(msg.chat.id,text)
            bot.send_document(msg.chat.id,f'./{name}')
        else:
            msg.delete()
            msg = bot.send_message(msg.chat.id,'**📶Uploading....**')
            mail = MailClient(user_info['username'],user_info['password'],user_info['host'])
            file = filename.split('\\')[-1]
            if mail.login():
                fileup=upload_file(user_info,filename,progressupload,msg,bot,mail)
                if not fileup:
                    msg = bot.send_message(msg.chat.id,'Error de Subida')
                    return
            else:
                msg = bot.send_message(msg.chat.id,'Error al Iniciar Sesion')
                return 
            text = f'**Files:**\n\n {fileup}'
            msg.delete()
            lista = [fileup]
            name = create_txt(file,lista)
            msg = bot.send_message(msg.chat.id,text)
            bot.send_document(msg.chat.id,f'./{name}')
    except Exception as e:
        msg.delete()
        bot.send_message(msg.chat.id,f'❌Error de Descarga❌ {e}')
    

def download(client,message,user_info):
    #=====================Comando de Videos de Youtube y De Twitch=====================#
    if "youtu" in message.text or 'twitch' in message.text:
        global yturls
        yturls = []
        ytdl = YoutubeDL()
        try:
            yt = ytdl.info(message.text)
            for f in yt:
                yturls.append(f.split(sep=':'))
            button_list = []
            for each in yturls:
                button_list.append(InlineKeyboardButton(each[1], callback_data = each[0]))
            keyboard_group=InlineKeyboardMarkup(build_menu(button_list, n_cols=3))
            text = '**Seleccione la Resolucion:👇**'
            msg= bot.send_message(chat_id=message.chat.id,text=text,reply_markup=keyboard_group,reply_to_message_id=message.id) 
        except Exception as e:
            bot.send_message(message.chat.id,f'❌**Error al Analizar el Video❌-> {e}**')

    #================Descargas de Mediafire===================
    elif "mediafire" in message.text:
        try:
            save = './'+message.chat.username+'/'
            if not os.path.exists(save):
                os.mkdir(save)
            msg = bot.send_message(message.chat.id, '⏬**Descargando Archivo. Por Favor Espere....**')
            name = downloadwget(get(message.text),msg,bot,out=f'./{message.chat.username}/',bar=progresswget)
            filename = name.split("/")[-1]
            msg = bot.edit_message_text(message.chat.id,msg.id, '✅**Archivo Descargado Correctamente**')
            proces_upload(user_info,name,msg,bot)
        except Exception as e: bot.edit_message_text(message.chat.id, msg.id, f"❌ **El Enlace no se pudo descargar -> {e}**❌")
        return

    elif 'http' in message.text:
        try:
            save = './'+message.chat.username+'/'
            if not os.path.exists(save):
                os.mkdir(save)
            msg = bot.send_message(message.chat.id,'⏬**Descargando Archivo. Por Favor Espere....**')
            filename = downloadwget(message.text,msg,bot,out=f'./{message.chat.username}/',bar=progresswget)
            file = filename.split("/")[-1]
            msg = bot.edit_message_text(message.chat.id,msg.id,f'✅**Archivo Descargado Correctamente**')
            proces_upload(user_info,filename,msg,bot)
        except Exception as e: bot.edit_message_text(message.chat.id, msg.id, f"❌ **El Enlace no se pudo descargar -> {e} **❌")
        return


@bot.on_callback_query()
def callback_querry(client,CallbackQuery):
    msg = CallbackQuery.message
    msg.delete()
    username = CallbackQuery.message.chat.username
    jdb = JsonDatabase('database')
    jdb.check_create()
    jdb.load()
    user_info = jdb.get_user(username)
    if 'username' in CallbackQuery.data:
        msg = bot.send_message(msg.chat.id,'🖌**Inserte el Nuevo Usuario**:👇 __Tiene 8 seg...__')
        try:
            name = asyncio.run(client.listen.Message(filters.chat(msg.chat.id), timeout = 8))
        except asyncio.TimeoutError:
            msg.edit_text('🚫**Tiempo de Espera Exedido**🚫')
            return
        if user_info:
            user_info['username'] = name.text
            jdb.save()
        msg.delete()
        msg = bot.send_message(msg.chat.id,'**✅Configuracion Registrada**')
    elif 'password' in CallbackQuery.data:
        msg = bot.send_message(msg.chat.id,'🖌**Inserte la Nueva Contraseña**:👇 __Tiene 8 seg...__')
        try:
            name = asyncio.run(client.listen.Message(filters.chat(msg.chat.id), timeout = 8))
        except asyncio.TimeoutError:
            msg.edit_text('🚫**Tiempo de Espera Exedido**🚫')
            return
        if user_info:
            user_info['password'] = name.text
            jdb.save()
        msg.delete()
        msg = bot.send_message(msg.chat.id,'**✅Configuracion Registrada**')
    elif 'host' in CallbackQuery.data:
        msg = bot.send_message(msg.chat.id,'🖌**Inserte el Nuevo Host**:👇 __Tiene 8 seg...__')
        try:
            name = asyncio.run(client.listen.Message(filters.chat(msg.chat.id), timeout = 8))
        except asyncio.TimeoutError:
            msg.edit_text('🚫**Tiempo de Espera Exedido**🚫')
            return
        if user_info:
            user_info['host'] = name.text
            jdb.save()
        msg.delete()
        msg = bot.send_message(msg.chat.id,'**✅Configuracion Registrada**')
    elif 'zips' in CallbackQuery.data:
        msg = bot.send_message(msg.chat.id,'🖌**Inserte el Nuevo Tamaño de Zips**:👇 __Tiene 8 seg...__')
        try:
            name = asyncio.run(client.listen.Message(filters.chat(msg.chat.id), timeout = 8))
        except asyncio.TimeoutError:
            msg.edit_text('🚫**Tiempo de Espera Exedido**🚫')
            return
        if user_info:
            user_info['zips'] = name.text
            jdb.save()
        msg.delete()
        msg = bot.send_message(msg.chat.id,'**✅Configuracion Registrada**')
    elif 'stop' in CallbackQuery.data:
        return

    global yturls
    for each in yturls:
        if CallbackQuery.data == each[0]:
            upload = download_of_youtube(CallbackQuery,each,bot,user_info)
            if upload:
                yturls = []
                break

if __name__=="__main__":
    print('========Init Bot===========')
    bot.run()
