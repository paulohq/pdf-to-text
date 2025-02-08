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
                for field in fields:
                    # find the first position of field in file.
                    index_start = text.find(field)

                    if index_start != -1:
                        #  Add the length of the field found above.
                        index_start = index_start + len(field)
                        # Find the position of the next "New Line" after the field (to find the final position of the field's value).
                        # Add 1 because some fields may have a "New Line" at the beginning.
                        index_end = text.find('\n', index_start + 1)

                        # if it's the field "X1" then set value = SAIDA
                        if field == 'X1':
                            value = "SAIDA"
                        # else if it's the field "X2" then set value = ENTRADA
                        elif field == 'X2':
                            value = "ENTRADA"
                        # else set value
                        else:
                            value = text[index_start:index_end].replace("\n", "")

                        # if it's the field "Valtor Total da Nota" then remove spaces.
                        if field == 'Valor Total da Nota':
                            value = re.sub(r'[A-Z]|[a-z]', "", value)

                        print(field + ': ' + value.strip())


                print("##########################################")


def main(dir):
    load_pdf(dir)

if __name__ == "__main__":
    main(sys.argv[1])