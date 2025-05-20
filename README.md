# Siron Songbook Generator

A tool for generating songbooks in PDF format from an Excel file, with different versions for singers, musicians, and projection.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Generating JSON from Excel](#generating-json-from-excel)
  - [Generating Song Pages](#generating-song-pages)
  - [Generating Table of Contents](#generating-table-of-contents)
  - [Generating All Pages for a Version (New)](#generating-all-pages-for-a-version-new)
  - [Building a Final Merged Songbook (New)](#building-a-final-merged-songbook-new)
  - [Finding YouTube Links (New)](#finding-youtube-links-new)
- [Directory Structure](#directory-structure)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)

## Overview

This application automates the generation of songbooks in PDF format, with different versions:

- **Singer's Songbook**: Contains only lyrics in A4 portrait format
- **Musician's Songbook**: Contains lyrics and chords in A4 portrait format
- **Projection Songbook**: Contains lyrics in 16:9 aspect ratio for screen display

The system uses:
- Python scripts for data processing
- Jinja2 templates for page layouts
- wkhtmltopdf for HTML to PDF conversion
- PyPDF2 for merging multiple PDFs

## Installation

### Prerequisites

- Python 3.6 or higher
- wkhtmltopdf

### Step 1: Clone the repository

```bash
git clone https://github.com/yourusername/siron-generator.git
cd siron-generator
```

### Step 2: Install Python dependencies

```bash
pip install -r requirements.txt
```

This will install all required Python packages:
- pandas
- jinja2
- pypdf2
- openpyxl
- youtube-search-python
- python-dotenv
- qrcode

### Step 3: Install wkhtmltopdf

#### Windows
1. Download the installer from [wkhtmltopdf downloads](https://wkhtmltopdf.org/downloads.html)
2. Run the installer and follow the installation wizard
3. Make sure the wkhtmltopdf executable is in your system PATH

#### macOS
```bash
brew install wkhtmltopdf
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get install wkhtmltopdf
```

## Usage

### Generating JSON from Excel

Place your input Excel file (`Siron.xlsx`) in the `data` directory, then run:

```bash
python src/generate_json.py
```

This will create a `songs.json` file in the data directory, which contains all the song information in a structured format.

### Generating Song Pages

To generate a page for a specific song:

```bash
python src/generate_songbook_page.py --song-id [ID] --version [singer|musician|projection]
```

Options:
- `--song-id`: The ID of the song to generate a page for
- `--version`: Songbook version to generate (singer, musician, or projection)
- `--templates-dir`: Directory containing template files (default: ../templates)
- `--output-dir`: Directory to save output files (default: ../output)
- `--json-file`: Path to the JSON file containing song data (default: ../data/songs.json)

Example:
```bash
python src/generate_songbook_page.py --song-id ZS08 --version musician
```

### Generating Table of Contents

To generate a table of contents:

```bash
python src/generate_toc.py --version [singer|musician] --toc-version [1|2]
```

Options:
- `--version`: Songbook version to generate (singer or musician)
- `--toc-version`: ToC version: 1 for ordered by ID, 2 for alphabetical by title
- `--templates-dir`: Directory containing template files (default: ../templates)
- `--output-dir`: Directory to save output files (default: ../output)
- `--json-file`: Path to the JSON file containing song data (default: ../data/songs.json)

Example:
```bash
python src/generate_toc.py --version singer --toc-version 2
```

Note: Projection version does not include a table of contents.

### Generating All Pages for a Version (New)

To generate all pages for a specific songbook version, including both types of Table of Contents (for singer/musician versions) and all individual song pages:

```bash
python src/generate_full_songbook.py --version [singer|musician|projection]
```

Options:
- `--version`: (Required) Songbook version to generate (`singer`, `musician`, or `projection`).
- `--songs-json`: (Optional) Path to the JSON file containing song data. Overrides the path in `config.json`.
- `--templates-dir`: (Optional) Directory containing template files. Overrides the path in `config.json`.
- `--output-dir`: (Optional) Directory to save output files. Overrides the path in `config.json`.

Example:
```bash
python src/generate_full_songbook.py --version singer
```

This script will:
1. Generate the Table of Contents sorted by ID (if applicable).
2. Generate the Table of Contents sorted by Title (if applicable).
3. Generate individual PDF pages for all songs listed in the `songs.json` file for the specified version.

### Building a Final Merged Songbook (New)

After generating all individual song pages and TOCs (e.g., by using `generate_full_songbook.py`), you can merge them into a single PDF document for a specific version.

```bash
python src/build_final_songbook.py --version [singer|musician|projection]
```

Options:
- `--version`: (Required) Songbook version to build (`singer`, `musician`, or `projection`).

Example:
```bash
python src/build_final_songbook.py --version musician
```

This script will:
1. Look for `toc_by_id.pdf` and `toc_by_title.pdf` in the version-specific output folder (e.g., `output/musicians_songbook/`) and add them to the merge list if found. For `projection` version, TOCs are skipped.
2. Scan the version-specific output folder for all `song_*.pdf` files.
3. Sort the song PDFs numerically based on the number in their filename (which corresponds to `inner_id`).
4. Merge the PDFs in the following order:
    - `toc_by_id.pdf` (if applicable and found)
    - `toc_by_title.pdf` (if applicable and found)
    - All sorted `song_*.pdf` files.
5. Save the final merged document directly in the `output/` directory with a filename like `{version}_SironSongbook_Merged.pdf` (e.g., `musician_SironSongbook_Merged.pdf`).

**Important Note:** This script assumes that the individual song PDF files (e.g., `song_1.pdf`, `song_2.pdf`) and TOCs have already been generated in the respective version's subdirectory within the `output` folder. You should run `generate_full_songbook.py` before running this script.

### Finding YouTube Links (New)

To find YouTube links for all songs in your `songs.json` file and export them to a text file:

```bash
python src/find_youtube_links.py
```

Options:
- `--songs_json`: (Optional) Path to the input `songs.json` file. Defaults to the path specified in `config.json` (usually `data/songs.json`).
- `--output_txt`: (Optional) Path to the output TXT file where links will be saved. Defaults to `output/youtube_links.txt`.

Example:
```bash
python src/find_youtube_links.py --songs_json data/my_custom_songs.json --output_txt output/custom_links.txt
```

This script will:
1. Read each song from the specified `songs.json` file.
2. If a song entry already has a `youtube_link` field, that link is used.
3. Otherwise, it searches YouTube for the song using its title and author.
    - It prioritizes "official music videos".
    - If not found, it looks for "audio" or "lyric" videos, preferring the most viewed.
    - It tries to exclude live or concert recordings.
4. Write the found YouTube link (or a "-" if no suitable link is found) to the output TXT file, one link per line, corresponding to each song in the input JSON.
5. The `songs.json` file itself is **not** modified by this script. If you want to update `songs.json` with these links, you'll need to do that manually or with another script.

## Directory Structure

```
siron-generator/
├── data/
│   ├── Siron.xlsx          # Input Excel file
│   └── songs.json          # Converted JSON data
├── output/
│   ├── youtube_links.txt   # Exported YouTube links
│   ├── singers_songbook/   # Generated PDFs for singers
│   ├── musicians_songbook/ # Generated PDFs for musicians
│   ├── projection_songbook/ # Generated PDFs for projection
│   ├── singer_SironSongbook_Merged.pdf   # Final merged singer songbook
│   └── musician_SironSongbook_Merged.pdf # Final merged musician songbook
├── src/
│   ├── generate_json.py     # Converts Excel to JSON
│   ├── generate_songbook_page.py # Generates individual song pages
│   ├── generate_toc.py      # Generates table of contents
│   ├── generate_full_songbook.py # Generates all pages for a version (TOCs + all songs)
│   ├── build_final_songbook.py # Merges TOCs and all song pages for a version into a single PDF
│   └── find_youtube_links.py # Finds YouTube links for songs
└── templates/
    ├── toc_template_1.html  # ToC ordered by ID
    ├── toc_template_2.html  # ToC ordered alphabetically
    ├── singer_song_page_template.html # Singer version template
    ├── musician_song_page_template.html # Musician version template
    └── projection_song_page_template.html # Projection version template
```

## Customization

### Configuration (`config.json`)
Many aspects of the generation process are controlled by `config.json`. This includes:
- Default file paths (data directory, output directory, specific filenames).
- Excel column mappings for `generate_json.py`.
- Guitar chords recognized by `generate_songbook_page.py`.
- Lyrics length thresholds for font size adjustments and column breaks.
- Page parameters (size, margins, orientation, zoom) for PDF generation via `wkhtmltopdf`.
- Template filenames.

### Template Customization

You can modify the HTML templates in the `templates` directory to change the appearance of your songbooks:

- **Singer's template**: Modify `singer_song_page_template.html`
- **Musician's template**: Modify `musician_song_page_template.html`
- **Projection template**: Modify `projection_song_page_template.html`
- **Table of Contents templates**: Modify `toc_template_1.html` or `toc_template_2.html`

### CSS Styling

Each template includes CSS styling within the `<style>` section that can be customized to change:

- Fonts and text sizes
- Colors
- Spacing and margins
- Page dimensions

### WKHTMLTOPDF Path

The path to the `wkhtmltopdf` executable is typically defined in `config.json` or can be set via the `WKHTMLTOPDF_PATH` environment variable. Ensure this path is correct for your system.

## Troubleshooting

### Common Issues

1. **wkhtmltopdf not found**: Ensure wkhtmltopdf is installed and in your system PATH

2. **Missing dependencies**: Make sure all required Python packages are installed:
   ```bash
   pip install -r requirements.txt
   ```

3. **Template errors**: If you customize templates, verify your HTML/CSS is valid

4. **Excel parsing errors**: Ensure your Excel file follows the expected format

### Getting Help

For additional assistance or to report bugs, please create an issue on the GitHub repository.
