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

# Conversation History
conversation_history = [
    {"role": "system", "content": "You are the best companion in the world. You try to help anyone that comes to you for it. After  doing what they want, always try to give some extra advices that might come in handy. But avoid it in unnecessary situations."},
]
def stream_to_textbox(text_chunk):
    companion_area.config(state=tk.NORMAL)
    companion_area.insert(tk.END, text_chunk)
    companion_area.config(state=tk.DISABLED)
    companion_area.see(tk.END)  # Scroll to the end
def send_text(text):
    global conversation_history  # Access the global conversation history
    
    # Clear the companion area before the new response
    companion_area.config(state=tk.NORMAL)
    companion_area.delete("1.0", tk.END)
    companion_area.config(state=tk.DISABLED)

    # Add user's message to the conversation history
    conversation_history.append({"role": "user", "content": text})

    client = OpenAI(api_key=openai.api_key)
    
    stream = client.chat.completions.create(
        model=current_model,
        messages=conversation_history,  # Use the full history
        stream=True,
    )
    
    for chunk in stream:
        text_chunk = chunk.choices[0].delta.content
        if text_chunk:
            window.after(0, stream_to_textbox, text_chunk)
    input_area.delete("1.0", tk.END)
    model = current_model.get()

    # Add assistant's response to the history (after streaming is complete)
    conversation_history.append(
        {"role": "assistant", "content": companion_area.get("1.0", tk.END).strip()}
    )

def send_thread(text_to_send):
    threading.Thread(target=send_text, args=(text_to_send,)).start()

def check_clipboard():
    global last_clipboard

    current_clipboard = pyperclip.paste()

    if current_clipboard != last_clipboard:
        last_clipboard = current_clipboard

        if use_input_area.get():
            input_area.delete("1.0", tk.END)
            input_area.insert(tk.END, current_clipboard, "color")  # Insert with "color" tag

    window.after(1000, check_clipboard)

# Function to set the model
def set_model(model_name):
    global current_model
    current_model = model_name
    print("Model changed to:", current_model)

set_model("gpt-3.5-turbo")
def get_comment():
    original_text = input_area.get("1.0", tk.END).strip()  # Get text from input area
    
    def on_submit():
        comment = comment_entry.get("1.0", tk.END).strip()
        comment_dialog.destroy()
        text_with_comment = f"Original text:\n{original_text}\n\nComment:\n{comment}"
        send_thread(text_with_comment)  # Directly send with the comment

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
window.title("Companion")

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

# --- Input Area --- (Adjust row here and for the elements below)
input_frame = ttk.Frame(window)
input_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

use_input_area = tk.BooleanVar(value=True)
#ttk.Checkbutton(input_frame, text="Use input area", variable=use_input_area).pack(side=tk.LEFT)

auto_send = tk.BooleanVar(value=False)
#ttk.Checkbutton(input_frame, text="Auto-send", variable=auto_send).pack(side=tk.LEFT)

input_label = ttk.Label(window, text="Enter your text:")
input_label.grid(row=1, column=0, padx=10, pady=(5, 0), sticky="w")

input_area = scrolledtext.ScrolledText(window, wrap=tk.WORD)
input_area.grid(row=2, column=0, padx=10, pady=(0, 5), sticky="nsew")

# --- Comment Button --- 
comment_button = ttk.Button(window, text="Comment", command=get_comment)
comment_button.grid(row=3, column=0, pady=5, sticky="ew")

# --- send Button ---
send_button = ttk.Button(window, text="Send", command=lambda: send_thread(input_area.get("1.0", tk.END).strip()))
send_button.grid(row=4, column=0, pady=5, sticky="ew")

# --- companion Area ---
companion_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, state=tk.DISABLED)
companion_area.grid(row=5, column=0, padx=10, pady=(0, 5), sticky="nsew")

# Configure grid weights for resizing
window.grid_rowconfigure(2, weight=1)  # Input area gets more weight
window.grid_rowconfigure(5, weight=1)  # companion area gets more weight
window.grid_columnconfigure(0, weight=1)  # Expand horizontally

# --- Model Selection Buttons --- (Modified)
model_frame = ttk.LabelFrame(window, text="Model")
model_frame.grid(row=0, column=0, sticky="w", padx=10, pady=5)

# Radio buttons arranged horizontally using grid
models = ["gpt-3.5-turbo", "gpt-4-turbo", "gpt-4o"]
for i, model in enumerate(models):
    ttk.Radiobutton(
        model_frame, 
        text=model.replace("-", " ").upper(),
        variable=current_model, 
        value=model,
        command=lambda m=model: set_model(m)
    ).grid(row=0, column=i, padx=5, sticky="w")  # Place in a row
  
last_clipboard = ""  # Store the last clipboard content to avoid duplicate checks
check_clipboard()

window.mainloop()
