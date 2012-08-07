#!/usr/bin/python
#coding: utf-8
## This program consists in a Crawler to get revenue information 
##


import mechanize
import cookielib
import csv
import pars
from bs4 import BeautifulSoup

# Browser
br = mechanize.Browser()

# CookieJar
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)

# Browser options
br.set_handle_equiv(True)
br.set_handle_referer(True)
br.set_handle_redirect(False)
br.set_handle_robots(False)

# Want debugging messages?
br.set_debug_http(True)
br.set_debug_redirects(True)
br.set_debug_responses(True)

# User Agent
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

# Proxy
br.set_proxies({"http":"66.229.18.79:53066"})
Reviewed-by: Vitor <vitor@vitor>

# This url will be used just to validate the session and check for the doc type
validation_url = "http://www.rad.cvm.gov.br/enetconsulta/frmGerenciaPaginaFRE.aspx?CodigoTipoInstituicao=1&NumeroSequencialDocumento="

# With this url it gets all the general information such like address, name, etc.
dados_gerais_url = "http://www.rad.cvm.gov.br/enetconsulta/frmDadosGeraisConsultaNovo.aspx?NumeroSequencialRegistroCvm=1359&NumeroSequencialDocumento="

endereco_url = "http://www.rad.cvm.gov.br/enetconsulta/frmEnderecoConsultaNovo.aspx?NumeroSequencialDocumento="

# If the document is the one showing little revenue information, this will be the
# url to use
info_finance_url = "http://www.rad.cvm.gov.br/enetconsulta/frmInformacoesFinanceirasFRE.aspx?NumeroSequencialDocumento="

# If the document has all the information, this will be the url to use
dfs_url = "http://www.rad.cvm.gov.br/enetconsulta/frmDemonstracaoFinanceiraITR.aspx?Informacao=1&Periodo=0&Grupo=DFs+Individuais&Quadro=Balan%C3%A7o+Patrimonial+Ativo&NomeTipoDocumento=ITR&Titulo=menor&Empresa=nada&DataReferencia=31/03/2012&Versao=2&Demonstracao="

# The first is used to show the 'Balanço Patrimonial Ativo' page
# the other to show the 'Demonstração de Resultado' page
df_ativo, df_receita, df_result, df_patrimonio = 2, 4, 5, 8

# The headers for the csv files with the final data
fieldnames = ['cnpj','nome','nome_ant','pagina', \
                  'endereco','cep','uf','municipio','telefone','fax','email', \
                  'pat_liquido2012','pat_liquido2011','pat_liquido2010', \
                  'pat_liquido2009','pat_liquido2008','pat_liquido2007', \
                  'ativo2012','ativo2011','ativo2010','ativo2009','ativo2008', \
                  'ativo2007','receita2012','receita2011','receita2010', \
                  'receita2009','receita2008','receita2007', \
                  'resultado_bruto2012','resultado_bruto2011', \
                  'resultado_bruto2010','resultado_bruto2009', \
                  'resultado_bruto2008','resultado_bruto2007', \
                  'resultado_liq2012','resultado_liq2011','resultado_liq2010',\
                  'resultado_liq2009','resultado_liq2008','resultado_liq2007', \
                  'qtd_acoes2012','qtd_acoes2011','qtd_acoes2010','qtd_acoes2009',\
                  'qtd_acoes2008','qtd_acoes2007','vlr_acoes2012','vlr_acoes2011',\
                  'vlr_acoes2010','vlr_acoes2009','vlr_acoes2008','vlr_acoes2007',\
                  'result_liq_acoes2012','result_liq_acoes2011', \
                  'result_liq_acoes2010','result_liq_acoes2009', \
                  'result_liq_acoes2008','result_liq_acoes2007']

dados_csv_filename = "/home/vitor/Documents/Projetos/Crawler/CVM/dados2.csv"

with open(dados_csv_filename,'wb') as csvfile:
    writer = csv.DictWriter(csvfile,fieldnames,extrasaction='ignore')
    writer.writeheader()
    for seq_documento in xrange(1,20000):
        try:
            br.open(validation_url+str(seq_documento))
            assert br.viewing_html()
            tipo_doc_tg = pars.check_doctype(br.response().read())
            unit_data = {}
            br.open(dados_gerais_url+str(seq_documento))
            assert br.viewing_html()
            unit_data = pars.get_general_data(unit_data,br.response().read())
            br.open(endereco_url+str(seq_documento))
            assert br.viewing_html()
            unit_data = pars.get_address_data(unit_data,br.response().read())
            if tipo_doc_tg == 'df':
                br.open(dfs_url+str(df_ativo)+"&NumeroSequencialDocumento="+str(seq_documento))
                assert br.viewing_html()
                unit_data,dates = pars.get_ativo_table(unit_data,br.response().read())
                br.open(dfs_url+str(df_receita)+"&NumeroSequencialDocumento="+str(seq_documento))
                assert br.viewing_html()
                unit_data = pars.get_receita_table(unit_data,br.response().read(),dates)
                br.open(dfs_url+str(df_result)+"&NumeroSequencialDocumento="+str(seq_documento))
                assert br.viewing_html()
                unit_data = pars.get_receita_table(unit_data,br.response().read(),dates,df_result)
                br.open(dfs_url+str(df_patrimonio)+"&NumeroSequencialDocumento="+str(seq_documento))
                assert br.viewing_html()
                unit_data = pars.get_patrimonio_table(unit_data,br.response().read(),dates)
                print 'Got: '+str(seq_documento)
            elif tipo_doc_tg == 'info':
                br.open(info_finance_url+str(seq_documento))
                assert br.viewing_html()
                unit_data = pars.get_info_table(unit_data,br.response().read())
                print 'Got: '+str(seq_documento)
            else:
                print "Got: "+str(seq_documento)+" Gen. data!"
            writer.writerow(unit_data)
        except mechanize.HTTPError as s:
            print "error: "+str(seq_documento)+' Not Found! 302Error!'
            continue
