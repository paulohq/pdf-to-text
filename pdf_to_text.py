import sys
import os
from PyPDF2 import PdfReader
import tabula
import re
from lxml import etree as ET

# os.getcwd() : mostra o diretório atual
# os.chdir() : muda de diretório
# listdir() : lista os arquivos presentes no diretório

# Fields that need to be found in file.
#fields = ['X1', 'X2', 'Nome/Razão Social', 'CNPJ/CPF', 'Data Emissão', 'Valor Total da Nota', 'Inscrição Estadual do Substituto', 'Alíquota']

dict_fields = {'X1': '', 'X2': '', 'Nome/Razão Social': '', 'CNPJ/CPF': '', 'Data Emissão': '', 'Valor Total da Nota': 0, 'Inscrição Estadual do Substituto': 0, 'Alíquota': 0}

meses = {'01': 'Janeiro', '02': 'Fevereiro', '03': 'Março', '04': 'Abril', '05': 'Maio', '06': 'Junho', '07': 'Julho', '08': 'Agosto', '09': 'Setembro', '10': 'Outubro', '11': 'Novembro', '12': 'Dezembro'}

def load_pdf(dir):
    # Reads files from the directory.
    files = os.listdir(dir)

    # iterates over the files.
    for file in files:
        # Open the file for reading.
        with open(dir + '/' + file, 'rb') as pdf_file:
            # Reads pdf file.
            pdf_read = PdfReader(pdf_file)
            # Get number of pages from file.
            num_pages = len(pdf_read.pages)

            # iterate over pages.
            for page_num in range(num_pages):
                page = pdf_read.pages[page_num]

                text = page.extract_text()

                # Iterate over fields.
                for key in dict_fields:
                    # find the first position of field in file.
                    index_start = text.find(key)

                    if index_start != -1:
                        #  Add the length of the field found above.
                        index_start = index_start + len(key)
                        # Find the position of the next "New Line" after the field (to find the final position of the field's value).
                        # Add 1 because some fields may have a "New Line" at the beginning.
                        index_end = text.find('\n', index_start + 1)

                        # if it's the field "X1" then set value = SAIDA
                        if key == 'X1':
                            dict_fields[key] = "SAIDA"
                        # else if it's the field "X2" then set value = ENTRADA
                        elif key == 'X2':
                            dict_fields[key] = "ENTRADA"
                        # else if it's the field "Valtor Total da Nota" then remove spaces.
                        elif key == 'Valor Total da Nota':
                            value = text[index_start:index_end].replace("\n", "")
                            dict_fields[key] = re.sub(r'[A-Z]|[a-z]|\s', "", value)
                        # else set value
                        else:
                            dict_fields[key] = text[index_start:index_end].replace("\n", "")


                        print(key + ': ' + dict_fields[key])

                print(dict_fields)
                insert_update_AR('xml/dec-ar-2024-formatted.xml')
                print("##########################################")

