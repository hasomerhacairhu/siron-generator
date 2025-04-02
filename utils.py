def split_songs_into_pages(songs):
    """
    Analyze songs and determine if they need to be split into multiple pages
    based on content length.
    
    Returns a list of songs with page split information.
    """
    songs_with_pages = []
    
    for song in songs:
        # Calculate approximate content length
        lyrics = song.get('lyrics', '')
        if not lyrics:
            lyrics = song.get('text', '')  # Fallback if 'lyrics' not found
        
        # Simple heuristic: if lyrics has more than 25 lines or 1500 characters, split into pages
        if lyrics.count('\n') > 25 or len(lyrics) > 1500:
            # Create a deep copy of the song for the second page
            song['needs_split'] = True
            
            # Split logic would be more complex in a real implementation
            # This is a simple approximation
            lines = lyrics.split('\n')
            split_point = len(lines) // 2
            
            song['first_page_content'] = '\n'.join(lines[:split_point])
            song['second_page_content'] = '\n'.join(lines[split_point:])
        else:
            song['needs_split'] = False
        
        songs_with_pages.append(song)
    
    return songs_with_pages

def generate_toc(songs, sort_by='id'):
    """
    Generate table of contents data sorted by the specified key.
    
    Args:
        songs: List of song dictionaries
        sort_by: Field to sort by ('id' or 'name')
    
    Returns:
        List of dictionaries with id, name, and page_number
    """
    if sort_by == 'id':
        sorted_songs = sorted(songs, key=lambda x: x.get('id', 0))
    else:  # sort_by == 'name'
        sorted_songs = sorted(songs, key=lambda x: x.get('name', '').lower())
    
    # In a real implementation, you would calculate actual page numbers
    # Here we're using a placeholder approach
    toc = []
    current_page = 1
    
    for song in sorted_songs:
        toc.append({
            'id': song.get('id', ''),
            'name': song.get('name', ''),
            'page': current_page
        })
        
        # Increment page counter based on song length
        current_page += 1
        if song.get('needs_split', False):
            current_page += 1
    
    return toc
