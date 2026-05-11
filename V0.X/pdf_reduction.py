"""
PDF Compressor Script using PyMuPDF

This script compresses a multi-page PDF by downscaling page images
iteratively until the file size is below a target (2 MB). 
It automatically sets the working directory to the script's location.

Dependencies:
- PyMuPDF (install via `pip install pymupdf`)
"""

import os
import sys
import subprocess

# Try importing PyMuPDF (fitz)
try:
    import fitz
except ImportError:
    print("PyMuPDF not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pymupdf"])
    import fitz
    print("PyMuPDF installed successfully!")

INPUT_FILE = "Brauneck_Andreas_Abitur_Urkunde.pdf"
OUTPUT_FILE = "compressed.pdf"
TARGET_SIZE = 2 * 1024 * 1024  # 2 MB → 2 * 1024 KB * 1024 bytes = 2,097,152 bytes
START_DPI = 150
MIN_DPI = 50  # nicht kleiner als 50 dpi, sonst kaum lesbar

def compress_pdf_to_target(input_file, output_file, target_size, start_dpi=150, min_dpi=50):
    dpi = start_dpi

    while dpi >= min_dpi:
        doc = fitz.open(input_file)
        new_pdf = fitz.open()

        zoom = dpi / 72
        matrix = fitz.Matrix(zoom, zoom)

        for page in doc:
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            rect = fitz.Rect(0, 0, pix.width, pix.height)

            new_page = new_pdf.new_page(width=pix.width, height=pix.height)
            new_page.insert_image(rect, pixmap=pix)

        new_pdf.save(output_file, deflate=True)
        doc.close()
        new_pdf.close()

        size = os.path.getsize(output_file)

        print(f"👉 DPI {dpi}: {size/1024/1024:.2f} MB")

        if size <= target_size:
            print(f"✅ Ziel erreicht bei {dpi} DPI ({size/1024/1024:.2f} MB)")
            return True

        dpi -= 10  # Schrittweise DPI reduzieren

    print("⚠️ Zielgröße nicht erreicht – Mindest-DPI erreicht.")
    return False

def main():
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    os.chdir(script_dir)

    if not os.path.exists(INPUT_FILE):
        print(f"❌ Eingabedatei '{INPUT_FILE}' nicht gefunden!")
        return

    compress_pdf_to_target(INPUT_FILE, OUTPUT_FILE, TARGET_SIZE, START_DPI, MIN_DPI)

if __name__ == "__main__":
    main()