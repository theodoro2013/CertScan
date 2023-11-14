import re
import subprocess
import json
import requests
from subprocess import Popen
import tkinter
from tkinter import ttk

#---- Global Variables ----
CertSerialNumberBD = []
log = []
CertSerialNumber=0
CertExported = 0
CertLike = 0
link = "https://coliseucertificados-default-rtdb.firebaseio.com/"
p = Popen(['certutil', '-user', '-store', 'My'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,universal_newlines=True)
#-- Global Variables END ----

def getcert(): 

    global log
    global CertExported  
    global CertLike 
    global link
    global p
    global CertSerialNumber
    global CertSerialNumberBD

    var_barra.set(0)

    output, errors = p.communicate()

    var_barra.set(10)

    #-- Principal Text Colect and Filter ----
    t=re.compile(r'[=]{16}\s[a-zA-Z0-9éú ]+:[0-9a-zA-z ]+\s[0-9a-zA-z ]+:[-a-zA-Z0-9éú=,@. ]+\s[-a-zA-Z0-9éú=,@.: ]+[0-9]+[/][0-9]+[/][0-9]+[ 0-9:]+\s[-a-zA-Z0-9éú=,@.: ]+[0-9]+[/][0-9]+[/][0-9]+[ 0-9:]+\s[-a-zA-Z0-9éú=,@.: ]+:[0-9]{14}[,]')
    output = t.findall(output)
    QTDCert = (len(output))
    output=str(output)

    var_barra.set(20)

    #-- Serie Number Colect and Filter ----
    t = re.compile(r'[=]{16}.[a-zA-Z0-9-záàâãéèêíïóôõöúçñÁÀÂÃÉÈÍÏÓÔÕÖÚÇÑ ]+: [a-zA-Z0-9-záàâãéèêíïóôõöúçñÁÀÂÃÉÈÍÏÓÔÕÖÚÇÑ ]+')              
    CertSerialNumber = t.findall(output)
    CertSerialNumber=str(CertSerialNumber)
    t = re.compile(r': [A-Za-z0-9]+')              
    CertSerialNumber = t.findall(CertSerialNumber)
    CertSerialNumber=str(CertSerialNumber)
    t = re.compile(r'[A-Za-z0-9]+')              
    CertSerialNumber = t.findall(CertSerialNumber)

    if (QTDCert==(len(CertSerialNumber))):

        var_barra.set(30)

        #-- Corporate Name Colect and Filter ----
        t = re.compile(r'CN=[A-Z0-9-,&. ]+[:]')
        CorporateName = t.findall(output)

        if (QTDCert==(len(CorporateName))):

            var_barra.set(40)

            #-- CNPJ Colect and Filter ----
            t = re.compile(r':[0-9]{14}[,]')
            CNPJ = t.findall(output)
            CNPJ = str(CNPJ)
            t = re.compile(r'[0-9]{14}')
            CNPJ = t.findall(CNPJ)

            if (QTDCert==(len(CNPJ))):

                var_barra.set(50)

                #-- Shelf Life Colect and Filter ----
                t = re.compile(r'NotAfter: [0-9]+[/][0-9]+[/]....')
                ShelfLife = t.findall(output)
                ShelfLife = str(ShelfLife)
                t = re.compile(r'[0-9]+[/][0-9]+[/][0-9]+')
                ShelfLife = t.findall(ShelfLife)

                if (QTDCert==(len(ShelfLife))):

                    var_barra.set(60)

                    # Consulta aos certificados do banco
                    requisicaoBD = requests.get(f'{link}/Certificados.json')
                    CertImport = requisicaoBD.json()
                    Dic_CertImport = dict(CertImport)

                    var_barra.set(70)

                    # Colect serial numbers from DB
                    for k, v in Dic_CertImport.items():
                        CertSerialNumberBD.append(v['Numero de Série'])

                    # Most quantify certs on DB
                    QTDSerieBD = len(CertSerialNumberBD)

                    var_barra.set(80)

                    for i in range(0, QTDCert):

                        # Tratamento dos dados coletados
                        CorporateName[i] = re.sub('CN=', '', CorporateName[i])
                        CorporateName[i] = re.sub(':', '', CorporateName[i])
                        CertSerialNumber[i] = CertSerialNumber[i]
                        ShelfLife[i] = ShelfLife[i]
                        CNPJ[i] = CNPJ[i]
                        
                    var_barra.set(90)

                    for i in range(0, QTDCert):

                        CertLike=0

                        for j in range(0, QTDSerieBD):
                            if (CertSerialNumber[i] == CertSerialNumberBD[j]):
                                CertLike = 1

                        if (CertLike == 0):

                            dados = {'Data de vencimento': (ShelfLife[i]),
                                    'CNPJ': (CNPJ[i]), 
                                    'Empresa': (CorporateName[i]),
                                    'Numero de Série': (CertSerialNumber[i])}
                            requisicao = requests.post(f'{link}/Certificados/.json', data=json.dumps(dados))
                            requisicao=(str(requisicao))
                            log.append(requisicao)
                            if (requisicao=='<Response [200]>'):
                                CertExported=CertExported+1
                    
                    Concluido = ttk.Label(root, text='Concluído',background='white')
                    Concluido.place(x=90, y=50)
                    Sucesso = ttk.Label(root, text=f'{CertExported} Certificados exportados com sucesso!',background='white')

                    var_barra.set(100)

                    Sucesso.place(x=20, y=100) 
                else:
                    Cause='Miss mach info'
                    Type='Erro ao escanear certificado'
                    Descript='Campo (ShelfLife) \n Não corresponde ao esperado.'
                    error(Cause,Type,Descript)
            else:
                Cause='Miss mach info'
                Type='Erro ao escanear certificado'
                Descript='Campo (CNPJ) \n Não corresponde ao esperado.'
                error(Cause,Type,Descript)
        else:
            Cause='Miss mach info'
            Type='Erro ao escanear certificado'
            Descript='Campo (CorporateName) \n Não corresponde ao esperado.'
            error(Cause,Type,Descript)
    else:
        Cause='Miss mach info'
        Type='Erro ao escanear certificado'
        Descript='Campo (CertSerialNumber) \n Não corresponde ao esperado.'
        error(Cause,Type,Descript)

def ScannedTable():
        global link
        global CertSerialNumber
        global CertSerialNumberBD
        output, errors = p.communicate()
        
        if (CertSerialNumber==0):
            error('Not Scan','Erro ao gerar tabela.','Nenhum certificado escaneado.')
        else:
            FilterMenu = tkinter.Tk()
            FilterMenu.title('Certificado(s)')
            FilterMenu.geometry("550x270+250+100")
            FilterMenu['bg']=['white']

            requisicao = requests.get(f'{link}/Certificados.json')
            CertImport = requisicao.json()
            Dic_CertImport=dict(CertImport)
            tabela=ttk.Treeview(FilterMenu,columns=('Empresa','CNPJ','Data de vencimento','Numero de Série'), show='headings')
            tabela.column('Empresa',minwidth=200,width=200)
            tabela.column('CNPJ',minwidth=100,width=100)
            tabela.column('Data de vencimento',minwidth=100,width=100)
            tabela.column('Numero de Série',minwidth=120,width=120)
            tabela.heading('Empresa',text='Empresa')
            tabela.heading('CNPJ',text='CNPJ')
            tabela.heading('Data de vencimento',text='Data de vencimento')
            tabela.heading('Numero de Série',text='Numero de Série')
            qtdcertlocal=len(CertSerialNumber)
            for k,v in Dic_CertImport.items():
                for i in range (0,qtdcertlocal):
                    if (CertSerialNumber[i]==v['Numero de Série']):
                        tabela.insert('','end',values=(v['Empresa'],v['CNPJ'],v['Data de vencimento'],v['Numero de Série']))

            tabela.place(x=10, y=10)

def error(Cause,Type,Descript):
    erro = tkinter.Tk()
    erro.title(f'Erro {Cause}')
    erro.geometry("280x150+200+50")
    erro['bg']=['black']
    LB_ErrorType = ttk.Label(erro,foreground='white', font= 15, text=Type,background='black')
    LB_ErrorType.place(relx=0.25, rely=0.2)
    LB_ErrorDescript = ttk.Label(erro,foreground='white', text=Descript,background='black')
    LB_ErrorDescript.place(relx=0.1, rely=0.5)
    erro = tkinter.Tk()

root = tkinter.Tk()  
root.title('Coliseu Scan')
root.geometry("240x125+200+50")
root['bg']=['white']

var_barra = tkinter.DoubleVar()
minha_barra = ttk.Progressbar(root, variable=var_barra, maximum=100)
minha_barra.place(x=70, y=75)
var_barra.set(0)

scan_button = ttk.Button(root,command=getcert, text='Scan')
scan_button.place(x=80, y=20)

menubar = tkinter.Menu(root)
root['menu'] = menubar

menubar.add_cascade(command= ScannedTable, label='Certificados')

root.mainloop()
