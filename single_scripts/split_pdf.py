import os

# name the file and the page numbers to get
in_file = "Brauneck_Andreas_MSc_Vorläufiges_Zeugnis.pdf"
get_pages = [3,4]

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
in_file = wd + "/" + in_file

if in_file != "" and get_pages != []:
    reader = PdfReader(in_file)
    merger = PdfWriter()

    # iterate over all pages and check if page is to be kept
    for page in range(0,len(reader.pages)):
        #print(page+1)
        if page + 1 in get_pages:
            #print(True)
            merger.add_page(reader.pages[page])

    merger.write(wd + "/" + out_file)
    merger.close() 
    print("Finished extracting pages!")
else:
    print("No file found!")