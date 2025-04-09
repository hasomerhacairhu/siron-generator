## Updated Software Requirements Specification (SRS) - Version 3

### 1. Introduction

This document provides the updated software requirements for the application that generates songbooks from an input Excel file. The software will include multiple templates for the table of contents and individual song pages, and it will use the `wkhtmltopdf` library for PDF generation. Additionally, a script will be responsible for generating the entire songbook, including the table of contents and song pages.

This version introduces the aspect ratio change for the projection songbook (16:9), and specifies the creation of an installation and usage guide in the `README.md` file.

### 2. Purpose

The purpose of the software is to automate the generation of songbooks in PDF format from an input Excel file, with different versions for singers, musicians, and projection. The software will generate and assemble the entire songbook, including:
- **Table of Contents Templates**: Two variations for singer and musician versions.
- **Song Page Templates**: Three versions for singer, musician, and projection (with 16:9 aspect ratio for projection).

### 3. Scope

The software will:
- Generate multiple templates for table of contents (ToC) and song pages.
- Generate entire songbooks in PDF format for each version (singer, musician, projection).
- The projection version will have a 16:9 aspect ratio for the pages.

### 4. Functional Requirements

#### 4.1 Template Requirements

There are three distinct templates required:

1. **Table of Contents Templates** (for singer and musician versions):
   - **ToC Template 1**: Ordered by `id`.
   - **ToC Template 2**: Ordered alphabetically by `title`.

2. **Song Page Templates**:
   - **Singer’s Songbook Template**: Contains only the lyrics in an A4 portrait layout.
   - **Musician’s Songbook Template**: Contains both lyrics and chords in an A4 portrait layout.
   - **Projection Songbook Template**: Contains only the lyrics with a **16:9 aspect ratio** (for screen projection).

#### 4.2 Script for Generating the Entire Songbook

The new script will handle the entire process of generating the songbook:
- **Input**: JSON file containing song data (`songs.json`).
- **Output**: Complete songbook in PDF format for each version (singer, musician, projection).

The script will:
1. **Generate Table of Contents**: Based on the selected ToC template.
2. **Generate Song Pages**: For each song, using the appropriate page template (lyrics-only, lyrics-with-chords, or projection).
3. **Combine Pages into a Full Songbook**: Merge all generated pages into a single PDF file for each version.

### 5. Detailed Functional Flow

1. **Input**: The input Excel file (`Siron.xlsx`) is parsed and converted into a JSON format (`songs.json`).
2. **Table of Contents Generation**:
   - **Version 1 & 2**: Two ToC templates are available:
     - ToC ordered by `id`.
     - ToC ordered alphabetically by `title`.
   - **Version 3 (Projection)**: No ToC is generated.
3. **Song Pages**:
   - For **singer** version, generate a page with lyrics only.
   - For **musician** version, generate a page with both lyrics and chords.
   - For **projection** version, generate a page with lyrics only in a **16:9 aspect ratio** (screen-friendly layout).
4. **Final Songbook Generation**:
   - Combine the generated pages and the ToC (if applicable) into a final PDF for each version.
   
### 6. System Architecture

1. **Data Parsing**:
   - The `generate_json.py` script reads the `Siron.xlsx` file and converts it into a `songs.json` format.
   
2. **Template Generation**:
   - Templates for the table of contents and song pages are stored in the `templates` folder:
     - **ToC Templates**: `toc_template_1.html`, `toc_template_2.html`.
     - **Song Page Templates**: `singer_song_page_template.html`, `musician_song_page_template.html`, `projection_song_page_template.html`.

3. **Songbook Generation**:
   - The `generate_songbook_page.py` script generates pages for each song based on the selected template.
   - The script will use the **wkhtmltopdf** library to convert HTML templates to PDF.
   - **Projection Version**: The template for projection uses a **16:9 aspect ratio** for each page, optimized for screen display.

4. **Complete Songbook Generation**:
   - The `generate_complete_songbook.py` script will combine all the generated pages and table of contents (if applicable) into one PDF per version.
   - The final output PDFs will be saved in version-specific folders in the `output` directory (`singers_songbook`, `musicians_songbook`, `projection_songbook`).

### 7. Template and CSS Management

- **CSS Styles**: A common CSS style will be used across all templates to maintain consistent styling.
- **Template Organization**:
  - **Table of Contents Templates**:
    - `toc_template_1.html`: ToC ordered by `id`.
    - `toc_template_2.html`: ToC ordered alphabetically by `title`.
  - **Song Page Templates**:
    - `singer_song_page_template.html`: For singer songbooks (lyrics only).
    - `musician_song_page_template.html`: For musician songbooks (lyrics with chords).
    - `projection_song_page_template.html`: For projection songbooks (lyrics only with 16:9 aspect ratio).

### 8. Non-Functional Requirements

#### 8.1 Usability
- The software should be easy to use, with clear input and output folder structures (`data`, `output`, `templates`).
- The software should provide easy configuration via command-line arguments to select the songbook version, include/exclude the table of contents, and set other preferences.

#### 8.2 Flexibility
- The system should allow for easy modifications to templates, including layout and styling changes.
- The system should support future expansions, such as additional templates or songbook versions.

#### 8.3 Performance
- The system should handle large numbers of songs efficiently and generate PDFs within a reasonable time frame.

### 9. Technical Requirements

- **Programming Language**: Python 3.x.
- **Libraries**:
  - `wkhtmltopdf` (for PDF generation).
  - Pandas (for processing Excel data).
  - Jinja2 (for templating).
  - PyPDF2 (for merging PDFs).
  - OpenPyXL or xlrd (for reading Excel files).
  
- **Directory Structure**:
  ```
  ├── data/
  │   ├── Siron.xlsx
  │   └── songs.json
  ├── output/
  │   ├── singers_songbook/
  │   ├── musicians_songbook/
  │   └── projection_songbook/
  ├── src/
  │   ├── generate_json.py
  │   ├── generate_songbook_page.py
  │   ├── generate_complete_songbook.py
  │   └── merge_pdfs.py
  └── templates/
      ├── base_template.html
      ├── toc_template_1.html
      ├── toc_template_2.html
      ├── singer_song_page_template.html
      ├── musician_song_page_template.html
      └── projection_song_page_template.html
  ```

### 10. Installation and Usage Guide

#### 10.1 Installation

1. Clone the repository.
2. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Install `wkhtmltopdf` as per the [installation instructions](https://wkhtmltopdf.org/downloads.html).

#### 10.2 Usage

1. Place your input Excel file (`Siron.xlsx`) in the `data` directory.
2. Run the JSON generation script:

    ```bash
    python src/generate_json.py
    ```

3. Generate the complete songbook using:

    ```bash
    python src/generate_complete_songbook.py --version singers --toc yes
    ```

4. The final songbook PDF will be saved in the `output/singers_songbook` directory.

#### 10.3 Directory Structure

- **data/**: Input files (Excel and JSON).
- **templates/**: Templates for different songbook versions.
- **src/**: Python scripts for processing and generating PDFs.
- **output/**: Output PDFs, categorized by version.

### 11. README.md - Installation and Usage Guide

The `README.md` file should include the following sections:
1. **Installation Instructions**:
   - How to clone the repository and install dependencies.
   - How to install `wkhtmltopdf` (link to download page).
2. **Usage Instructions**:
   - How to prepare the input Excel file and place it in the `data` folder.
   - Instructions on running the script to generate the JSON file.
   - Instructions on running the script to generate the songbook PDFs (including options for selecting the version and table of contents).
3. **Directory Structure**:
   - Explanation of the folder and file organization in the project.

