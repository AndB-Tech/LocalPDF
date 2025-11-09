# LocalPDF 📝

**LocalPDF** is a Windows desktop application for editing PDF files locally.  
It provides tools for splitting, reordering, resizing, interleaving scanned pages, and normalizing page sizes to A4. Built with **Python** and **PyQt6**, it can be turned into a standalone executable.

---

## Table of Contents
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Creating an Executable](#creating-an-executable)
- [Dependencies](#dependencies)
- [Credits](#credits)

---

## Features
- **Split PDF**: Extract specific pages from a PDF.
- **Reorder PDF**: Rearrange pages of up to two PDF visually in a GUI.
- **Resize PDF**: Change file-size sizes of a PDF.
- **Interleave Scanned Pages**: Merge even and odd pages from scanned documents.
- **Normalize Pages**: Resize all pages to A4.

---

## Project Structure

- **app.py**  
  Main window containing all PDF tools.
  
- **_resize.py**  
  Handles PDF resizing.

- **_extract.py**  
  Handles extraction of specific pages.

- **_reorder.py**  
  Handles page reordering with a visual viewer.

- **_interleave.py**  
  Handles interleaving of uneven/even pages from scans.

- **_normalize.py**  
  Normalizes all pages to A4 size.

- **_baseWindows.py**
  Custom QMainWindow for Application.

---

## Installation

### Option 1: Get Release (Python Unnecessary)

1. Download Release
2. Unzip the File
3. Execute LocalPDF.exe

### Option 2: Run from Code

1. Clone the repository:
   ```bash
   git clone https://github.com/AndB-Tech/LocalPDF.git
   cd LocalPDF

2. Create a virtual enviroment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    venv\Scripts\activate     # Windows

3. Install dependencies:
    ```bash
    pip install -r requirements.txt

4. Running the App
    ```bash
    python app.py
    
---

## Creating an Executable

  ```bash
  pip install pyinstaller

### Option 1: Folder-based executable (smaller build time)
    python -m PyInstaller --windowed --name "LocalPDF" --icon "hard/path/to/LocalPDF/icon/document-pdf-text.png" --add-data "hard/path/to/LocalPDF/icon;icon" --add-data "hard/path/to/LocalPDF/created_images;created_images" --distpath "hard/path/to/LocalPDF/pyinstaller/V1.1/dist" --workpath "hard/path/to/LocalPDF/pyinstaller/V1.1/build" --specpath "hard/path/to/LocalPDF/pyinstaller/V1.1/spec" app.py

### Option 2: Single-file executable (larger size, easier distribution)
    python -m PyInstaller --onefile --windowed --name "LocalPDF" --icon "hard/path/to/LocalPDF/icon/document-pdf-text.png" --add-data "hard/path/to/LocalPDF/icon;icon" --add-data "hard/path/to/LocalPDF/created_images;created_images" --distpath "hard/path/to/LocalPDF/pyinstaller/v1.0/dist" --workpath "hard/path/to/LocalPDF/pyinstaller/v1.0/build" --specpath "hard/path/to/LocalPDF/pyinstaller/v1.0/spec" app.py

---

## Dependencies

- Python 3.11+
- PyQt6
- PyMuPDF
- pypdf

---

## Credits

- Icons from the [Fugue Icons](https://p.yusukekamiyamane.com/) set by [Yusuke Kamiyamane](https://p.yusukekamiyamane.com/),  
  licensed under [Creative Commons Attribution 3.0 License](https://creativecommons.org/licenses/by/3.0/).
