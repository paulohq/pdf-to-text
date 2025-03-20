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
fields = {'X1': '', 'X2': '', 'ENTRADAX': '', 'Nome/Razão Social': '', 'CNPJ/CPF': '', 'DESTINATÁRIO\nNome/Razão Social': '', 'Data Emissão': '', 'Valor Total da Nota': 0, 'Inscrição Estadual do Substituto': 0, 'Alíquota': 0, 'GADO BOVINO': ''}

meses = {'01': 'Janeiro', '02': 'Fevereiro', '03': 'Março', '04': 'Abril', '05': 'Maio', '06': 'Junho', '07': 'Julho', '08': 'Agosto', '09': 'Setembro', '10': 'Outubro', '11': 'Novembro', '12': 'Dezembro'}

def load_pdf(dir):
    # Reads files from the directory.
    files = os.listdir(dir)

    cont = 0
    # iterates over the files.
    for file in files:
        if file[-3:].lower() == 'pdf':
            # Open the file for reading.
            with open(dir + '/' + file, 'rb') as pdf_file:
                print('Arquivo: ' + file)
                # Reads pdf file.
                pdf_read = PdfReader(pdf_file)
                # Get number of pages from file.
                num_pages = len(pdf_read.pages)

                # iterate over pages.
                for page_num in range(num_pages):
                    page = pdf_read.pages[page_num]

                    text = page.extract_text()

                    # Iterate over fields.
                    for key in fields:
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
                                fields[key] = "SAIDA"
                            # else if it's the field "X2" then set value = ENTRADA
                            elif key == 'X2':
                                fields[key] = "ENTRADA"
                            elif key == 'ENTRADAX':
                                fields[key] = 'ENTRADA'
                            # else if it's the field "Valtor Total da Nota" then remove spaces.
                            elif key == 'Valor Total da Nota':
                                value = text[index_start:index_end].replace("\n", "")
                                fields[key] = re.sub(r'[A-Z]|[a-z]|\s', "", value)
                            elif key == 'GADO BOVINO':
                                fields[key] = 'COMPRA DE GADO DE '
                            # else set value
                            else:
                                fields[key] = text[index_start:index_end].replace("\n", "")

                            #print(key + ': ' + fields[key])

            cont += 1
            print('Contador: ' + str(cont))
            print('Data Emissão: ' + fields['Data Emissão'])
            historico = ''
            if fields['X1'] == 'SAIDA':
                # Nota de saída de terceiro para o destinatário PAULO HENRIQUE DA SILVA.
                if fields['GADO BOVINO'] == 'COMPRA DE GADO DE ':
                    conta = '2.21.001'
                    historico = 'COMPRA DE GADO DE '
                else:
                    conta = '2.23.004'
                    historico = "COMPRA NA EMPRESA "
            elif fields['X2'] == 'ENTRADA' or fields['ENTRADAX'] == 'ENTRADA':
                conta = '1.15.001'
                historico = "VENDA DE GADO PARA "
            elif fields['X2'] == 'COMPRA':
                conta = '2.21.001'
                historico = 'COMPRA DE GADO DE '

            print('Conta: ' + conta)
            historico = historico + fields['Nome/Razão Social'] + " CNPJ: " + fields['CNPJ/CPF'] + " NF: " + str(fields['Inscrição Estadual do Substituto']) + " SE: " + str(fields['Alíquota'])
            print('Histórico: ' + historico)
            print('Valor: ' + fields['Valor Total da Nota'])
            #print(fields)
            #insert_update_AR('xml/DEC-AR-2024-copy.xml')
            print("##############################################################################################################")
            for key in fields:
                fields[key] = ''

