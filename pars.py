#!/usr/bin/python
#coding: utf-8
from bs4 import BeautifulSoup

def check_doctype(html):
    """This function will check which document type we are dealing with, whether
    is the type showing all the revenue information or the one with only a few
    financial info."""
    soup = BeautifulSoup(html)
    second_div = soup.find(id="ctl00_cphPopUp_cmbGrupo_cmbGrupo_c2")
    if not second_div: # if it has no info at all
        return ''
    if second_div.string.strip().encode('utf-8') == 'DFs Individuais': # if it is the one with all info
        return 'df'
    for i in xrange(3,6): # This will also check for the one with all info, iterating through some items in the droplist
        div = soup.find(id="ctl00_cphPopUp_cmbGrupo_cmbGrupo_c"+str(i))
        if div and div.string.strip().encode('utf-8') == 'DFs Individuais': 
            return 'df'
    return 'info' # if none of the above, it's the one with little information

def get_ativo_table(data,html):
    """This function will get all the data from a page that has all revenue
    information. Right now the format on which the data consists, is as follows:
    the key will be the concatenation of 'Descrição' and the year.
    An the value will consist on the cell that corresponds to that key on the table
    Ex.: 'ativo2011' : 4687123.0 """
    soup = BeautifulSoup(html)
    header = soup.tr.extract()
    header_tds = header.findAll('td')
    dates = []
    for i in xrange(2,len(header_tds)):
        date_tag = header_tds[i].contents[-1]
        date_string = date_tag.string.encode('utf-8')[-6:-2] # if it is the 'Demonstração de Resultado' page, the year starts at -6 pos.
        dates.append(date_string)
    ativo = soup.tr.extract()
    ativo_tds = ativo.findAll('td')[2:]
    for i in xrange(len(dates)):
        number = ativo_tds[i].string.strip().encode('utf-8')
        if number:
            number = number.replace('.','')
            number = number.replace(',','.')
            data['ativo'+dates[i]] = float(number) # Here we add the value to its according position at the dictionaire
        else:
            data['ativo'+dates[i]] = 0.0
    return data,dates

def get_fieldname(desc):
    """ Just a small function to translate the Description to a field in the
    table. This is used on the page that has a summary of all the financial
    information."""
    fields = [('Patrimônio Líquido','pat_liquido'), \
                  ('Ativo Total','ativo'), \
                  ('Rec. Liq./Rec. Intermed. Fin./Prem. Seg. Ganhos','receita'), \
                  ('Resultado Bruto','resultado_bruto'), \
                  ('Resultado Líquido','resultado_liq'), \
                  ('Número de Ações, Ex-Tesouraria','qtd_acoes'), \
                  ('Valor Patrimonial de Ação (Reais Unidade)','vlr_acoes'), \
                  ('Resultado Líquido por Ação','result_liq_acoes')]
    for e in fields:
        if desc == e[0]:
            return e[1]
    return 'none'

def get_info_table(data,html):
    """This function will get the data that does not have all the information,
     but it has a little revenue info. Right now the format on which the data is
     as follows, the key will be 'Informação Financeira'(description) concatenated
     with the year. And the value will be consistent with the cell in that table
     key. Ex.: 'Patrimônio Líquido2010': -5210229.0 """
    soup = BeautifulSoup(html)
    header = soup.tr.extract()
    ths = header.findAll('th')
    dates = [ths[i].span.string[-4:] for i in range(1,len(ths)) if ths[i].span.string] # Get the years to concatenate later
    for tr in soup.findAll('tr'): # For each row in the table, it will get the description
        desc = tr.td.extract().string.strip().encode('utf-8')
        field = get_fieldname(desc)
        cols = tr.findAll('td')
        for i in xrange(len(cols)): # Then for each cell, it will get the value
            number = cols[i].string.strip().encode('utf-8')
            if field == 'none':
                continue
            if number:
                number = number.replace('.','')
                number = number.replace(',','.')
                data[field+dates[i]] = float(number) # The key with description concatenated with year
            else: # if it doesn't find any value
                data[field+dates[i]] = 0
    return data

