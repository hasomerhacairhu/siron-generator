#!/usr/bin/env python3

import os
import json
import argparse
import subprocess
import base64
from io import BytesIO
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv
import qrcode

# Load environment variables from .env file
load_dotenv()

def load_song_data(json_file_path, song_id=None):
    """
    Load song data from a JSON file.
    If song_id is provided, return only that song.
    Otherwise, return all songs.
    """
    with open(json_file_path, 'r', encoding='utf-8') as file:
        songs = json.load(file)
    
    if song_id is not None:
        for song in songs:
            if str(song['id']) == str(song_id):
                return song
        raise ValueError(f"Song with ID {song_id} not found.")
    return songs

def generate_qr_code(url):
    """
    Generate a QR code for the given URL and return it as a base64 encoded string
    """
    if not url:
        return None
    
    print(f"Generating QR code for URL: {url}")
            
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save image to a bytes buffer
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    # Convert to base64 for embedding in HTML
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return f"data:image/png;base64,{img_str}"

def process_line_breaks(text):
    """
    Replace \n characters with HTML line breaks
    """
    if not text:
        return text
    return text.replace('\n', '<br>')

def render_template(template_path, song_data):
    """
    Render a Jinja2 template with the provided song data.
    """
    template_dir = os.path.dirname(template_path)
    template_file = os.path.basename(template_path)
    
    # Process line breaks in lyrics and chords
    if 'lyrics' in song_data:
        song_data['lyrics'] = process_line_breaks(song_data['lyrics'])
    if 'lyrics_with_chords' in song_data:
        song_data['lyrics_with_chords'] = process_line_breaks(song_data['lyrics_with_chords'])
    
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_file)
    
    # Add footer text for the template
    footer = {
        'left': "Hasomer Hacair Magyarország",
        'right': "Siron - Daloskönyv"
    }
    
    # Generate QR code if YouTube link exists
    qr_code_data = None
    if 'youtube' in song_data and song_data['youtube']:
        qr_code_data = generate_qr_code(song_data['youtube'])
    
    return template.render(song=song_data, footer=footer, qr_code_data=qr_code_data)

def html_to_pdf(html_content, output_path, version):
    """
    Convert HTML content to PDF using wkhtmltopdf.
    Adjust page size based on version.
    """
    # Create temporary HTML file
    temp_html = os.path.join(os.path.dirname(output_path), "temp.html")
    with open(temp_html, 'w', encoding='utf-8') as file:
        file.write(html_content)
    
    # Set page parameters based on version
    if version == "projection":
        # 16:9 aspect ratio
        page_options = [
            "--page-width", "1920px",
            "--page-height", "1080px",
            "--margin-top", "50px",
            "--margin-bottom", "50px",
            "--margin-left", "50px",
            "--margin-right", "50px"
        ]
    else:
        # A4 portrait
        page_options = [
            "--page-size", "A4",
            "--orientation", "Portrait",
            "--margin-top", "15",
            "--margin-bottom", "15",
            "--margin-left", "30",
            "--margin-right", "20"
        ]

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Execute wkhtmltopdf command
    wkhtmltopdf_path = os.getenv('WKHTMLTOPDF_PATH', os.path.join("C:\\Program Files\\wkhtmltopdf\\bin", "wkhtmltopdf.exe"))
    cmd = [wkhtmltopdf_path] + page_options + [temp_html, output_path]
    
    try:
        result = subprocess.run(cmd, check=True)
        print(f"Generated PDF: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error generating PDF: {e}")
    finally:
        # Clean up temporary HTML file
        if os.path.exists(temp_html):
            os.remove(temp_html)

def get_template_for_version(templates_dir, version):
    """
    Return the appropriate template file path based on the songbook version.
    """
    if version == "singer":
        return os.path.join(templates_dir, "singer_song_page_template.html")
    elif version == "musician":
        return os.path.join(templates_dir, "musician_song_page_template.html")
    elif version == "projection":
        return os.path.join(templates_dir, "projection_song_page_template.html")
    else:
        raise ValueError(f"Invalid version: {version}")

def generate_song_page(song_id, version, templates_dir, output_dir, json_file):
    """
    Generate a PDF page for the specified song and songbook version.
    """
    # Load song data
    song_data = load_song_data(json_file, song_id)
    
    # Get the appropriate template
    template_path = get_template_for_version(templates_dir, version)
    
    # Render HTML
    html_content = render_template(template_path, song_data)
    
    # Generate output file path
    output_subdir = f"{version}s_songbook"
    os.makedirs(os.path.join(output_dir, output_subdir), exist_ok=True)
    output_filename = f"song_{song_id}.pdf"
    output_path = os.path.join(output_dir, output_subdir, output_filename)
    
    # Convert HTML to PDF
    html_to_pdf(html_content, output_path, version)
    
    return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a songbook page for a specific song.")
    parser.add_argument("--song-id", required=True, help="ID of the song to generate a page for")
    parser.add_argument("--version", choices=["singer", "musician", "projection"], 
                        required=True, help="Songbook version to generate")
    parser.add_argument("--templates-dir", default="../templates", 
                        help="Directory containing template files")
    parser.add_argument("--output-dir", default="../output", 
                        help="Directory to save output files")
    parser.add_argument("--json-file", default="../data/songs.json", 
                        help="Path to the JSON file containing song data")
    
    args = parser.parse_args()
    
    generate_song_page(
        args.song_id, 
        args.version, 
        args.templates_dir, 
        args.output_dir, 
        args.json_file
    )
