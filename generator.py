import json
import os
from datetime import datetime
from flask import Flask, render_template, url_for
import re

# Load songs data from JSON file
def load_songs_data():
    with open('data/songs.json', 'r', encoding='utf-8') as file:
        songs_data = json.load(file)
    return songs_data

# Process chord arrays into lyrics and chords
def process_chord_arrays(songs_data):
    processed_songs = []
    
    for index, song in enumerate(songs_data):
        song_id = index + 1
        chords_array = song.get("chords_array", "")
        
        if chords_array:
            # Split by the special separator '¤¤¤'
            parts = chords_array.split("¤¤¤")
            
            # Process the parts to extract lyrics and chords
            lyrics = []
            for part in parts:
                # Remove leading/trailing whitespace
                part = part.strip()
                if part:
                    lyrics.append(part)
            
            # Join all lyrics with newlines
            full_lyrics = "\n".join(lyrics)
            
            # For display in templates
            formatted_lyrics = full_lyrics.replace("\n", "<br>")
        else:
            full_lyrics = ""
            formatted_lyrics = ""
        
        # Check if the song needs to be split across pages
        needs_split = len(full_lyrics.split('\n')) > 30  # Example threshold
        
        if needs_split:
            lines = full_lyrics.split('\n')
            middle_point = len(lines) // 2
            first_page = '\n'.join(lines[:middle_point])
            second_page = '\n'.join(lines[middle_point:])
        else:
            first_page = full_lyrics
            second_page = ""
        
        # Create a song object with all needed properties
        song_obj = {
            "id": song_id,
            "name": f"Song {song_id}",
            "lyrics": full_lyrics,
            "formatted_lyrics": formatted_lyrics,
            "needs_split": needs_split,
            "first_page_content": first_page,
            "second_page_content": second_page,
            "key": "C"  # Default key, could be extracted from chords_array if needed
        }
        
        processed_songs.append(song_obj)
    
    return processed_songs

# Generate individual song files (lyrics and chords)
def generate_song_files(songs):
    app = Flask(__name__)
    app.jinja_env.globals.update(now=datetime.now)
    
    # Ensure output directories exist
    os.makedirs('output', exist_ok=True)
    os.makedirs('output/lyrics', exist_ok=True)
    os.makedirs('output/chords', exist_ok=True)
    
    with app.app_context():
        for song in songs:
            if song["lyrics"]:
                # Generate lyrics page
                lyrics_html = render_template('single_song_lyrics.html', song=song)
                with open(f'output/lyrics/song_{song["id"]}.html', 'w', encoding='utf-8') as file:
                    file.write(lyrics_html)
                
                # Generate chords page
                chords_html = render_template('single_song_chords.html', song=song)
                with open(f'output/chords/song_{song["id"]}.html', 'w', encoding='utf-8') as file:
                    file.write(chords_html)

# Generate presentation file
def generate_presentation(songs):
    app = Flask(__name__)
    app.jinja_env.globals.update(now=datetime.now)
    
    # Filter out songs with no lyrics
    songs_with_lyrics = [song for song in songs if song["lyrics"]]
    
    with app.app_context():
        presentation_html = render_template('presentation.html', songs=songs_with_lyrics, title="Song Presentation")
        
        with open('output/presentation.html', 'w', encoding='utf-8') as file:
            file.write(presentation_html)

def main():
    # Load songs data
    songs_data = load_songs_data()
    
    # Process songs data
    processed_songs = process_chord_arrays(songs_data)
    
    # Generate individual song files
    generate_song_files(processed_songs)
    
    # Generate presentation file
    generate_presentation(processed_songs)
    
    print(f"Generated files for {len(processed_songs)} songs")

if __name__ == "__main__":
    main()
