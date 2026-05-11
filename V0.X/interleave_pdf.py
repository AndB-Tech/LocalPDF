import os
from itertools import zip_longest

# name the files with even pages and uneven pages
pdf_uneven = "Mietvertrag_uneven.pdf"
pdf_even = "Mietvertrag_even.pdf"

# name of the finished file
out_file = "result.pdf"


#############################################################

try:
    from pypdf import PdfWriter, PdfReader
except ImportError:
    print("Trying to Install required module: pypdf\n")
    os.system('python -m pip install pypdf')
# -- above lines try to install requests module if not present
# -- if all went well, import required module again ( for global access)
    from pypdf import PdfWriter, PdfReader

wd = os.path.dirname(os.path.realpath(__file__))
pdf_uneven = wd + "/" + pdf_uneven
pdf_even = wd + "/" + pdf_even

if pdf_uneven != "" and pdf_even != "":
    reader_uneven = PdfReader(pdf_uneven)
    reader_even = PdfReader(pdf_even)
    merger = PdfWriter()
    
    # Interleave pages (handles uneven lengths too)
    for odd, even in zip_longest(reader_uneven.pages, reader_even.pages):
        if odd:
            merger.add_page(odd)
        if even:
            merger.add_page(even)

    merger.write(wd + "/" + out_file)
    merger.close()  
else:
    print("No files found!")
