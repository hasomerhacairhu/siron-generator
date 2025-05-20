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
import re

# Load configuration
CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'config.json')
with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
    CONFIG = json.load(f)

# Load environment variables from .env file
load_dotenv()

def wrap_chords_in_lyrics(text_with_chords):
    """
    Finds words in the input text that are guitar chords (from config)
    and wraps them in a <span class="chord">CHORD</span>.
    """
    if not text_with_chords:
        return ""
    
    chords = CONFIG.get('guitar_chords', [])
    if not chords:
        return text_with_chords
        
    # Sort chords by length in descending order to match longer chords first (e.g., "Am7" before "A")
    # Also, escape special characters in chords for regex.
    sorted_chords_escaped = sorted(map(re.escape, chords), key=len, reverse=True)
    
    # Pattern to match standalone chords.
    # (?<!\S) asserts position is not preceded by a non-whitespace character.
    # (?!\S) asserts position is not followed by a non-whitespace character.
    # This effectively matches whole words separated by whitespace.
    # The inner parentheses create a capturing group for the chord itself.
    chord_pattern_str = r'(?<!\S)(' + '|'.join(sorted_chords_escaped) + r')(?!\S)'
    
    def replace_chord(match):
        return f'<span class="chord">{match.group(1)}</span>' # match.group(1) is the captured chord
        
    return re.sub(chord_pattern_str, replace_chord, text_with_chords)

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
            if str(song['inner_id']) == str(song_id): # Changed 'id' to 'inner_id'
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

def break_lyrics_into_columns(lyrics_html, num_columns):
    """
    Breaks lyrics into the specified number of columns.
    Currently supports 2 columns, splitting at a <br><br> tag
    that is closest to the middle of the content.

    Returns:
        list: A list containing two strings: [column1_html, column2_html].
              If no split is performed, column1_html is the original lyrics_html
              and column2_html is an empty string.
    """
    if not lyrics_html or num_columns <= 1:
        return [lyrics_html, ""]

    if num_columns == 2:
        sections = lyrics_html.split('<br><br>')
        
        if len(sections) <= 1:
            # No <br><br> found, or only one section, so cannot split by this rule.
            return [lyrics_html, ""]

        total_char_count = len(lyrics_html)
        ideal_col1_char_count = total_char_count / 2.0
        
        best_split_point_index = -1
        min_abs_diff_from_middle = float('inf')

        # Iterate through all possible split points
        for i in range(len(sections) - 1):
            col1_candidate_sections = sections[:i+1]
            col1_candidate_content = "<br><br>".join(col1_candidate_sections)
            current_col1_len = len(col1_candidate_content)
            
            abs_diff = abs(current_col1_len - ideal_col1_char_count)
            
            if abs_diff < min_abs_diff_from_middle:
                min_abs_diff_from_middle = abs_diff
                best_split_point_index = i

        if best_split_point_index != -1:
            col1_final_sections = sections[:best_split_point_index+1]
            col2_final_sections = sections[best_split_point_index+1:]
            
            col1_content = "<br><br>".join(col1_final_sections)
            col2_content = "<br><br>".join(col2_final_sections)
            
            return [col1_content, col2_content]
        else:
            # This case implies no suitable split point was found,
            # though with len(sections) > 1, a best_split_point_index should be found.
            # Safely return original content in first column.
            return [lyrics_html, ""]
    else:
        # For num_columns other than 2, return original lyrics in first column.
        return [lyrics_html, ""]

def render_template(template_path, song_data):
    """
    Render a Jinja2 template with the provided song data.
    """
    song_data['columns'] = 1
    template_dir = os.path.dirname(template_path)
    template_file = os.path.basename(template_path)
    # Construct static path using config
    static_path_abs = os.path.abspath(os.path.join(CONFIG['paths']['templates_dir'], CONFIG['paths']['static_dir_name']))
    song_data['static_path'] = 'file:///' + static_path_abs.replace(os.sep, '/')


    if song_data['version'] == "musician":
        song_data['lyrics'] = process_line_breaks(wrap_chords_in_lyrics(song_data['lyrics_with_chords']))
    else: # For other versions like projection, handle lyrics if necessary
        song_data['lyrics'] = process_line_breaks(song_data['lyrics'])

    # Determine the CSS class for lyrics based on length thresholds from config
    lyrics_length = len(song_data['lyrics'].split('<br>'))
    if lyrics_length >= CONFIG['lyrics']['column_break_threshold']:
        song_data['columns'] = 2

    if song_data['columns'] > 1:
        song_data['lyrics'] = break_lyrics_into_columns(song_data['lyrics'], song_data['columns'])

    if lyrics_length <= CONFIG['lyrics']['lines_thresholds']['large']:
        song_data['lyrics_css'] = 'lyrics-l'
    elif lyrics_length >= CONFIG['lyrics']['lines_thresholds']['small']:
        song_data['lyrics_css'] = 'lyrics-s'
    else:
        song_data['lyrics_css'] = 'lyrics-m'
   
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_file)
    
    # Generate QR code if YouTube link exists
    if 'youtube' in song_data and song_data['version'] == "singer":
        song_data['qr_code_data'] = generate_qr_code(song_data['youtube'])
    
    return template.render(song=song_data)

