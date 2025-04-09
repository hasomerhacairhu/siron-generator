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
│   └── generate_complete_songbook.py # Generates entire songbooks
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
