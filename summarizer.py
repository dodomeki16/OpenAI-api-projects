import tkinter as tk
from tkinter import ttk, scrolledtext
from tkinter import messagebox  # Correct import
import threading  # For running the summarization in the background
from openai import OpenAI
import openai
import os
import pyperclip
import platform

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

openai.api_key=os.getenv("OPENAI_API_KEY")

def stream_to_textbox(text_chunk):
    summary_area.config(state=tk.NORMAL)
    summary_area.insert(tk.END, text_chunk)
    summary_area.config(state=tk.DISABLED)
    summary_area.see(tk.END)  # Scroll to the end
def summarize_text(text):
    client = OpenAI(api_key=openai.api_key)

    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a coding Expert. You know every languages and spent lots of years with educating coding to newbies. Everytime a code sent to you, look for bugs and correct them. You are always friendly to people and teach them like anybody can understand. Also you always give some tips to improve their code. You write in html format. Use in-code style features for your response to make them look better and read easier. I want you to use your HTML format to make texts look like chatgpt output. Try to imitate how they give response on their own website. Like codes on a different overlay, Lists on a special format etc. I want you to use your html style attributes to imitate that. Don't forget to use indentation on your response"},
            {"role": "user", "content": text}  
        ],
        stream=True
    )
    for chunk in stream:
        text_chunk = chunk.choices[0].delta.content
        if text_chunk:
            window.after(0, stream_to_textbox, text_chunk)  # Update the textbox immediately

def summarize_thread(text_to_summarize):
    threading.Thread(target=summarize_text, args=(text_to_summarize,)).start()

def check_clipboard():
    global last_clipboard

    current_clipboard = pyperclip.paste()

    if current_clipboard != last_clipboard:
        last_clipboard = current_clipboard

        if use_input_area.get():
            input_area.delete("1.0", tk.END)
            input_area.insert(tk.END, current_clipboard)

    window.after(1000, check_clipboard)


def get_comment():
    original_text = input_area.get("1.0", tk.END).strip()  # Get text from input area
    
    def on_submit():
        comment = comment_entry.get("1.0", tk.END).strip()
        comment_dialog.destroy()
        text_with_comment = f"Original text:\n{original_text}\n\nComment:\n{comment}"
        summarize_thread(text_with_comment)  # Directly summarize with the comment

    comment_dialog = tk.Toplevel(window)
    comment_dialog.title("Enter Comment")
    comment_dialog.attributes('-topmost', True)

    ttk.Label(comment_dialog, text="Enter your comment:").pack(padx=10, pady=(10, 0))
    comment_entry = scrolledtext.ScrolledText(comment_dialog, wrap=tk.WORD)
    comment_entry.pack(padx=10, pady=(0, 10), expand=True, fill="both")

    ttk.Button(comment_dialog, text="Submit", command=on_submit).pack(pady=10)

# --- Main UI Setup ---
window = tk.Tk()
window.attributes('-topmost',True)
window.title("Coding Coach")

# Get screen width and height (cross-platform)
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

# Calculate window position (top-right corner)
window_width = 300  # Adjust as needed
window_height = 400  # Adjust as needed
x_pos = screen_width - window_width
y_pos = 0

# Set window geometry (width, height, position)
window.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")

# --- Input Area ---
input_frame = ttk.Frame(window)
input_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")  # Use grid layout

use_input_area = tk.BooleanVar(value=True)
#ttk.Checkbutton(input_frame, text="Use input area", variable=use_input_area).pack(side=tk.LEFT)

auto_summarize = tk.BooleanVar(value=False)
#ttk.Checkbutton(input_frame, text="Auto-send", variable=auto_summarize).pack(side=tk.LEFT)

input_label = ttk.Label(window, text="Enter your text:")
input_label.grid(row=1, column=0, padx=10, pady=(5, 0), sticky="w")

input_area = scrolledtext.ScrolledText(window, wrap=tk.WORD)
input_area.grid(row=2, column=0, padx=10, pady=(0, 5), sticky="nsew")

# --- Comment Button --- 
comment_button = ttk.Button(window, text="Comment", command=get_comment)
comment_button.grid(row=3, column=0, pady=5, sticky="ew")

# --- Summarize Button ---
summarize_button = ttk.Button(window, text="Summarize", command=lambda: summarize_thread(input_area.get("1.0", tk.END).strip()))
summarize_button.grid(row=4, column=0, pady=5, sticky="ew")

# --- Summary Area ---
summary_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, state=tk.DISABLED)
summary_area.grid(row=5, column=0, padx=10, pady=(0, 5), sticky="nsew")

# Configure grid weights for resizing
window.grid_rowconfigure(2, weight=1)  # Input area gets more weight
window.grid_rowconfigure(5, weight=1)  # Summary area gets more weight
window.grid_columnconfigure(0, weight=1)  # Expand horizontally

last_clipboard = ""  # Store the last clipboard content to avoid duplicate checks
check_clipboard()

window.mainloop()
