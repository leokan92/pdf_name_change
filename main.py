
import PyPDF2
import os
import re
from openai import OpenAI
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import json

# Google Gemini imports
try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None


def extract_title_and_last_author_with_llm(text, api_key, model):
    """
    Dispatches to OpenAI or Google Gemini based on the model name.
    If model starts with 'gemini', use Google Gemini, else use OpenAI.
    """
    if model.lower().startswith("gemini"):
        return extract_with_gemini(text, api_key, model)
    else:
        return extract_with_openai(text, api_key, model)

def extract_with_openai(text, api_key, model):
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Extract the title and the first author's lastname from the following text. Respond with only the title, followed by the first author's lastname, separated by a semicolon, in the format: [Title of the Paper]; [First Author's Last Name].\n\n{text}"}
        ]
    )
    content = response.choices[0].message.content.strip()
    if ";" in content:
        title, last_author = content.split(";", 1)
        return title.strip(), last_author.strip()
    else:
        return "Unknown Title", "Unknown Author"

def extract_with_gemini(text, api_key, model):
    if genai is None or types is None:
        raise ImportError("google-genai is not installed. Please install it with 'pip install google-genai'.")
    # Set API key for Gemini
    import os as _os
    _os.environ["GEMINI_API_KEY"] = api_key
    client = genai.Client()
    prompt = (
        "Extract the title and the first author's lastname from the following text. "
        "Respond with only the title, followed by the first author's lastname, separated by a semicolon, "
        "in the format: [Title of the Paper]; [First Author's Last Name].\n\n" + text
    )
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0)
        ),
    )
    content = response.text.strip()
    if ";" in content:
        title, last_author = content.split(";", 1)
        return title.strip(), last_author.strip()
    else:
        return "Unknown Title", "Unknown Author"

def sanitize_filename(filename):
    filename = re.sub(r'[<>:"/\\|?*\n\r]', '', filename)
    filename = filename.strip()
    filename = re.sub(r'\s+', ' ', filename)
    return filename

def rename_pdf_with_title_and_author(pdf_path, api_key, model):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page_num in range(min(3, len(reader.pages))):
            text += reader.pages[page_num].extract_text() + "\n"
        
        title, author = extract_title_and_last_author_with_llm(text, api_key, model)
        sanitized_title = sanitize_filename(title)
        sanitized_author = sanitize_filename(author)

    new_file_name = f"{sanitized_title} - {sanitized_author}.pdf"
    new_file_path = os.path.join(os.path.dirname(pdf_path), new_file_name)
    os.rename(pdf_path, new_file_path)
    print(f"File renamed to: {new_file_name}")

def process_all_pdfs_in_directory(directory_path, api_key, model):
    pdf_files = [f for f in os.listdir(directory_path) if f.lower().endswith('.pdf')]
    total_files = len(pdf_files)
    progress_bar['maximum'] = total_files

    for index, filename in enumerate(pdf_files):
        pdf_path = os.path.join(directory_path, filename)
        try:
            rename_pdf_with_title_and_author(pdf_path, api_key, model)
        except Exception as e:
            print(f"Failed to process {filename}: {e}")
        progress_bar['value'] = index + 1
        root.update_idletasks()

def browse_directory():
    directory_path = filedialog.askdirectory()
    directory_entry.delete(0, tk.END)
    directory_entry.insert(0, directory_path)

def save_last_inputs(api_key, model, directory_path):
    data = {
        "api_key": api_key,
        "model": model,
        "directory_path": directory_path
    }
    with open("last_inputs.json", "w") as file:
        json.dump(data, file)

def load_last_inputs():
    if os.path.exists("last_inputs.json"):
        with open("last_inputs.json", "r") as file:
            return json.load(file)
    return {"api_key": "", "model": "", "directory_path": ""}

def start_processing():
    api_key = api_key_entry.get()
    model = model_entry.get()
    directory_path = directory_entry.get()
    if not api_key or not model or not directory_path:
        messagebox.showerror("Error", "All fields are required!")
        return
    save_last_inputs(api_key, model, directory_path)
    try:
        process_all_pdfs_in_directory(directory_path, api_key, model)
        messagebox.showinfo("Success", "Processing completed!")
    except ImportError as e:
        messagebox.showerror("Missing Dependency", str(e))
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Load last inputs when the app starts
last_inputs = load_last_inputs()

root = tk.Tk()
root.title("PDF Renamer")

tk.Label(root, text="API Key:").grid(row=0, column=0, padx=10, pady=5)
api_key_entry = tk.Entry(root, width=50)
api_key_entry.grid(row=0, column=1, padx=10, pady=5)
api_key_entry.insert(0, last_inputs["api_key"])

tk.Label(root, text="Model:").grid(row=1, column=0, padx=10, pady=5)
model_entry = tk.Entry(root, width=50)
model_entry.grid(row=1, column=1, padx=10, pady=5)
model_entry.insert(0, last_inputs["model"] or "gemini-2.5-flash")

tk.Label(root, text="Directory Path:").grid(row=2, column=0, padx=10, pady=5)
directory_entry = tk.Entry(root, width=50)
directory_entry.grid(row=2, column=1, padx=10, pady=5)
directory_entry.insert(0, last_inputs["directory_path"])
tk.Button(root, text="Browse", command=browse_directory).grid(row=2, column=2, padx=10, pady=5)

tk.Button(root, text="Start", command=start_processing).grid(row=3, column=0, columnspan=3, pady=20)
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

root.mainloop()
