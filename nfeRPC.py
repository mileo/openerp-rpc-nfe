# coding: utf-8
#################################################################################
#									                                         	#
#		luisfelipemileo@gmail.com - Luis Felipe Miléo							#
#							                                         			#
#################################################################################
import xmlrpclib
import time


#Configs


server='localhost:8069'
dbname='db'
company='empresa'
username='admin'
pwd='admin'
SAVE_DIR=''
ambiente='2' #Produção 1 - Homologação 2 

def grava_no_arquivo(txt, nomearquivo='exportado-nfe.txt', mode="w", ql="\n"):
    with open(nomearquivo, mode) as bol:
        bol.write(txt + ql)

common = xmlrpclib.ServerProxy ('http://'+server+'/xmlrpc/common')
sock = xmlrpclib.ServerProxy('http://'+server+'/xmlrpc/object')

uid = common.login(dbname, username, pwd)
print "Tentando conectar ao servidor:", server
#if uid:
print "Conectado com user",username, "ID:",uid
args = [('name', '=', company)]
company_id = sock.execute(dbname, uid, pwd, 'res.company', 'search', args)

args = [('state','=','sefaz_export'),('nfe_export_date','=',False),('own_invoice','=',True)]

while True:
    invoice_ids = sock.execute(dbname,uid,pwd,'account.invoice','search',args)
    if invoice_ids:
        print 'Invoices recebidas:',invoice_ids
        grava_no_arquivo(sock.execute(dbname,uid,pwd,'account.invoice','nfe_export_txt',invoice_ids,ambiente))
    time.sleep(2)







