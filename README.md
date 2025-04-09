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

1. Set up a virtual environment (recommended):
   ```bash
   # Create a virtual environment
   python -m venv venv
   
   # Activate the virtual environment
   # On Windows:
   .\.venv\Scripts\activate.bat

   Set-ExecutionPolicy -Scope CurrentUser unrestricted
   .\.venv\Scripts\activate.ps1

   # On macOS/Linux:
   source venv/bin/activate
   ```
   
   Your command prompt should now show `(venv)` at the beginning of the line, indicating the virtual environment is active.

2. Install dependencies:
   - Install Python dependencies using `pip install -r requirements.txt`.

3. Install wkhtmltopdf on Windows:
   - Download the installer from [wkhtmltopdf.org](https://wkhtmltopdf.org/downloads.html).
   - Run the installer and follow the installation wizard.
   - Make sure to remember the installation path (default is `C:\Program Files\wkhtmltopdf`).
   - Verify the installation by running `wkhtmltopdf --version` in Command Prompt.
   - Update the `WKHTMLTOPDF_PATH` variable in `main.py` to match your installation path if needed:
     ```python
     WKHTMLTOPDF_PATH = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
     ```

4. Place your Excel file in the `data` directory:
   - Only the "Siron" sheet will be processed
   - Ensure column A contains the song ID parameter

## Usage

### Basic Usage

Generate all document types:
```shell
python main.py
```

### Advanced Usage

#### Generate Specific Document Type

To generate only the song book with lyrics:
```shell
python main.py --type lyrics
```

To generate only the song book with chords:
```shell
python main.py --type chords
```

To generate only the presentation slides:
```shell
python main.py --type slides
```

#### Customize Templates

You can customize the templates used for generating documents. The templates are located in the `templates` directory. Modify the HTML files to suit your needs.

#### Pagination Settings

For longer songs, pagination is automatically handled. You can adjust pagination settings in the `config.py` file.

#### Table of Contents

The script generates multiple table of contents:
- By ID
- By song name

You can customize the appearance of the table of contents in the templates.

#### Excel File Requirements

Ensure your Excel file is placed in the `data` directory and contains a sheet named "Siron". The script processes only this sheet. Ensure column A contains the song ID parameter.

#### Debugging

If you encounter issues, use the `--debug` flag to enable debug mode:
```shell
python main.py --debug
```
This will provide detailed logs to help you troubleshoot.

## Troubleshooting

### Common Issues

1. **'python' is not recognized as a command:**
   - Ensure Python is installed and added to your PATH environment variable
   - Try using `py` or `python3` instead

2. **Cannot activate virtual environment:**
   - On Windows, you might need to set execution policy: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`
   - Make sure you created the virtual environment correctly

3. **Package installation errors:**
   - Make sure your virtual environment is activated (you should see `(venv)` in your command prompt)
   - Try updating pip: `pip install --upgrade pip`
   - If a package fails to install, check for any system dependencies it might require

4. **Deactivating the virtual environment:**
   - Simply type `deactivate` in your command prompt
   - Your command prompt should no longer show `(venv)` at the beginning

