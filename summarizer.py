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


def summarize_text():
    input_text = input_area.get("1.0", tk.END) 

    # Placeholder for your summarization logic
    # Example: 
    client = OpenAI()

    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a coding Expert. You know every languages and spent lots of years with educating coding to newbies. Everytime a code sent to you, look for bugs and correct them. You are always friendly to people and teach them like anybody can understand. Also you always give some tips to improve their code."},
        {"role": "user", "content": input_text}
    ]
    )
    summary = completion.choices[0].message.content # Temporary placeholder

    # Update the summary area with the result
    summary_area.config(state=tk.NORMAL)  
    summary_area.delete("1.0", tk.END)
    summary_area.insert(tk.END, summary)
    summary_area.config(state=tk.DISABLED)

def summarize_thread():
    """Run the summarization in a separate thread to avoid freezing the UI."""
    threading.Thread(target=summarize_text).start()

def check_clipboard():
    global last_clipboard

    current_clipboard = pyperclip.paste()
    if current_clipboard != last_clipboard:
        last_clipboard = current_clipboard

        if use_input_area.get():  # Check if user wants to use the input area
            input_area.delete("1.0", tk.END)  # Clear the input area
            input_area.insert(tk.END, current_clipboard)  # Paste the copied text

        if auto_summarize.get():
            summarize_thread()
        else:
            ask_to_summarize(current_clipboard)

    window.after(1000, check_clipboard)


def ask_to_summarize(text):
    def on_yes():
        dialog.destroy()
        summarize_thread()

    def on_no():
        dialog.destroy()

    dialog = tk.Toplevel(window)
    dialog.title("Summarize?")
    dialog.attributes('-topmost', True)

    text_label = ttk.Label(dialog, text=f"Summarize the copied text?\n\n{text[:200]}...", wraplength=400)  # Adjust wraplength as needed
    text_label.pack(padx=10, pady=10)

    button_frame = ttk.Frame(dialog)
    button_frame.pack(pady=10)

    yes_button = ttk.Button(button_frame, text="Yes", command=on_yes)
    yes_button.pack(side=tk.LEFT, padx=5)
    no_button = ttk.Button(button_frame, text="No", command=on_no)
    no_button.pack(side=tk.LEFT, padx=5)

# --- Main UI Setup ---
window = tk.Tk()
window.attributes('-topmost',True)
window.title("Text Summarizer")

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
ttk.Checkbutton(input_frame, text="Use input area", variable=use_input_area).pack(side=tk.LEFT)

auto_summarize = tk.BooleanVar(value=False)
ttk.Checkbutton(input_frame, text="Auto-summarize", variable=auto_summarize).pack(side=tk.LEFT)

input_label = ttk.Label(window, text="Enter your text:")
input_label.grid(row=1, column=0, padx=10, pady=(5, 0), sticky="w")

input_area = scrolledtext.ScrolledText(window, wrap=tk.WORD)
input_area.grid(row=2, column=0, padx=10, pady=(0, 5), sticky="nsew")

# --- Summarize Button ---
summarize_button = ttk.Button(window, text="Summarize", command=summarize_thread)
summarize_button.grid(row=3, column=0, pady=10, sticky="ew")

# --- Summary Area ---
summary_label = ttk.Label(window, text="Summary:")
summary_label.grid(row=4, column=0, padx=10, pady=(5, 0), sticky="w")

summary_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, state=tk.DISABLED)
summary_area.grid(row=5, column=0, padx=10, pady=(0, 5), sticky="nsew")

# Configure grid weights for resizing
window.grid_rowconfigure(2, weight=1)  # Input area gets more weight
window.grid_rowconfigure(5, weight=1)  # Summary area gets more weight
window.grid_columnconfigure(0, weight=1)  # Expand horizontally

last_clipboard = ""  # Store the last clipboard content to avoid duplicate checks
check_clipboard()

window.mainloop()