def insert_update_AR(file):
    tree = ET.parse(file)
    root = tree.getroot()
    conta = ''

    mes = dict_fields['Data Emissão'][3:5]
    #DA CIA BRASILEIRA DE DISTRIBUICAO CNPJ 47.508.411/0786-94 NF 604798 SE 302
    historico = "COMPRA DA EMPRESA " + dict_fields['Nome/Razão Social'] + " CNPJ: " + dict_fields['CNPJ/CPF'] + " NF: " + str(dict_fields['Inscrição Estadual do Substituto']) + " SE: " + str(dict_fields['Alíquota'])
    if dict_fields['X1'] == 'SAIDA':
        conta = '2.23.004'
    elif dict_fields['X2'] == 'VENDA':
        conta = '1.15.001'
    elif dict_fields['X2'] == 'COMPRA':
        conta = '2.21.001'

    # encontra o nó consolidação para atualizar o totalDespesas ou totalReceitas.
    for el in root.iter('consolidacao'):
        # Se for registro de SAIDA ou COMPRA então atualiza o valor do campo totalDespesas.
        if (dict_fields['X1'] == 'SAIDA') or (dict_fields['X1'] == 'COMPRA'):
            vl = float(el.get('totalDespesas').replace('.','').replace(',','.')) + float(str(dict_fields['Valor Total da Nota']).replace('.',',').replace(',','.'))
            # converte para decimal com dois dígitos.
            vl = f'{vl:,.2f}'
            # substitui "." por "," e grava no campo saldo do item.
            el.set('totalDespesas', vl.replace('.','*').replace(',','.').replace('*', ','))
        # Senão se for registro de VENDA então atualiza o valor do campo totalReceitas.
        elif dict_fields['X2'] == 'VENDA':
            #vl = float(el.attrib.values()[4].replace(',','.')) + float(str(dict_fields['Valor Total da Nota']).replace(',','.'))
            vl = float(el.get('totalReceitas').replace('.','').replace(',','.')) + float(str(dict_fields['Valor Total da Nota']).replace('.',',').replace(',','.'))
            # converte para decimal com dois dígitos.
            vl = f'{vl:,.2f}'
            # substitui "." por "," e grava no campo saldo do item.
            el.set('totalReceitas', vl.replace('.','*').replace(',','.').replace('*', ','))

    # Itera sobre o nó consolidação para encontrar o mês que será consolidado.
    for el in root[1].iterchildren():
        # Se a tag do nó for igual ao mês do registro que será alterado.
        if el.get('mes') == meses[mes]:
            # Se for registro de SAIDA ou COMPRA então atualiza o valor do campo despesas.
            if (dict_fields['X1'] == 'SAIDA') or (dict_fields['X1'] == 'COMPRA'):
                vl = float(el.get('despesas').replace('.','').replace(',','.')) + float(str(dict_fields['Valor Total da Nota']).replace('.',',').replace(',','.'))
                # converte para decimal com dois dígitos.
                vl = f'{vl:,.2f}'
                # substitui "." por "," e grava no campo saldo do item.
                el.set('despesas', vl.replace('.','*').replace(',','.').replace('*', ','))
            # Senão se for registro de VENDA então atualiza o valor do campo receitas.
            elif dict_fields['X2'] == 'VENDA':
                vl = float(el.get('receitas').replace('.','').replace(',','.')) + float(str(dict_fields['Valor Total da Nota']).replace('.',',').replace(',','.'))
                # converte para decimal com dois dígitos.
                vl = f'{vl:,.2f}'
                # substitui "." por "," e grava no campo saldo do item.
                el.set('receitas', vl.replace('.','*').replace(',','.').replace('*', ','))

    # itera sobre o terceiro elemento abaixo do nó root (escrituracao).
    for child in root[2]:
        if child.tag != 'colecaoPlanoContas':
            # se o atributo nomeMes (que é numérico) do nó for igual ao mês do registro que será adicionado.
            if child.get('nomeMes').rjust(2, '0') == mes:
                # soma valor ao saldo do item.
                vl = float(child.get('saldo').replace('.','').replace(',','.')) + (float(str(dict_fields['Valor Total da Nota']).replace('.',',').replace(',','.')) * -1)
                # converte para decimal com dois dígitos.
                vl = f'{vl:,.2f}'
                # substitui "." por "," e grava no campo saldo do item.
                child.set('saldo', vl.replace('.','*').replace(',','.').replace('*', ','))

                # adiciona nó item no mês.
                element = ET.SubElement(root[2][mes], 'item')
                # adiciona as tags no elemento adicionado acima.
                element.set('classificacaoConta', '')
                element.set('codTipoContaSelecao', conta)
                element.set('data', dict_fields['Data Emissão'])
                element.set('historico', historico)
                element.set('nomeAbaConta', meses[mes][0:3].upper())
                element.set('pais', "105")
                element.set('valor', dict_fields['Valor Total da Nota'])

    tree.write('xml/AR-output.xml')

def main(dir):
    load_pdf(dir)

if __name__ == "__main__":
    main(sys.argv[1])