def insert_update_AR(file):
    tree = ET.parse(file)
    root = tree.getroot()
    conta = ''

    mes = fields['Data Emissão'][3:5]
    #DA CIA BRASILEIRA DE DISTRIBUICAO CNPJ 47.508.411/0786-94 NF 604798 SE 302
    historico = "COMPRA DA EMPRESA " + fields['Nome/Razão Social'] + " CNPJ: " + fields['CNPJ/CPF'] + " NF: " + str(fields['Inscrição Estadual do Substituto']) + " SE: " + str(fields['Alíquota'])
    if fields['X1'] == 'SAIDA':
        conta = '2.23.004'
    elif fields['X2'] == 'VENDA':
        conta = '1.15.001'
    elif fields['X2'] == 'COMPRA':
        conta = '2.21.001'

    # encontra o nó consolidação para atualizar o totalDespesas ou totalReceitas.
    for el in root.iter('consolidacao'):
        # Se for registro de SAIDA ou COMPRA então atualiza o valor do campo totalDespesas.
        if (fields['X1'] == 'SAIDA') or (fields['X1'] == 'COMPRA'):
            vl = float(el.get('totalDespesas').replace('.','').replace(',','.')) + float(str(fields['Valor Total da Nota']).replace('.',',').replace(',','.'))
            # converte para decimal com dois dígitos.
            vl = f'{vl:,.2f}'
            # substitui "." por "," e grava no campo saldo do item.
            el.set('totalDespesas', vl.replace('.','*').replace(',','.').replace('*', ','))
        # Senão se for registro de VENDA então atualiza o valor do campo totalReceitas.
        elif fields['X2'] == 'VENDA':
            #vl = float(el.attrib.values()[4].replace(',','.')) + float(str(fields['Valor Total da Nota']).replace(',','.'))
            vl = float(el.get('totalReceitas').replace('.','').replace(',','.')) + float(str(fields['Valor Total da Nota']).replace('.',',').replace(',','.'))
            # converte para decimal com dois dígitos.
            vl = f'{vl:,.2f}'
            # substitui "." por "," e grava no campo saldo do item.
            el.set('totalReceitas', vl.replace('.','*').replace(',','.').replace('*', ','))

    # Itera sobre o nó consolidação para encontrar o mês que será consolidado.
    for el in root[1].iterchildren():
        # Se a tag do nó for igual ao mês do registro que será alterado.
        if el.get('mes') == meses[mes]:
            # Se for registro de SAIDA ou COMPRA então atualiza o valor do campo despesas.
            if (fields['X1'] == 'SAIDA') or (fields['X1'] == 'COMPRA'):
                vl = float(el.get('despesas').replace('.','').replace(',','.')) + float(str(fields['Valor Total da Nota']).replace('.',',').replace(',','.'))
                # converte para decimal com dois dígitos.
                vl = f'{vl:,.2f}'
                # substitui "." por "," e grava no campo saldo do item.
                el.set('despesas', vl.replace('.','*').replace(',','.').replace('*', ','))

            # Senão se for registro de VENDA então atualiza o valor do campo receitas.
            elif fields['X2'] == 'VENDA':
                vl = float(el.get('receitas').replace('.','').replace(',','.')) + float(str(fields['Valor Total da Nota']).replace('.',',').replace(',','.'))
                # converte para decimal com dois dígitos.
                vl = f'{vl:,.2f}'
                # substitui "." por "," e grava no campo saldo do item.
                el.set('receitas', vl.replace('.','*').replace(',','.').replace('*', ','))
            break

    # itera sobre o terceiro elemento abaixo do nó root (escrituracao).
    for child in root[2]:
        if child.tag != 'colecaoPlanoContas':
            # se o atributo nomeMes (que é numérico) do nó for igual ao mês do registro que será adicionado.
            if child.get('nomeMes').rjust(2, '0') == mes:
                # soma valor ao saldo do item.
                #vl = float(child.get('saldo').replace('.','').replace(',','.')) + (float(str(fields['Valor Total da Nota']).replace('.',',').replace(',','.')) * (-1 if (fields['X1'] == 'SAIDA') or (fields['X1'] == 'COMPRA') else 1))
                # converte para decimal com dois dígitos.
                #vl = f'{vl:,.2f}'
                # substitui "." por "," e grava no campo saldo do item.
                #vl = vl.replace('.','*').replace(',','.').replace('*', ',')
                #child.set('saldo', vl)
                # Se for registro de SAIDA ou COMPRA então atualiza o valor do campo despesas.
                if (fields['X1'] == 'SAIDA') or (fields['X1'] == 'COMPRA'):
                    vl = float(child.get('totalDespesaCusteioInvestimentos').replace('.','').replace(',','.')) + float(str(fields['Valor Total da Nota']).replace('.',',').replace(',','.'))
                    # converte para decimal com dois dígitos.
                    vl = f'{vl:,.2f}'
                    # substitui "." por "," e grava no campo saldo do item.
                    vl = vl.replace('.','*').replace(',','.').replace('*', ',')
                    child.set('totalDespesaCusteioInvestimentos', vl)
                    child.set('totalDespesaCusteioInvestimentosPendencia',vl)
                # Senão se for registro de VENDA então atualiza o valor do campo receitas.
                elif fields['X2'] == 'VENDA':
                    vl = float(child.get('totalReceitaDaAtividadeRural').replace('.','').replace(',','.')) + float(str(fields['Valor Total da Nota']).replace('.',',').replace(',','.'))
                    # converte para decimal com dois dígitos.
                    vl = f'{vl:,.2f}'
                    # substitui "." por "," e grava no campo saldo do item.
                    vl = vl.replace('.','*').replace(',','.').replace('*', ',')
                    child.set('totalReceitaDaAtividadeRural', vl.replace('-', ''))
                    child.set('totalReceitaDaAtividadeRuralPendencia',vl.replace('-', ''))

                # atualiza saldo
                saldo = float(child.get('totalReceitaDaAtividadeRural').replace('.','').replace(',','.')) - float(child.get('totalDespesaCusteioInvestimentos').replace('.','').replace(',','.'))
                # converte para decimal com dois dígitos.
                saldo = f'{saldo:,.2f}'
                # substitui "." por "," e grava no campo saldo do item.
                saldo = saldo.replace('.','*').replace(',','.').replace('*', ',')
                child.set('saldo', saldo)

                # adiciona nó item no mês.
                element = ET.SubElement(root[2][int(mes)], 'item')
                # adiciona as tags no elemento adicionado acima.
                element.set('classificacaoConta', '')
                element.set('codTipoContaSelecao', conta)
                element.set('data', fields['Data Emissão'])
                element.set('historico', historico)
                element.set('nomeAbaConta', meses[mes][0:3].upper())
                element.set('pais', "105")
                element.set('valor', fields['Valor Total da Nota'])
                break

    tree.write('xml/DEC-AR-2024-copy.xml')

def main(dir):
    load_pdf(dir)

if __name__ == "__main__":
    main(sys.argv[1])