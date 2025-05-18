#!/usr/bin/env python3

import os
import json
import subprocess
import argparse
import sys

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

def run_script(script_name, args_list):
    """Helper function to run a Python script using subprocess."""
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    command = [sys.executable, script_path] + args_list
    print(f"Running command: {' '.join(command)}")
    try:
        # Using encoding for stdout/stderr
        result = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
        print(f"Successfully ran {script_name} with args: {' '.join(args_list)}")
        if result.stdout:
            print(f"Output:\n{result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name} with args: {' '.join(args_list)}")
        print(f"Return code: {e.returncode}")
        if e.stdout:
            print(f"Stdout:\n{e.stdout}")
        if e.stderr:
            print(f"Stderr:\n{e.stderr}")
        return False
    except FileNotFoundError:
        print(f"Error: Script {script_path} not found.")
        return False


def generate_full_songbook(version, songs_file_path_arg, templates_dir_arg, output_dir_arg):
    """
    Generates all pages for a specific songbook version, including two types of TOCs and all song pages.
    """
    print(f"Starting generation for version: {version}")

    # Common arguments for sub-scripts
    # These will be passed if the user provides them to this script,
    # otherwise, the sub-scripts will use their own defaults from config.json.
    common_args = []
    if templates_dir_arg:
        common_args.extend(["--templates-dir", templates_dir_arg])
    if output_dir_arg:
        common_args.extend(["--output-dir", output_dir_arg])
    if songs_file_path_arg:
        common_args.extend(["--json-file", songs_file_path_arg])

    # 1. Generate Table of Contents (if not projection version)
    if version != "projection":
        print("\nGenerating Table of Contents (by ID)...")
        toc_args_id = ["--version", version, "--toc-version", "1"] + common_args
        if not run_script("generate_toc.py", toc_args_id):
            print("Failed to generate TOC by ID. Aborting.")
            return

        print("\nGenerating Table of Contents (by Title)...")
        toc_args_title = ["--version", version, "--toc-version", "2"] + common_args
        if not run_script("generate_toc.py", toc_args_title):
            print("Failed to generate TOC by Title. Aborting.")
            return
    else:
        print("\nSkipping TOC generation for projection version.")

    # 2. Load songs data to iterate for page generation
    # Determine the actual songs file path to use (argument or config default)
    actual_songs_file_path = songs_file_path_arg or os.path.join(CONFIG['paths']['data_dir'], CONFIG['paths']['songs_json_filename'])
    
    try:
        with open(actual_songs_file_path, 'r', encoding='utf-8') as f:
            songs = json.load(f)
    except FileNotFoundError:
        print(f"Error: Songs JSON file not found at {actual_songs_file_path}. Aborting song page generation.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {actual_songs_file_path}. Aborting song page generation.")
        return

    if not songs:
        print("No songs found in the JSON file. Skipping song page generation.")
        return

    print(f"\nFound {len(songs)} songs. Generating individual song pages...")
    # 3. Generate all song pages
    songs_processed_count = 0
    songs_failed_count = 0
    for i, song in enumerate(songs):
        song_inner_id = song.get("inner_id")
        if not song_inner_id:
            print(f"Warning: Song at index {i} (Title: {song.get('title', 'N/A')}) is missing 'inner_id'. Skipping.")
            songs_failed_count += 1
            continue

        print(f"\nGenerating page for song with inner_id: {song_inner_id} (Title: {song.get('title', 'N/A')})...")
        song_page_args = ["--song-id", str(song_inner_id), "--version", version] + common_args
        if run_script("generate_songbook_page.py", song_page_args):
            songs_processed_count +=1
        else:
            print(f"Failed to generate page for song inner_id {song_inner_id}. Continuing with next song...")
            songs_failed_count +=1
            
    print(f"\nSong page generation summary: {songs_processed_count} succeeded, {songs_failed_count} failed/skipped.")
    print(f"Finished generation for version: {version}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate all songbook pages and TOCs for a specific version.")
    parser.add_argument("--version", choices=["singer", "musician", "projection"],
                        required=True, help="Songbook version to generate (singer, musician, projection).")
    
    parser.add_argument("--songs-json",
                        help="Path to the JSON file containing song data. Overrides config.json setting for sub-scripts.")
    parser.add_argument("--templates-dir",
                        help="Directory containing template files. Overrides config.json setting for sub-scripts.")
    parser.add_argument("--output-dir",
                        help="Directory to save output files. Overrides config.json setting for sub-scripts.")

    args = parser.parse_args()

    # Resolve paths to be absolute if provided by user, to ensure consistency for subprocess calls.
    # If not provided, they remain None, and sub-scripts will use their defaults from their loaded config.
    abs_songs_json = os.path.abspath(args.songs_json) if args.songs_json else None
    abs_templates_dir = os.path.abspath(args.templates_dir) if args.templates_dir else None
    abs_output_dir = os.path.abspath(args.output_dir) if args.output_dir else None

    generate_full_songbook(args.version, abs_songs_json, abs_templates_dir, abs_output_dir)
