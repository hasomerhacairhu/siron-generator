#!/usr/bin/env python3

import os
import json
import argparse
import subprocess
from jinja2 import Environment, FileSystemLoader

def load_songs_data(json_file_path):
    """Load all songs data from the JSON file."""
    with open(json_file_path, 'r', encoding='utf-8') as file:
        songs = json.load(file)
    return songs

def sort_songs(songs, sort_by="id"):
    """
    Sort songs either by ID or alphabetically by title.
    
    Args:
        songs: List of song dictionaries
        sort_by: Either "id" or "title"
    
    Returns:
        Sorted list of song dictionaries
    """
    if sort_by == "id":
        return sorted(songs, key=lambda x: int(x['id']) if isinstance(x['id'], (int, str)) else x['id'])
    elif sort_by == "title":
        return sorted(songs, key=lambda x: x['title'].lower())
    else:
        raise ValueError(f"Invalid sort_by parameter: {sort_by}")

def render_toc_template(template_path, songs_data):
    """Render a ToC template with the provided songs data."""
    template_dir = os.path.dirname(template_path)
    template_file = os.path.basename(template_path)
    
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_file)
    
    return template.render(songs=songs_data)

def html_to_pdf(html_content, output_path):
    """Convert HTML content to PDF using wkhtmltopdf."""
    # Create temporary HTML file
    temp_html = os.path.join(os.path.dirname(output_path), "temp_toc.html")
    with open(temp_html, 'w', encoding='utf-8') as file:
        file.write(html_content)
    
    # A4 portrait settings for ToC
    page_options = [
        "--page-size", "A4",
        "--orientation", "Portrait",
        "--margin-top", "20",
        "--margin-bottom", "20",
        "--margin-left", "20",
        "--margin-right", "20"
    ]

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Execute wkhtmltopdf command
    cmd = ["wkhtmltopdf"] + page_options + [temp_html, output_path]
    
    try:
        result = subprocess.run(cmd, check=True)
        print(f"Generated ToC PDF: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error generating ToC PDF: {e}")
    finally:
        # Clean up temporary HTML file
        if os.path.exists(temp_html):
            os.remove(temp_html)

def get_toc_template_path(templates_dir, toc_version):
    """Return the appropriate ToC template file path."""
    if toc_version == "1":
        return os.path.join(templates_dir, "toc_template_1.html")
    elif toc_version == "2":
        return os.path.join(templates_dir, "toc_template_2.html")
    else:
        raise ValueError(f"Invalid ToC version: {toc_version}")

def generate_toc(version, toc_version, templates_dir, output_dir, json_file):
    """
    Generate a PDF Table of Contents for the specified songbook version.
    
    Args:
        version: Songbook version ("singer" or "musician")
        toc_version: ToC template version ("1" for by ID, "2" for alphabetical)
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
    
    # Get the appropriate template
    template_path = get_toc_template_path(templates_dir, toc_version)
    
    # Render HTML
    html_content = render_toc_template(template_path, sorted_songs)
    
    # Generate output file path
    output_subdir = f"{version}s_songbook"
    os.makedirs(os.path.join(output_dir, output_subdir), exist_ok=True)
    output_filename = f"table_of_contents.pdf"
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
    parser.add_argument("--templates-dir", default="../templates", 
                        help="Directory containing template files")
    parser.add_argument("--output-dir", default="../output", 
                        help="Directory to save output files")
    parser.add_argument("--json-file", default="../data/songs.json", 
                        help="Path to the JSON file containing song data")
    
    args = parser.parse_args()
    
    generate_toc(
        args.version, 
        args.toc_version, 
        args.templates_dir, 
        args.output_dir, 
        args.json_file
    )
