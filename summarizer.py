import tkinter as tk
from tkinter import ttk, scrolledtext
import threading  # For running the summarization in the background
from openai import OpenAI
import openai
import os

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
        {"role": "system", "content": "You are a text summarizer. All you do is summarizing texts that been given to you. Only respond with 'Here is the summarize of your text' then proceed with text summarization. Don't say anything else"},
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

# --- Main UI Setup ---
window = tk.Tk()
window.title("Text Summarizer")

# --- Input Area ---
input_label = ttk.Label(window, text="Enter your text:")
input_label.pack(padx=10, pady=5)

input_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=80, height=15)
input_area.pack(padx=10, pady=5)

# --- Summarize Button ---
summarize_button = ttk.Button(window, text="Summarize", command=summarize_thread)
summarize_button.pack(pady=10)

# --- Summary Area ---
summary_label = ttk.Label(window, text="Summary:")
summary_label.pack(padx=10, pady=5)

summary_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=80, height=10, state=tk.DISABLED)
summary_area.pack(padx=10, pady=5)

window.mainloop()
