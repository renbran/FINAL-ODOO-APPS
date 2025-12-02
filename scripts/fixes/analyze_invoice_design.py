#!/usr/bin/env python3
"""Analyze the invoice PDF to understand its design structure"""

try:
    import fitz  # PyMuPDF
    from PIL import Image
    import io
    
    pdf_path = "sample_invoice.pdf"
    
    print("=" * 80)
    print("INVOICE PDF DESIGN ANALYSIS")
    print("=" * 80)
    
    # Open the PDF
    doc = fitz.open(pdf_path)
    
    print(f"\n📄 Total Pages: {len(doc)}")
    
    # Analyze first page (most important for header/footer design)
    page = doc[0]
    
    print(f"\n📐 Page Dimensions: {page.rect.width} x {page.rect.height} pts")
    
    # Extract text to understand layout
    text = page.get_text()
    print("\n📝 Text Content (First 1000 chars):")
    print("-" * 80)
    print(text[:1000])
    print("-" * 80)
    
    # Check for images
    image_list = page.get_images()
    print(f"\n🖼️  Images Found: {len(image_list)}")
    
    if image_list:
        for idx, img in enumerate(image_list[:3]):  # First 3 images
            xref = img[0]
            base_image = doc.extract_image(xref)
            print(f"\n   Image {idx+1}:")
            print(f"   - Format: {base_image['ext']}")
            print(f"   - Size: {base_image['width']}x{base_image['height']} px")
            print(f"   - Color Space: {base_image.get('colorspace', 'Unknown')}")
    
    # Extract blocks for layout analysis
    blocks = page.get_text("dict")["blocks"]
    
    print(f"\n📦 Layout Blocks: {len(blocks)}")
    
    # Analyze header area (top 150 pts)
    header_blocks = [b for b in blocks if b.get("bbox") and b["bbox"][1] < 150]
    print(f"\n🔝 Header Area Blocks: {len(header_blocks)}")
    
    # Analyze footer area (bottom 100 pts)
    page_height = page.rect.height
    footer_blocks = [b for b in blocks if b.get("bbox") and b["bbox"][3] > page_height - 100]
    print(f"\n🔽 Footer Area Blocks: {len(footer_blocks)}")
    
    # Check for colored rectangles (background design elements)
    drawings = page.get_drawings()
    print(f"\n🎨 Drawing Elements: {len(drawings)}")
    
    colors_found = set()
    rectangles = []
    for draw in drawings[:10]:  # First 10 drawings
        if 'rect' in draw and draw['rect']:
            rectangles.append(draw['rect'])
        if 'color' in draw and draw['color']:
            colors_found.add(str(draw['color']))
    
    print(f"\n   Rectangles: {len([r for r in rectangles if r])}")
    print(f"   Colors used: {len(colors_found)}")
    if colors_found:
        print(f"   Sample colors: {list(colors_found)[:5]}")
    
    # Get bounding boxes for visual structure
    print("\n📊 Visual Structure:")
    print(f"   Header elements (y < 150): {len([b for b in blocks if b.get('bbox') and b['bbox'][1] < 150])}")
    print(f"   Body elements (150 < y < {page_height-100}): {len([b for b in blocks if b.get('bbox') and 150 < b['bbox'][1] < page_height-100])}")
    print(f"   Footer elements (y > {page_height-100}): {len([b for b in blocks if b.get('bbox') and b['bbox'][3] > page_height-100])}")
    
    doc.close()
    
    print("\n" + "=" * 80)
    print("✅ Analysis Complete!")
    print("=" * 80)

except ImportError as e:
    print(f"⚠️  Missing library: {e}")
    print("\nPlease install: pip install PyMuPDF pillow")
except FileNotFoundError:
    print("⚠️  PDF file not found: sample_invoice.pdf")
except Exception as e:
    print(f"❌ Error analyzing PDF: {e}")
    import traceback
    traceback.print_exc()
