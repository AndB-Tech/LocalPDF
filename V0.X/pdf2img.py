import os, sys

# name the file to turn into images
pdf_file = "Brauneck_Andreas_Urkunden.pdf"


#############################################################

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Installing PyMuPDF (fitz)...")
    os.system(f'{sys.executable} -m pip install --upgrade PyMuPDF')
# -- above lines try to install requests module if not present
# -- if all went well, import required module again ( for global access)
    import fitz  # PyMuPDF

wd = os.path.dirname(os.path.realpath(__file__))
    
doc = fitz.open(f"{wd}/{pdf_file}")
for i in range(doc.page_count):
    page = doc.load_page(i)
    # drastically reduce quality: scale down to 10% and use grayscale without alpha
    pix = page.get_pixmap(matrix=fitz.Matrix(0.2, 0.2))
    output = f"{wd}/page_{i+1}.png"
    pix.save(output)
doc.close()