def html_to_pdf(html_content, output_path, version):
    """
    Convert HTML content to PDF using wkhtmltopdf.
    Adjust page size based on version.
    """
    # Create temporary HTML file
    temp_html = os.path.join(CONFIG['paths']['temp_dir'], CONFIG['file_names']['temp_html_page'])
    with open(temp_html, 'w', encoding='utf-8') as file:
        file.write(html_content)
    
    # Set page parameters based on version from config
    if version == "projection":
        params = CONFIG['page_parameters']['projection']
        page_options = [
            "--page-width", params['page_width'],
            "--page-height", params['page_height'],
            "--margin-top", params['margin_top'],
            "--margin-bottom", params['margin_bottom'],
            "--margin-left", params['margin_left'],
            "--margin-right", params['margin_right'],
            "--zoom", params['zoom']
        ]
    else: # singer or musician (A4)
        params = CONFIG['page_parameters']['a4_song']
        page_options = [
            "--page-size", params['page_size'],
            "--orientation", params['orientation'],
            "--margin-top", params['margin_top'],
            "--margin-bottom", params['margin_bottom'],
            "--margin-left", params['margin_left'],
            "--margin-right", params['margin_right']
        ]
    
    # Add common extra options from config
    page_options += params.get('extra_options', [])
        
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Execute wkhtmltopdf command
    wkhtmltopdf_path = os.getenv('WKHTMLTOPDF_PATH', CONFIG['paths']['wkhtmltopdf'])
    cmd = [wkhtmltopdf_path] + page_options + [temp_html, output_path]
    
    try:
        result = subprocess.run(cmd, check=True)
        print(f"Successfully generated PDF: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error generating PDF: {e}")

def get_template_for_version(templates_dir, version):
    """
    Return the appropriate template file path based on the songbook version.
    """
    if version == "singer":
        return os.path.join(templates_dir, CONFIG['templates']['singer_song_page'])
    elif version == "musician":
        return os.path.join(templates_dir, CONFIG['templates']['musician_song_page'])
    elif version == "projection":
        return os.path.join(templates_dir, CONFIG['templates']['projection_song_page'])
    else:
        raise ValueError(f"Invalid version: {version}")

def generate_song_page(song_id, version, templates_dir, output_dir, json_file):
    """
    Generate a PDF page for the specified song and songbook version.
    """
    # Load song data
    song_data = load_song_data(json_file, song_id)
    
    # Add version to song_data so it can be passed to render_template
    song_data['version'] = version

    # Get the appropriate template
    template_path = get_template_for_version(templates_dir, version)
    
    # Render HTML
    html_content = render_template(template_path, song_data)
    
    # Generate output file path
    output_subdir_template = CONFIG['output_formats']['songbook_subdir_template']
    output_subdir = output_subdir_template.format(version=version)
    os.makedirs(os.path.join(output_dir, output_subdir), exist_ok=True)
    output_filename = f"{CONFIG['file_names']['song_page_prefix']}{song_data['inner_id']}{CONFIG['file_names']['song_page_suffix']}"
    output_path = os.path.join(output_dir, output_subdir, output_filename)
    
    # Convert HTML to PDF
    html_to_pdf(html_content, output_path, version)
    
    return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a songbook page for a specific song.")
    parser.add_argument("--song-id", required=True, help="Inner ID of the song to generate a page for")
    parser.add_argument("--version", choices=["singer", "musician", "projection"], 
                        required=True, help="Songbook version to generate")
    parser.add_argument("--templates-dir", default=CONFIG['paths']['templates_dir'], 
                        help="Directory containing template files")
    parser.add_argument("--output-dir", default=CONFIG['paths']['output_dir'], 
                        help="Directory to save output files")
    parser.add_argument("--json-file", default=os.path.join(CONFIG['paths']['data_dir'], CONFIG['paths']['songs_json_filename']), 
                        help="Path to the JSON file containing song data")
    
    args = parser.parse_args()
    
    generate_song_page(
        args.song_id, 
        args.version, 
        args.templates_dir, 
        args.output_dir, 
        args.json_file
    )
