# PDF Name Change


Most PDFs downloaded from the internet come with random or unreadable filenames, making it hard to organize and find documents later. As users, we often want to rename them for better organization, but doing this manually is tedious and error-prone. This program automates the process by using advanced Large Language Models (LLMs) to extract the actual title and first author's last name from the PDF content, and then renames the files accordingly. While using LLMs for this task might seem like overkill, it ensures highly accurate and context-aware renaming, saving you time and effort.

This application automatically renames PDF files in a folder based on their title and first author's last name, using either OpenAI or Google Gemini (Gemini API) for extraction.

**Note:** You can easily modify the prompt in the code to adapt this tool for other use cases, such as extracting different metadata or renaming files according to your own rules. Just edit the prompt string in the code to suit your needs.

## Features
- Batch rename PDFs in a folder to `[Title of the Paper] - [First Author's Last Name].pdf`
- Works with both OpenAI and Google Gemini (Gemini API) models
- Simple graphical interface (no command line needed)

## Requirements
- Python 3.9+
- OpenAI API key and/or Google Gemini API key

## Setup

### 1. Clone or Download the Project
Download or clone this repository to your computer.

### 2. Project Dependencies
The main dependencies for this project are:

- Python 3.9+
- PyPDF2
- openai
- google-genai
- pydantic < 2.0 (for google-genai)
- tk (for tkinter GUI)

You can install these using conda and pip as needed, or add them to a requirements file for pip installation.

### 3. Run the Application

```sh
python main.py
```

## Usage
1. Enter your API key (OpenAI or Gemini).
2. Enter the model name:
	- For OpenAI: e.g. `gpt-3.5-turbo`
	- For Gemini: e.g. `gemini-2.5-flash` (default)
3. Select the folder containing your PDF files.
4. Click **Start**. The PDFs will be renamed in place.

## Building a Standalone EXE
You can create a Windows executable using PyInstaller:

1. Install PyInstaller:
	```sh
	pip install pyinstaller
	```
2. Build the EXE:
	```sh
	pyinstaller --onefile --windowed --icon=icon-removebg-preview.ico main.py
	```
	The EXE will be in the `dist` folder. Copy any required files (like `icon-removebg-preview.ico` and `last_inputs.json` if needed) to the same folder as the EXE.

## Notes
- The app uses the first 3 pages of each PDF to extract the title and author.
- Your API key is not stored or shared, only used locally.
- If you use Gemini, make sure you have a valid Gemini API key from Google AI Studio.
- If you get errors about `pydantic`, ensure you have version 1.x: `pip install "pydantic<2.0"`

## License
MIT
