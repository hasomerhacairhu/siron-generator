#!/usr/bin/env python3

import os
import json
import argparse
import sys
import re
from PyPDF2 import PdfMerger

# Load configuration
try:
    CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
        CONFIG = json.load(f)
except FileNotFoundError:
    print(f"Error: Configuration file not found at {CONFIG_FILE_PATH}")
    sys.exit(1)
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from {CONFIG_FILE_PATH}")
    sys.exit(1)

def build_final_songbook(version):
    """Merges existing TOCs and all song PDFs for a given version into a single PDF."""
    print(f"Starting to build final songbook for version: {version} from existing files.")

    main_output_dir = CONFIG['paths']['output_dir']
    version_songbook_subdir_template = CONFIG['output_formats']['songbook_subdir_template']
    version_songbook_files_dir = os.path.join(main_output_dir, version_songbook_subdir_template.format(version=version))

    if not os.path.isdir(version_songbook_files_dir):
        print(f"Error: Version specific directory {version_songbook_files_dir} not found. Cannot proceed.")
        sys.exit(1)

    merger = PdfMerger()
    pdfs_to_merge = []

    if version != "projection":
        print("\nLooking for Table of Contents files...")
        
        # Look for TOC by ID
        toc_by_id_filename = CONFIG['file_names']['toc_pdf_ordered']
        toc_by_id_path = os.path.join(version_songbook_files_dir, toc_by_id_filename)
        if os.path.exists(toc_by_id_path):
            pdfs_to_merge.append(toc_by_id_path)
            print(f"Found {toc_by_id_filename}. Added to merge list.")
        else:
            print(f"Warning: {toc_by_id_filename} not found in {version_songbook_files_dir}. It will not be included.")

        # Look for TOC by Title
        toc_by_title_filename = CONFIG['file_names']['toc_pdf_alphabetical']
        toc_by_title_path = os.path.join(version_songbook_files_dir, toc_by_title_filename)
        if os.path.exists(toc_by_title_path):
            pdfs_to_merge.append(toc_by_title_path)
            print(f"Found {toc_by_title_filename}. Added to merge list.")
        else:
            print(f"Warning: {toc_by_title_filename} not found in {version_songbook_files_dir}. It will not be included.")
    else:
        print("\nSkipping TOC inclusion for projection version.")

    print("\nProcessing song pages...")
    song_files_in_dir = []
    for f_name in os.listdir(version_songbook_files_dir):
        if re.match(r"song_\d+\.pdf", f_name, re.IGNORECASE):
            song_files_in_dir.append(f_name)
    
    if not song_files_in_dir:
        print(f"No song_*.pdf files found in {version_songbook_files_dir}.")
    else:
        song_files_in_dir.sort(key=lambda f: int(re.search(r"song_(\d+)\.pdf", f, re.IGNORECASE).group(1)))
        print(f"Found and sorted {len(song_files_in_dir)} song pages.")
        for song_file in song_files_in_dir:
            pdfs_to_merge.append(os.path.join(version_songbook_files_dir, song_file))
    
    if not pdfs_to_merge:
        print("No PDF files to merge. Exiting.")
        return

    print(f"\nMerging {len(pdfs_to_merge)} PDF files...")
    for pdf_path in pdfs_to_merge:
        if os.path.exists(pdf_path):
            print(f"Adding: {pdf_path}")
            merger.append(pdf_path)
        else:
            print(f"Warning: File {pdf_path} not found, skipping.")

    final_output_filename = f"{version}_SironSongbook_Merged.pdf"
    final_output_path = os.path.join(main_output_dir, final_output_filename)

    try:
        merger.write(final_output_path)
        print(f"\nSuccessfully merged PDF saved as: {final_output_path}")
    except Exception as e:
        print(f"Error writing final PDF: {e}")
    finally:
        merger.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build a complete songbook PDF by merging TOCs and song pages for a specific version.")
    parser.add_argument("--version", choices=["singer", "musician", "projection"],
                        required=True, help="Songbook version to build (singer, musician, projection).")
    
    args = parser.parse_args()
    build_final_songbook(args.version)
