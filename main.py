import os
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import pdfkit
import argparse
from utils import split_songs_into_pages, generate_toc

# Configuration
EXCEL_PATH = 'data/Siron.xlsx'
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
        # Ensure first column is considered as ID regardless of column name
        if len(df.columns) > 0:
            first_col = df.columns[0]
            df['id'] = df[first_col]
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

def generate_single_song(song_id, format_type):
    """Generate a document for a single song"""
    songs = read_song_data()
    
    if not songs:
        print("No song data found. Exiting.")
        return False
    
    # Find the song with the specified ID in the first column (column A)
    # Case-insensitive comparison
    selected_song = None
    for song in songs:
        if str(song.get('id', '')).lower() == str(song_id).lower():
            selected_song = song
            break
    
    if not selected_song:
        print(f"Song with ID '{song_id}' not found. Please check the first column (column A) of your Excel file.")
        return False
    
    # Process the song based on format type
    songs_with_pages = split_songs_into_pages([selected_song])
    
    if format_type == 'lyrics':
        generate_document('single_song_lyrics.html', f'song_{song_id}_lyrics', {
            'song': songs_with_pages[0],
            'title': f'Song {song_id} - Lyrics'
        })
    elif format_type == 'chords':
        generate_document('single_song_chords.html', f'song_{song_id}_chords', {
            'song': songs_with_pages[0],
            'title': f'Song {song_id} - Chords'
        })
    elif format_type == 'presentation':
        generate_document('single_song_presentation.html', f'song_{song_id}_presentation', {
            'song': selected_song,
            'title': f'Song {song_id} - Presentation'
        })
    else:
        print(f"Unknown format type: {format_type}")
        return False
    
    print(f"Successfully generated {format_type} document for song ID: {song_id}")
    return True

def generate_toc_only(sort_type):
    """Generate only the table of contents document"""
    songs = read_song_data()
    
    if not songs:
        print("No song data found. Exiting.")
        return False
    
    # Generate table of contents based on the sort type
    if sort_type == 'id':
        toc = generate_toc(songs, sort_by='id')
        generate_document('toc_only.html', 'toc_by_id', {
            'toc': toc,
            'title': 'Table of Contents - By ID',
            'sort_type': 'ID'
        })
    elif sort_type == 'name':
        toc = generate_toc(songs, sort_by='name')
        generate_document('toc_only.html', 'toc_by_name', {
            'toc': toc,
            'title': 'Table of Contents - By Name',
            'sort_type': 'Name'
        })
    else:
        print(f"Unknown sort type: {sort_type}")
        return False
    
    return True

def main():
    """Main function with command-line argument handling"""
    parser = argparse.ArgumentParser(description='Generate songbooks in different formats')
    
    # Define command-line arguments
    parser.add_argument('--format', choices=['lyrics', 'chords', 'presentation', 'all'], 
                        default='all', help='Specify the output format')
    parser.add_argument('--song-id', type=str, help='Generate a document for a specific song ID (from column A, e.g., H08)')
    parser.add_argument('--toc', choices=['id', 'name', 'both'], 
                        help='Generate only the table of contents sorted by ID or name')
    
    args = parser.parse_args()
    
    print("Starting Siron Song Book Generator")
    
    # Handle single song generation
    if args.song_id:
        if args.format == 'all':
            print("Please specify a single format (lyrics, chords, or presentation) when generating a single song.")
            return
        generate_single_song(args.song_id, args.format)
        return
    
    # Handle TOC-only generation
    if args.toc:
        if args.toc == 'both':
            generate_toc_only('id')
            generate_toc_only('name')
        else:
            generate_toc_only(args.toc)
        return
    
    # Read song data for full book generation
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
    
    # Generate the requested format(s)
    if args.format in ['lyrics', 'all']:
        generate_document('lyrics_book.html', 'songbook_lyrics', {
            'songs': songs_with_pages,
            'toc_by_id': toc_by_id,
            'toc_by_name': toc_by_name,
            'title': 'Song Book - Lyrics'
        })
    
    if args.format in ['chords', 'all']:
        generate_document('chords_book.html', 'songbook_chords', {
            'songs': songs_with_pages,
            'toc_by_id': toc_by_id,
            'toc_by_name': toc_by_name,
            'title': 'Song Book - Chords'
        })
    
    if args.format in ['presentation', 'all']:
        generate_document('presentation.html', 'songbook_presentation', {
            'songs': songs,
            'title': 'Song Presentation'
        })
    
    print("Document generation complete!")

if __name__ == "__main__":
    main()
