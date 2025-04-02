import os
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import pdfkit
from utils import split_songs_into_pages, generate_toc

# Configuration
EXCEL_PATH = 'data/songbook_data.xlsx'
SHEET_NAME = 'Siron'
TEMPLATE_DIR = 'templates'
OUTPUT_DIR = 'output'
WKHTMLTOPDF_PATH = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'  # Update as needed

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Configure PDF options
pdf_config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)

# Initialize Jinja environment
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

def read_song_data():
    """Read song data from Excel file"""
    print(f"Reading data from {EXCEL_PATH}")
    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME)
        return df.fillna('').to_dict('records')  # Convert to list of dictionaries
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return []

def generate_document(template_name, output_filename, context):
    """Generate PDF document from template"""
    try:
        template = env.get_template(template_name)
        html_content = template.render(**context)
        
        # Save HTML for debugging (optional)
        with open(f"{OUTPUT_DIR}/{output_filename}.html", 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Convert HTML to PDF
        pdf_options = {
            'page-size': 'A4' if 'presentation' not in output_filename else None,
            'orientation': 'Portrait' if 'presentation' not in output_filename else 'Landscape',
            'margin-top': '10mm',
            'margin-right': '10mm',
            'margin-bottom': '10mm',
            'margin-left': '10mm',
            'encoding': 'UTF-8',
        }
        
        if 'presentation' in output_filename:
            pdf_options['page-width'] = '384mm'  # 16:9 ratio for landscape A4
            pdf_options['page-height'] = '216mm'
            
        pdfkit.from_string(html_content, f"{OUTPUT_DIR}/{output_filename}.pdf", 
                          configuration=pdf_config, options=pdf_options)
        
        print(f"Generated {output_filename}.pdf")
    except Exception as e:
        print(f"Error generating {output_filename}: {e}")

def main():
    """Main function to generate all documents"""
    print("Starting Siron Song Book Generator")
    
    # Read song data
    songs = read_song_data()
    
    if not songs:
        print("No song data found. Exiting.")
        return
    
    print(f"Found {len(songs)} songs.")
    
    # Prepare data for each document type
    songs_with_pages = split_songs_into_pages(songs)
    
    # Generate table of contents
    toc_by_id = generate_toc(songs, sort_by='id')
    toc_by_name = generate_toc(songs, sort_by='name')
    
    # Generate lyrics book
    generate_document('lyrics_book.html', 'songbook_lyrics', {
        'songs': songs_with_pages,
        'toc_by_id': toc_by_id,
        'toc_by_name': toc_by_name,
        'title': 'Song Book - Lyrics'
    })
    
    # Generate chords book
    generate_document('chords_book.html', 'songbook_chords', {
        'songs': songs_with_pages,
        'toc_by_id': toc_by_id,
        'toc_by_name': toc_by_name,
        'title': 'Song Book - Chords'
    })
    
    # Generate presentation slides
    generate_document('presentation.html', 'songbook_presentation', {
        'songs': songs,
        'title': 'Song Presentation'
    })
    
    print("Document generation complete!")

if __name__ == "__main__":
    main()
