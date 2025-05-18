# Siron Songbook Generator

A tool for generating songbooks in PDF format from an Excel file, with different versions for singers, musicians, and projection.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Generating JSON from Excel](#generating-json-from-excel)
  - [Generating Song Pages](#generating-song-pages)
  - [Generating Table of Contents](#generating-table-of-contents)
  - [Creating Complete Songbooks](#creating-complete-songbooks)
  - [Generating All Pages for a Version (New)](#generating-all-pages-for-a-version-new)
  - [Building a Final Merged Songbook (New)](#building-a-final-merged-songbook-new)
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

### Creating Complete Songbooks

To generate a complete songbook:

```bash
python src/generate_complete_songbook.py --version [singer|musician|projection] --toc-version [1|2|none]
```

Options:
- `--version`: Songbook version to generate (singer, musician, or projection)
- `--toc-version`: ToC version: 1 for ordered by ID, 2 for alphabetical by title, none for no ToC
- `--templates-dir`: Directory containing template files (default: ../templates)
- `--output-dir`: Directory to save output files (default: ../output)
- `--json-file`: Path to the JSON file containing song data (default: ../data/songs.json)

Example:
```bash
python src/generate_complete_songbook.py --version musician --toc-version 1
```

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
1. For `singer` and `musician` versions:
    - Call `generate_toc.py` to create a Table of Contents (TOC) sorted by ID. This TOC is saved as `toc_by_id.pdf` in the version-specific output folder (e.g., `output/musicians_songbook/`).
    - Call `generate_toc.py` again to create a TOC sorted by Title. This TOC is saved as `toc_by_title.pdf` in the same folder.
2. For `projection` version, TOC generation is skipped.
3. Scan the version-specific output folder (e.g., `output/musicians_songbook/`) for all `song_*.pdf` files.
4. Sort the song PDFs numerically by their `inner_id` (extracted from the filename).
5. Merge the PDFs in the following order:
    - `toc_by_id.pdf` (if applicable)
    - `toc_by_title.pdf` (if applicable)
    - All sorted `song_*.pdf` files.
6. Save the final merged document directly in the `output/` directory with a filename like `{version}_SironSongbook_Merged.pdf` (e.g., `musician_SironSongbook_Merged.pdf`).

**Important Note:** This script assumes that the individual song PDF files (e.g., `song_1.pdf`, `song_2.pdf`) have already been generated in the respective version's subdirectory within the `output` folder (e.g., `output/singers_songbook/`). You should run `generate_full_songbook.py` or `generate_songbook_page.py` for all songs before running this script.

## Directory Structure

```
siron-generator/
├── data/
│   ├── Siron.xlsx          # Input Excel file
│   └── songs.json          # Converted JSON data
├── output/
│   ├── singers_songbook/   # Generated PDFs for singers
│   ├── musicians_songbook/ # Generated PDFs for musicians
│   └── projection_songbook/ # Generated PDFs for projection
├── src/
│   ├── generate_json.py     # Converts Excel to JSON
│   ├── generate_songbook_page.py # Generates individual song pages
│   ├── generate_toc.py      # Generates table of contents
│   ├── generate_complete_songbook.py # Generates entire songbooks (likely to be deprecated or merged)
│   ├── generate_full_songbook.py # Generates all pages for a version (TOCs + all songs)
│   └── build_final_songbook.py # Merges TOCs and all song pages for a version into a single PDF
└── templates/
    ├── toc_template_1.html  # ToC ordered by ID
    ├── toc_template_2.html  # ToC ordered alphabetically
    ├── singer_song_page_template.html # Singer version template
    ├── musician_song_page_template.html # Musician version template
    └── projection_song_page_template.html # Projection version template
```

## Customization

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
