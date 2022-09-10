import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import quote


import uuid
import os
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor


class MailClient():
    def __init__(self,username,password,host):
        self.username = username
        self.password = password
        self.host = host
        self.islogin = False
        self.__session = requests.session()

    def login(self):

        response = self.__session.get(self.host)

        content = response.text

        soup = BeautifulSoup(content,features='html.parser')
        login_csrf = soup.find('input',{'name':'login_csrf'})['value']
        loginOp	= "login"
        client = "preferred"
        payload = {
            'loginOp':loginOp,
            'login_csrf':login_csrf,
            'username':self.username,
            'password':self.password,
            'client':client

        }
        response = self.__session.post(self.host,data=payload)
        soup = BeautifulSoup(response.text,features='html.parser')
        title = soup.find('title').text
        print(response.url)
        if title == 'Zimbra Web Client Sign In':
            print('Error al Iniciar Sesion')
            return False
        else:
            print('He Iniciado Sesion')
            return True

    def uploadFile(self,filepath,upload_callback,bot,message):
        response=self.__session.get(f'{self.host}/h/search?st=briefcase')
        soup = BeautifulSoup(response.text,features='html.parser')
        url = soup.find('a',id='NEW_UPLOAD')['href']

        payload = {
            'doBriefcaseAction':'1',
            'sendUID':'',
            'actionAttachDone':'Hecho'
        }

        filename = filepath.split('/')[-1]
        size=os.path.getsize(filepath)
        start = time.time()
        with open(filepath, "rb") as f:
            b = f'---------------------------{uuid.uuid4().hex}'
            print(b)
            payload["fileUpload"] = (filename,f)
            e = MultipartEncoder(fields=payload,boundary=b)
            m = MultipartEncoderMonitor(e,lambda monitor: upload_callback(monitor,size,filename,start,bot,message))
            response=self.__session.post(f'https://correo.uclv.edu.cu/h/search{url}',data=m,headers={'Content-Disposition':'form-data',"Content-Type": m.content_type,"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36"})
            print(response.status_code)
        
        return f'{self.host}home/{self.username}/Briefcase/{quote(filename)}?auth=co'