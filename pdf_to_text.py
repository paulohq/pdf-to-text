import sys
import os
from PyPDF2 import PdfReader
import tabula
import re

# os.getcwd() : mostra o diretório atual
# os.chdir() : muda de diretório
# listdir() : lista os arquivos presentes no diretório

# Fields that need to be found in file.
fields = ['X1', 'X2', 'Nome/Razão Social', 'CNPJ/CPF', 'Data Emissão', 'Valor Total da Nota', 'Inscrição Estadual do Substituto', 'Alíquota']

dict_fields = {'X1': '', 'X2': '', 'Nome/Razão Social': '', 'CNPJ/CPF': '', 'Data Emissão': '', 'Valor Total da Nota': 0, 'Inscrição Estadual do Substituto': 0, 'Alíquota': 0}

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
                print("##########################################")


def main(dir):
    load_pdf(dir)

if __name__ == "__main__":
    main(sys.argv[1])