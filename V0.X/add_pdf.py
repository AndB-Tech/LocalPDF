import os

# name the files in the order you need it
pdf_list = []

# name of the finished file
out_file = "result.pdf"


#############################################################

try:
    from pypdf import PdfWriter
except ImportError:
    print("Trying to Install required module: pypdf\n")
    os.system('python -m pip install pypdf')
# -- above lines try to install requests module if not present
# -- if all went well, import required module again ( for global access)
    from pypdf import PdfWriter

merger = PdfWriter()

wd = os.path.dirname(os.path.realpath(__file__))
file_list = os.listdir(wd)

if len(pdf_list) > 0:
    for pdf in pdf_list:
        merger.append(wd + "/" + pdf)
else:
    auto_pdf = []
    for file in file_list:
        if file.endswith("pdf"):
            auto_pdf.append(wd + "/"+ file)
    for pdf in auto_pdf:
        merger.append(pdf)

merger.write(wd + "/" + out_file)
merger.close()