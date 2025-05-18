#!/usr/bin/env python3

import os
import json
import argparse
import subprocess
from jinja2 import Environment, FileSystemLoader

# Load configuration
CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'config.json')
with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
    CONFIG = json.load(f)

def load_songs_data(json_file_path):
    """Load all songs data from the JSON file."""
    with open(json_file_path, 'r', encoding='utf-8') as file:
        songs = json.load(file)
    return songs

def sort_songs(songs, sort_by="id"):
    """
    Sort songs either by ID or alphabetically by title, excluding songs with skip_toc set to True.
    
    Args:
        songs: List of song dictionaries
        sort_by: Either "id" or "title"
    
    Returns:
        Sorted list of song dictionaries
    """
    # Filter out songs with skip_toc set to True
    filtered_songs = [song for song in songs if not song.get('skip_toc', False)]
    
    if sort_by == "id":
        # Sort by the new 'inner_id' for consistent numerical ordering
        return sorted(filtered_songs, key=lambda x: int(x['inner_id']))
    elif sort_by == "title":
        hungarian_alphabet = "aábcdeéfghiíjklmnoóöőpqrstuúüűvwxyz"
        alphabet_order = {char: index for index, char in enumerate(hungarian_alphabet)}
        
        def hungarian_sort_key(title):
            return [alphabet_order.get(char, len(hungarian_alphabet)) for char in title.casefold()]
        
        return sorted(filtered_songs, key=lambda x: hungarian_sort_key(x['title']))
    else:
        raise ValueError(f"Invalid sort_by parameter: {sort_by}")

def render_toc_template(template_path, songs_data, sort_order):
    """Render a ToC template with the provided songs data and sort order."""
    page_data = {}
    template_dir = os.path.dirname(template_path)
    template_file = os.path.basename(template_path)
    # Corrected static path to be relative to the templates_dir from config
    static_path_abs = os.path.abspath(os.path.join(CONFIG['paths']['templates_dir'], CONFIG['paths']['static_dir_name']))
    page_data['static_path'] = 'file:///' + static_path_abs.replace(os.sep, '/')
    
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_file)

    return template.render(songs=songs_data, page=page_data, sort_order=sort_order) # Pass sort_order to template

def html_to_pdf(html_content, output_path):
    """Convert HTML content to PDF using wkhtmltopdf."""
    # Create temporary HTML file
    temp_html = os.path.join(CONFIG['paths']['temp_dir'], CONFIG['file_names']['temp_html_toc'])
    with open(temp_html, 'w', encoding='utf-8') as file:
        file.write(html_content)
    
    # A4 portrait settings for ToC from config
    params = CONFIG['page_parameters']['a4_toc']
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
        print(f"Generated ToC PDF: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error generating ToC PDF: {e}")
    finally:
        if os.path.exists(temp_html):
            os.remove(temp_html)

def generate_toc(version, toc_version, templates_dir, output_dir, json_file):
    """
    Generate a PDF Table of Contents for the specified songbook version.
    
    Args:
        version: Songbook version ("singer" or "musician")
        toc_version: ToC template version ("1" for ordered by ID, "2" for alphabetical)
        templates_dir: Directory containing template files
        output_dir: Directory to save output files
        json_file: Path to the JSON file containing song data
    """
    # Projection version doesn't have a TOC
    if version == "projection":
        print("Projection version does not include a Table of Contents.")
        return None
    
    # Load songs data
    songs_data = load_songs_data(json_file)
    
    # Sort songs based on TOC version
    sort_by = "id" if toc_version == "1" else "title"
    sorted_songs = sort_songs(songs_data, sort_by)
    
    # Get the template path from config
    template_filename = CONFIG['templates']['toc_template']
    template_path = os.path.join(templates_dir, template_filename)
    
    # Render HTML, passing the sort_by value as sort_order for the template
    html_content = render_toc_template(template_path, sorted_songs, sort_by)
    
    # Generate output file path
    output_subdir_template = CONFIG['output_formats']['songbook_subdir_template']
    output_subdir = output_subdir_template.format(version=version)
    os.makedirs(os.path.join(output_dir, output_subdir), exist_ok=True)
    if toc_version == "1":
        output_filename = CONFIG['file_names']['toc_pdf_ordered']
    elif toc_version == "2":
        output_filename = CONFIG['file_names']['toc_pdf_alphabetical']
    else:
        raise ValueError(f"Invalid ToC version: {toc_version}")
    output_path = os.path.join(output_dir, output_subdir, output_filename)
    
    # Convert HTML to PDF
    html_to_pdf(html_content, output_path)
    
    return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a Table of Contents for the songbook.")
    parser.add_argument("--version", choices=["singer", "musician", "projection"], 
                        required=True, help="Songbook version to generate")
    parser.add_argument("--toc-version", choices=["1", "2"], required=True,
                        help="ToC version: 1 for ordered by ID, 2 for alphabetical by title")
    parser.add_argument("--templates-dir", default=CONFIG['paths']['templates_dir'], 
                        help="Directory containing template files")
    parser.add_argument("--output-dir", default=CONFIG['paths']['output_dir'], 
                        help="Directory to save output files")
    parser.add_argument("--json-file", default=os.path.join(CONFIG['paths']['data_dir'], CONFIG['paths']['songs_json_filename']), 
                        help="Path to the JSON file containing song data")
    
    args = parser.parse_args()
    
    generate_toc(
        args.version, 
        args.toc_version, 
        args.templates_dir, 
        args.output_dir, 
        args.json_file
    )
