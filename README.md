# Siron Song Book Generator

A Python-based tool to generate song books in multiple formats from Excel data.

## Features

- Generates three document types:
  - Song book with lyrics (A4 format)
  - Song book with chords (A4 format)
  - Presentation slides (16:9 format)
- Automatically handles song pagination for longer songs
- Creates multiple table of contents (by ID and by song name)
- Customizable templates using Jinja2

## Setup

1. Install dependencies:
   - Install Python dependencies using `pip install -r requirements.txt`.
   - Install wkhtmltopdf:
     - Download the installer from [wkhtmltopdf.org](https://wkhtmltopdf.org/downloads.html).
     - Run the installer and follow the instructions.
     - Add the installation directory to your system's PATH environment variable.

