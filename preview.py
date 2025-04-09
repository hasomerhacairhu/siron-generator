from flask import Flask, render_template, url_for
from datetime import datetime
import json

app = Flask(__name__)
app.jinja_env.globals.update(now=datetime.now)

# Load songs data from JSON file
def load_songs_data():
    with open('data/songs.json', 'r', encoding='utf-8') as file:
        songs_data = json.load(file)
    return songs_data

# Process chord arrays into lyrics and chords (similar to generator.py)
def process_chord_arrays(songs_data):
    processed_songs = []
    
    for index, song in enumerate(songs_data):
        song_id = index + 1
        chords_array = song.get("chords_array", "")
        
        if chords_array:
            parts = chords_array.split("¤¤¤")
            lyrics = [part.strip() for part in parts if part.strip()]
            full_lyrics = "\n".join(lyrics)
            formatted_lyrics = full_lyrics.replace("\n", "<br>")
        else:
            full_lyrics = ""
            formatted_lyrics = ""
        
        needs_split = len(full_lyrics.split('\n')) > 30
        
        if needs_split:
            lines = full_lyrics.split('\n')
            middle_point = len(lines) // 2
            first_page = '\n'.join(lines[:middle_point])
            second_page = '\n'.join(lines[middle_point:])
        else:
            first_page = full_lyrics
            second_page = ""
        
        song_obj = {
            "id": song_id,
            "name": f"Song {song_id}",
            "lyrics": full_lyrics,
            "formatted_lyrics": formatted_lyrics,
            "needs_split": needs_split,
            "first_page_content": first_page,
            "second_page_content": second_page,
            "key": "C"
        }
        
        processed_songs.append(song_obj)
    
    return processed_songs

@app.route('/')
def index():
    return '''
    <html>
        <body>
            <h1>Preview Pages</h1>
            <ul>
                <li><a href="/lyrics/1">Sample Lyrics Page</a></li>
                <li><a href="/chords/1">Sample Chords Page</a></li>
                <li><a href="/presentation">Presentation</a></li>
            </ul>
        </body>
    </html>
    '''

@app.route('/lyrics/<int:song_id>')
def lyrics_page(song_id):
    songs = process_chord_arrays(load_songs_data())
    song = next((s for s in songs if s["id"] == song_id), None)
    if song:
        return render_template('single_song_lyrics.html', song=song)
    return "Song not found", 404

@app.route('/chords/<int:song_id>')
def chords_page(song_id):
    songs = process_chord_arrays(load_songs_data())
    song = next((s for s in songs if s["id"] == song_id), None)
    if song:
        return render_template('single_song_chords.html', song=song)
    return "Song not found", 404

@app.route('/presentation')
def presentation():
    songs = process_chord_arrays(load_songs_data())
    songs_with_lyrics = [song for song in songs if song["lyrics"]]
    return render_template('presentation.html', songs=songs_with_lyrics, title="Song Presentation")

if __name__ == '__main__':
    app.run(debug=True)