def get_general_data(data,html):
    soup = BeautifulSoup(html)
    data['cnpj'] = soup.find(id='ctl00_cphPopUp_txtCnpj').string.strip().encode('utf-8')
    data['nome'] = soup.find(id='ctl00_cphPopUp_txtNomeEmpresarial').string.strip().encode('utf-8')
    nome_ant = soup.find(id='ctl00_cphPopUp_txtNomeEmpresarialAnterior').string
    data['nome_ant'] = nome_ant.strip().encode('utf-8') if nome_ant else ''
    pagina = soup.find(id='ctl00_cphPopUp_txtPaginaEmissorRedeMundialComputadores').string
    data['pagina'] = pagina.strip().encode('utf-8') if pagina else ''
    return data

def get_address_data(data,html):
    soup = BeautifulSoup(html)
    if soup.find(id='ctl00_cphPopUp_txtLogradouroSede') != None:
        fonte = 'Sede'
    else:
        fonte = 'Correspondencia'
    logradouro = soup.find(id='ctl00_cphPopUp_txtLogradouro'+fonte).string
    complemento = soup.find(id='ctl00_cphPopUp_txtComplemento'+fonte).string
    bairro = soup.find(id='ctl00_cphPopUp_txtBairro'+fonte).string
    endereco = logradouro.strip().encode('utf-8')+' ' if logradouro else ''
    endereco += complemento.strip().encode('utf-8')+' ' if complemento else ''
    endereco += bairro.strip().encode('utf-8') if bairro else ''
    data['endereco'] = endereco.replace(',','')
    cep = soup.find(id='ctl00_cphPopUp_txtCep'+fonte).string
    data['cep'] = cep.strip().encode('utf-8') if cep else ''
    uf = soup.find(id='ctl00_cphPopUp_txtUf'+fonte).string
    data['uf'] = uf.strip().encode('utf-8') if uf else ''
    municipio = soup.find(id='ctl00_cphPopUp_txtMunicipio'+fonte).string
    data['municipio'] = municipio.strip().encode('utf-8') if municipio else ''
    ddd_tel = soup.find(id='ctl00_cphPopUp_txtDTel'+fonte).string
    tel = '('+ddd_tel.strip().encode('utf-8')+')' if ddd_tel else ''
    telefone = soup.find(id='ctl00_cphPopUp_txtTel'+fonte).string
    tel += telefone.strip().encode('utf-8') if telefone else ''
    data['telefone'] = tel
    ddd_fax = soup.find(id='ctl00_cphPopUp_txtDFax'+fonte).string
    tel_fax = '('+ddd_fax.strip().encode('utf-8')+')' if ddd_fax else ''
    fax = soup.find(id='ctl00_cphPopUp_txtFax'+fonte).string
    tel_fax += fax.strip().encode('utf-8') if fax else ''
    data['fax'] = tel_fax
    email = soup.find(id='ctl00_cphPopUp_txtEmail'+fonte).string
    data['email'] = email.strip().encode('utf-8') if email else ''
    return data

def get_receita_table(data,html,dates,result=0):
    soup = BeautifulSoup(html)
    header = soup.tr.extract()
    desc = 'resultado_liq' if result else 'receita'
    receita = soup.tr.extract()
    receita_tds = receita.findAll('td')[2:]
    for i in xrange(len(dates)):
        number = receita_tds[i].string.strip().encode('utf-8')
        if number:
            number = number.replace('.','')
            number = number.replace(',','.')
            data[desc+dates[i]] = float(number)
        else:
            data[desc+dates[i]] = 0.0
    return data

def get_patrimonio_table(data,html,dates):
    soup = BeautifulSoup(html)
    dates.reverse()
    how_many = len(dates)
    rows = soup.findAll('tr')[-how_many:]
    for i in xrange(len(rows)):
        number = rows[i].findAll('td')[-1]
        if number:
            number_str = number.string.strip().encode('utf-8')
        if number_str:
            number_str = number_str.replace('.','')
            number_str = number_str.replace(',','.')
            data['pat_liquido'+dates[i]] = float(number_str)
        else:
            data['pat_liquido'+dates[i]] = 0.0            
    return data

