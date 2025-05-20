import json
import os
import argparse

# --- YouTube search logic using youtube-search-python ---
# Ensure 'youtube-search-python' is installed (pip install youtube-search-python)

from youtubesearchpython import VideosSearch

def actual_youtube_search(song_title, song_author):
    """
    Searches YouTube for the song and returns the best matching URL or "-".
    Prioritizes official music videos, then most viewed audio versions.
    Excludes concert/live recordings.
    """
    print(f"  Searching YouTube for: '{song_author} - {song_title}'")

    # Attempt to find official music video
    query_official_video = f"{song_author} {song_title} official music video"
    print(f"    Attempt 1: Searching for official music video with query: '{query_official_video}'")
    videos_search_official = VideosSearch(query_official_video, limit=5)
    results_official = videos_search_official.result().get('result', [])

    for video in results_official:
        title_lower = video.get('title', '').lower()
        link = video.get('link')
        if "official video" in title_lower or "official music video" in title_lower:
            if not ("concert" in title_lower or "live" in title_lower):
                print(f"      Found official music video: '{video.get('title')}' - {link}")
                return link
            else:
                print(f"      Skipping official video (concert/live): '{video.get('title')}'")
    print("    Attempt 1: No direct official music video found (non-concert).")

    # If no official video, search for audio / most viewed (excluding concerts)
    query_audio = f"{song_author} {song_title} audio"
    print(f"    Attempt 2: Searching for audio versions with query: '{query_audio}'")
    videos_search_audio = VideosSearch(query_audio, limit=10)
    results_audio = videos_search_audio.result().get('result', [])

    best_audio_url = None
    max_views = -1
    best_audio_title = ""

    if results_audio:
        print(f"      Found {len(results_audio)} potential audio tracks. Analyzing...")
        for video in results_audio:
            title_lower = video.get('title', '').lower()
            link = video.get('link')
            if "concert" in title_lower or "live" in title_lower:
                print(f"        Skipping audio (concert/live): '{video.get('title')}'")
                continue

            is_likely_audio = "audio" in title_lower or \
                              "lyric" in title_lower or \
                              song_title.lower() in title_lower

            if is_likely_audio:
                try:
                    view_count_str = video.get('viewCount', {}).get('text', '0').split(' ')[0].replace(',', '')
                    views = int(view_count_str) if view_count_str.isdigit() else 0
                    print(f"        Considering audio: '{video.get('title')}' (Views: {views})")
                    if views > max_views:
                        max_views = views
                        best_audio_url = link
                        best_audio_title = video.get('title')
                except Exception:
                    print(f"        Considering audio (view count unavailable): '{video.get('title')}'")
                    if max_views == -1: # If no other viewed video found yet, take this one
                        best_audio_url = link
                        best_audio_title = video.get('title')
                        max_views = 0 # Mark as found, but with 0 views for comparison
            else:
                print(f"        Skipping (not marked as audio/lyric): '{video.get('title')}'")
    else:
        print("      No results for audio-specific search.")

    if best_audio_url:
        print(f"    Attempt 2: Found best audio version: '{best_audio_title}' (Views: {max_views if max_views > 0 else 'N/A'}) - {best_audio_url}")
        return best_audio_url
    print("    Attempt 2: No suitable audio version found.")

    # Fallback: if no specifically "audio" marked video with high views, take the first non-concert result from a general search
    query_general = f"{song_author} {song_title}"
    print(f"    Attempt 3: Performing general search with query: '{query_general}'")
    videos_search_general = VideosSearch(query_general, limit=3) # Broader fallback
    results_general = videos_search_general.result().get('result', [])

    if results_general:
        print(f"      Found {len(results_general)} general results. Checking first non-concert...")
        for video in results_general:
            title_lower = video.get('title', '').lower()
            link = video.get('link')
            if not ("concert" in title_lower or "live" in title_lower):
                print(f"    Attempt 3: Found general fallback: '{video.get('title')}' - {link}")
                return link
            else:
                print(f"      Skipping general result (concert/live): '{video.get('title')}'")
    print("    Attempt 3: No suitable general fallback found.")

    print(f"  No suitable YouTube link found for '{song_author} - {song_title}'. Returning '-'.")
    return "-"

def get_youtube_link_for_song(song_details):
    """
    Gets the YouTube link for a song.
    Uses existing link if available, otherwise calls the actual_youtube_search function.
    """
    if song_details.get("youtube_link"):
        print(f"  Found existing YouTube link: {song_details['youtube_link']}")
        return song_details["youtube_link"]

    song_title = song_details.get("title")
    song_author = song_details.get("author")

    if not song_title or not song_author:
        print(f"  Warning: Song missing title or author. Title: '{song_title}', Author: '{song_author}'. Cannot search.")
        return "-"

    # Call the actual search function
    return actual_youtube_search(song_title, song_author)

def main():
    # Load configuration to get default paths
    config = {}
    try:
        config_file_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
        with open(config_file_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Warning: Configuration file not found at {config_file_path}. Using default paths.")
    except json.JSONDecodeError:
        print(f"Warning: Could not decode JSON from {config_file_path}. Using default paths.")

    # Determine paths
    script_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(script_dir, '..'))

    default_data_dir = config.get('paths', {}).get('data_dir', os.path.join(project_root, 'data'))
    default_songs_filename = config.get('paths', {}).get('songs_json_filename', 'songs.json')
    default_songs_json_path = os.path.join(default_data_dir, default_songs_filename)

    default_output_dir = config.get('paths', {}).get('output_dir', os.path.join(project_root, 'output'))
    default_output_txt_filename = 'youtube_links.txt'
    default_output_txt_path = os.path.join(default_output_dir, default_output_txt_filename)

    parser = argparse.ArgumentParser(description="Find YouTube links for songs in songs.json and export to a TXT file.")
    parser.add_argument(
        "--songs_json",
        default=default_songs_json_path,
        help=f"Path to the input songs.json file (default: {default_songs_json_path})"
    )
    parser.add_argument(
        "--output_txt",
        default=default_output_txt_path,
        help=f"Path to the output TXT file (default: {default_output_txt_path})"
    )
    args = parser.parse_args()

    songs_json_path = os.path.abspath(args.songs_json)
    output_txt_path = os.path.abspath(args.output_txt)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_txt_path), exist_ok=True)

    try:
        with open(songs_json_path, 'r', encoding='utf-8') as f:
            songs_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Songs JSON file not found at {songs_json_path}")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {songs_json_path}")
        return

    if not isinstance(songs_data, list):
        print(f"Error: Expected a list of songs in {songs_json_path}, but got {type(songs_data)}")
        return

    print(f"Loaded {len(songs_data)} songs from {songs_json_path}")

    youtube_links_output = []
    for i, song in enumerate(songs_data):
        print(f"Processing song {i+1}/{len(songs_data)}: '{song.get('title', 'N/A')}' by '{song.get('author', 'N/A')}'")
        if not isinstance(song, dict):
            print(f"  Warning: Skipping non-dictionary item in songs list: {song}")
            youtube_links_output.append("-") # Maintain line count
            continue
        link = get_youtube_link_for_song(song)
        youtube_links_output.append(link)
        print(f"  Result for '{song.get('title', 'N/A')}': {link}\n") # Added newline for readability

    try:
        with open(output_txt_path, 'w', encoding='utf-8') as f:
            for link in youtube_links_output:
                f.write(link + "\n")
        print(f"Successfully wrote {len(youtube_links_output)} YouTube links/placeholders to {output_txt_path}")
    except IOError as e:
        print(f"Error writing to output file {output_txt_path}: {e}")

if __name__ == "__main__":
    main()
