import pandas as pd
import json
import os

# Load configuration
CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'config.json')
with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
    CONFIG = json.load(f)

def extract_data_to_json(excel_path=None, output_path=None):
    """
    Extract song data from Excel file and save as JSON
    
    Args:
        excel_path: Path to Excel file. Defaults to path from config.
        output_path: Path to save JSON output. Defaults to path from config.
    """
    if excel_path is None:
        excel_path = os.path.join(CONFIG['paths']['data_dir'], CONFIG['paths']['siron_excel_filename'])
    if output_path is None:
        output_path = os.path.join(CONFIG['paths']['data_dir'], CONFIG['paths']['songs_json_filename'])
        
    print(f"Reading data from {excel_path}...")
    
    # Mapping of Hungarian column headers to JSON property names from config
    column_mapping = CONFIG['excel_column_mapping']
    
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
        inner_id_counter = 0
        
        # Process each row
        for _, row in df.iterrows():
            inner_id_counter += 1
            # Create a song object with mapped properties
            song = {
                "id": str(row[first_column]),  # Ensure ID is a string
                "inner_id": str(inner_id_counter) # Add new inner_id
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
        # Ensure the output directory from config exists
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
        summary_json_path = os.path.join(CONFIG['paths']['data_dir'], CONFIG['paths']['songs_json_filename'])
        with open(summary_json_path, 'r', encoding='utf-8') as f:
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
