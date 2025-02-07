import sys
import os
from PyPDF2 import PdfReader
import tabula

# os.getcwd() : mostra o diretório atual
# os.chdir() : muda de diretório
# listdir() : lista os arquivos presentes no diretório
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
                print(text)

#def extract():


def main(dir):
    load_pdf(dir)
   # extract()

if __name__ == "__main__":
    main(sys.argv[1])