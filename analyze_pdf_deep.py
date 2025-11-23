import PyPDF2
import re

pdf_path = r'D:\Downloader\14967.pdf'

with open(pdf_path, 'rb') as pdf:
    reader = PyPDF2.PdfReader(pdf)
    page = reader.pages[0]
    
    print('=== DEEP PDF ANALYSIS ===')
    
    # Check if page has annotations or form fields
    if '/Annots' in page:
        print(f'Annotations: {page["/Annots"]}')
    
    # Get page resources
    if '/Resources' in page:
        resources = page['/Resources']
        print(f'\n=== PAGE RESOURCES ===')
        if '/Font' in resources:
            print(f'Fonts: {list(resources["/Font"].keys())}')
        if '/XObject' in resources:
            print(f'XObjects (images): {list(resources["/XObject"].keys())}')
    
    # Try to get page content stream
    if '/Contents' in page:
        print('\n=== RAW CONTENT STREAM ===')
        try:
            content = page.get_contents()
            if content:
                # Decode and show first 2000 chars of raw PDF commands
                content_data = content.get_data().decode('latin-1', errors='ignore')
                print(content_data[:2000])
                print(f'\n... (Total content length: {len(content_data)} bytes)')
        except Exception as e:
            print(f'Error reading content stream: {e}')
    
    # Check for overlapping text by looking at text positioning
    print('\n=== TEXT EXTRACTION WITH LAYOUT ===')
    try:
        # Try to preserve some layout information
        text = page.extract_text()
        print(text)
    except Exception as e:
        print(f'Error: {e}')
