import PyPDF2
import sys

pdf_path = r'D:\Downloader\14967.pdf'

with open(pdf_path, 'rb') as pdf:
    reader = PyPDF2.PdfReader(pdf)
    
    print('=== PDF ANALYSIS ===')
    print(f'Total Pages: {len(reader.pages)}')
    if reader.metadata:
        print(f'Creator: {reader.metadata.get("/Creator", "N/A")}')
        print(f'Producer: {reader.metadata.get("/Producer", "N/A")}')
    print()
    
    # Get page dimensions
    page = reader.pages[0]
    box = page.mediabox
    width = float(box.width)
    height = float(box.height)
    print(f'Page Size: {width:.2f} x {height:.2f} pts')
    print(f'Page Size (inches): {width/72:.2f} x {height/72:.2f}')
    print()
    
    # Extract all text
    print('=== FULL PAGE CONTENT ===')
    text = page.extract_text()
    
    # Split by lines for better analysis
    lines = text.split('\n')
    for i, line in enumerate(lines, 1):
        if line.strip():
            print(f'{i:3d}: {line}')
    
    print()
    print(f'Total lines: {len([l for l in lines if l.strip()])}')
