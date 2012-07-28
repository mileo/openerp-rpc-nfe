# coding: utf-8
##############################################################################
#
#     Copyright (C) 2012  - Luis Felipe Mileo - luisfelipemileo@gmail.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
##############################################################################
import xmlrpclib
import time
import libxml2
import urllib

class openERP(object):

    def __init__(self,export_dir):
        self.server='ip:porta'
        self.dbname='dbname'
        self.company='empresa'
        self.username='admin'
        self.pwd='senha'
        self.SAVE_DIR=''
        self.ambiente='2' #Produção 1 - Homologação 2   
        self.common = xmlrpclib.ServerProxy ('http://'+self.server+'/xmlrpc/common')
        self.sock = xmlrpclib.ServerProxy('http://'+self.server+'/xmlrpc/object')
        self.export_dir = './Envio'
        self.return_dir = './Retorno'

    def login(self):
        self.uid = self.common.login(self.dbname, self.username, self.pwd)
        print "Tentando conectar ao servidor:", self.server
        print "Conectado com user",self.username, "ID:",self.uid
        return self.uid

    def company_id(self):
        return self.sock.execute(self.dbname, self.uid, self.pwd, 'res.company', 'search', [('name', '=', self.company)])

    def execute(self, resource, operation,args,args2=''):
        return self.sock.execute(self.dbname,self.uid,self.pwd,resource,operation,args,args2)
       


class nfe(object):
     
    status = { 'Exportada' : 'exported', 'Autorizada' : 'sefaz_auth', 'Rejeitada' : 'sefaz_exception','Cancelada' : 'sefaz_canceled'}
    arquivo = 'nfe.csv'
    export_args = [('state','=','sefaz_export'),('nfe_export_date','=',False),('own_invoice','=',True)]

    def __init__(self,invoice_id, conn):
        self.invoice_id = []
        self.invoice_id.append(invoice_id)
        self.conn = conn
        self.nfe_status = 'sefaz_export'
        self.internal_number = self.internal_number()[0]['internal_number']
        self.exported_file = self.exportar_nf() 
        grava_no_arquivo(self.exported_file,'Envio/'+self.internal_number+'-nfe.txt')

    def update_nfe_status(self,new_stats):
        self.nfe_status = new_stats
        

    def internal_number(self):
        return self.conn.execute('account.invoice','read',self.invoice_id,['internal_number'])
                   
    def exportar_nf(self):
        return self.conn.execute('account.invoice','nfe_export_txt',self.invoice_id,self.conn.ambiente)

    def update_status(self):
        self.acess_key()
        self.num_lote()
        self.num_rec()
        xml = libxml2.parseFile('Retorno/'+self.num_rec()+'-pro-rec.xml')
        xmlcontext_nfe = xml.xpathNewContext()
        xmlcontext_nfe.xpathRegisterNs('nfe', 'http://www.portalfiscal.inf.br/nfe')
        self.cStat = xmlcontext_nfe.xpathEval("/nfe:retConsReciNFe/nfe:protNFe/nfe:infProt/nfe:cStat")[0].content
        self.dhRecbto = xmlcontext_nfe.xpathEval("/nfe:retConsReciNFe/nfe:protNFe/nfe:infProt/nfe:dhRecbto")[0].content
        self.xMotivo = xmlcontext_nfe.xpathEval("/nfe:retConsReciNFe/nfe:protNFe/nfe:infProt/nfe:xMotivo")[0].content
        conn.execute('account.invoice','write',self.invoice_id,{'nfe_access_key': self.nfe_acess_key,'nfe_status': self.xMotivo,'nfe_date': self.dhRecbto})

        if 'Autorizado' in self.xMotivo:
           # results = conn.sock.exec_workflow (self.conn.dbname, self.conn.uid, self.conn.pwd, 'account.invoice','invoice_open',self.invoice_id)
        return True
        
    def acess_key(self):
        self.nfe_acess_key = ler_arquivo('Retorno/'+self.internal_number+'-nfe.txt').readlines()[2][-44:]
        return self.nfe_acess_key

    def num_lote(self):
        xml = libxml2.parseFile('Retorno/'+self.nfe_acess_key+'-num-lot.xml')
        self.nfe_lote =  xml.xpathEval('/DadosLoteNfe/NumeroLoteGerado')[0].content
        return self.nfe_lote

    def num_rec(self):
        xml = libxml2.parseFile('Retorno/'+str(self.nfe_lote).zfill(15)+'-rec.xml')
        xmlcontext_nfe = xml.xpathNewContext()
        xmlcontext_nfe.xpathRegisterNs('nfe', 'http://www.portalfiscal.inf.br/nfe')       
        self.nfe_num_rec =  xmlcontext_nfe.xpathEval("/nfe:retEnviNFe/nfe:infRec/nfe:nRec")[0].content
        return self.nfe_num_rec
            

    @classmethod
    def get_invoices(self,conn):

        invoice_ids = conn.sock.execute(conn.dbname, conn.uid, conn.pwd,'account.invoice', 'search', self.export_args)
        if invoice_ids:
            return invoice_ids 
        else:
            return False


def grava_no_arquivo(txt, nomearquivo='exportado-nfe.txt', mode="w", ql="\n"):
    with open(nomearquivo, mode) as bol:
        bol.write(txt + '\n')

def ler_arquivo(file_name='exportado-nfe.txt'):
    return open(file_name,'r')

    
if __name__ == "__main__":
    print 'Programa NFE-RPC'
    conn = openERP('')
    conn.login()
    invoice_ids =  nfe.get_invoices(conn)
    

    nfes = []
    if invoice_ids:
        print invoice_ids   
        for ids in invoice_ids:
            print ids
            nfes.append(nfe(ids,conn))
    else: print 'Sem NFs'

# Para atualizar o status das notas nfes[0].update_status()
