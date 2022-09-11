from downloader.youtubedl import YoutubeDL
from progress import progresstwitch,progressytdl,progressupload
from zip import split,compressionone,getBytes
import math
from MailClient import MailClient
import os

def create_txt(name,files):
    name = f'{name}.txt'
    txt = open(name,'w')
    fi = 0
    for f in files:
        separator = '\n'
        txt.write(f+separator)
        fi += 1
    txt.close()
    return name

"""==========Nombre de Archivo de Telegram==========="""
def get_filename_media(message):
    if message.video:
        try:
            filename = message.video.file_name
        except:
            filename = message.video.file_id
    elif message.sticker:
        try:
            filename = message.sticker.file_name
        except:
            filename = message.sticker.file_id
    elif message.photo:
        try:
            filename = message.photo.file_name
        except:
            filename = message.photo.file_id
    elif message.audio:
        try:
            filename = message.audio.file_name
        except:
            filename = message.audio.file_id
    elif message.document:
        try:
            filename = message.document.file_name
        except:
            filename = message.document.file_id
    elif message.voice:
        try:
            filename = message.voice.file_name
        except:
            filename = message.voice.file_id
    return filename


"""================Constructor de Menu para los Videos de Youtube================"""
def build_menu(buttons,n_cols,header_buttons=None,footer_buttons=None):
    menu = []
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

def upload_file(user_info,file_path,callback,bot,message,mail):
        return mail.uploadFile(file_path,callback,bot,message)

def proces_upload(user_info,filename,msg,bot):
    try:
        save = './downloads'
        if not os.path.exists(save):
            os.mkdir(save)
        if os.path.getsize(filename)/1048576 > int(user_info['zips']):
            msg.delete()
            file =  ''.join(filename.split('/')[-1].split('.')[:-1])+ '.zip'
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
                        fileup=upload_file(user_info,f'./downloads/{filename}',progressupload,bot,msg,mail)
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
            msg = bot.send_message(msg.chat.id,'Uploading....')
            mail = MailClient(user_info['username'],user_info['password'],user_info['host'])
            file = filename.split('/')[-1]
            if mail.login():
                fileup=upload_file(user_info,filename,progressupload,bot,msg,mail)
            else:
                msg = bot.send_message(msg.chat.id,'Error al Iniciar Sesion')
                return
            text = f'**Files:**\n\n {fileup}'
            msg.delete()
            lista = [fileup]
            name = create_txt(file,lista)
            msg = bot.send_message(msg.chat.id,text)
            bot.send_document(msg.chat.id,f'./{name}')
    except Exception as ex:
        msg.delete()
        bot.send_message(msg.chat.id,f'❌Error al Subir❌ {ex}')


"""================Descarga de Videos de Youtube================"""
def download_of_youtube(CallbackQuery,each,bot,user_info):
    msg = CallbackQuery.message
    format = each[0]
    ext = each[-1]
    username = msg.chat.username
    url = CallbackQuery.message.reply_to_message.text.split(sep=' ')[-1]
    msg.delete()
    msg = bot.send_message(msg.chat.id,'⏬**Recopilando Información... Por favor Espere...**')
    try:
        twitch = False
        if 'twitch' in url:
            ytdl= YoutubeDL(progresstwitch,msg,bot,True)
        else:
            ytdl= YoutubeDL(progressytdl,msg,bot,twitch)
        file,duration = ytdl.download(url,username,format)
        msg.delete()
        msg = bot.send_message(msg.chat.id,'✅**Descargado Correctamente..**')
        proces_upload(user_info,file,msg,bot)
    except Exception as e:
        msg.delete()
        bot.send_message(msg.chat.id,f'❌**Error al Descargar de Youtube**❌ {e}')
        return False
