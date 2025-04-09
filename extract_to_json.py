import pandas as pd
import json
import os

def extract_data_to_json(excel_path='data/Siron.xlsx', output_path='data/songs.json'):
    """
    Extract song data from Excel file and save as JSON
    
    Args:
        excel_path: Path to Excel file
        output_path: Path to save JSON output
    """
    print(f"Reading data from {excel_path}...")
    
    # Mapping of Hungarian column headers to JSON property names
    column_mapping = {
        'Id': 'id',
        'Cím': 'title',
        'Szerző': 'author',
        'Dalszöveg': 'lyrics',
        'Dalszöveg akkordokkal': 'lyrics_with_chords',
        'Kategória': 'category',
        'Youtube link': 'youtube',
        'Érzékeny tartalom': 'explicit_content',
        'Állapot': 'status',
        'Dalszöveg tömb': 'lyrics_array',
        'Akkord Tömb': 'chords_array'
    }
    
    try:
        # Read the Excel file
        df = pd.read_excel(excel_path, sheet_name="Siron")
        
        # Ensure we have data
        if df.empty:
            print("Error: Excel file contains no data.")
            return False
        
        # Get the first column name (should contain ID)
        first_column = df.columns[0]
        
        # Create a list to hold our song objects
        songs = []
        
        # Process each row
        for _, row in df.iterrows():
            # Create a song object with mapped properties
            song = {
                "id": str(row[first_column])  # Ensure ID is a string
            }
            
            # Map each column to the corresponding JSON property if it exists
            for excel_header, json_prop in column_mapping.items():
                if excel_header in df.columns:
                    song[json_prop] = row.get(excel_header, "")
                else:
                    # Handle cases where columns might have different names or be missing
                    # Try some common alternatives
                    if json_prop == 'title' and 'name' in df.columns:
                        song[json_prop] = row.get('name', "")
                    elif json_prop == 'lyrics' and 'text' in df.columns:
                        song[json_prop] = row.get('text', "")
                    else:
                        song[json_prop] = ""
            
            # Fill in any missing values with empty strings
            for key in song:
                if pd.isna(song[key]):
                    song[key] = ""
            
            # Add to our songs list
            songs.append(song)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write to JSON file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(songs, f, ensure_ascii=False, indent=2)
        
        print(f"Successfully exported {len(songs)} songs to {output_path}")
        return True
    
    except Exception as e:
        print(f"Error extracting data: {str(e)}")
        return False

if __name__ == "__main__":
    # Run the extraction
    extract_data_to_json()
    
    # Provide a summary of the data
    try:
        with open('data/songs.json', 'r', encoding='utf-8') as f:
            songs = json.load(f)
            
        print("\nSummary:")
        print(f"Total songs: {len(songs)}")
        
        # Count songs with YouTube links
        youtube_count = sum(1 for song in songs if song.get('youtube'))
        print(f"Songs with YouTube links: {youtube_count}")
        
        # Count songs with explicit content
        explicit_count = sum(1 for song in songs if song.get('explicit_content'))
        print(f"Songs with explicit content: {explicit_count}")
        
        # Count songs by category
        categories = {}
        for song in songs:
            cat = song.get('category', '').strip()
            if cat:
                categories[cat] = categories.get(cat, 0) + 1
        
        if categories:
            print("\nSongs by category:")
            for cat, count in sorted(categories.items()):
                print(f"  {cat}: {count}")
    
    except Exception as e:
        print(f"Error generating summary: {str(e)}")
