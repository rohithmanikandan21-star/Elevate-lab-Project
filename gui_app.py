#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import sys
import os

ROOT = tk.Tk()
ROOT.title("Password Analyzer & Wordlist Generator")
ROOT.geometry("600x400")

notebook = ttk.Notebook(ROOT)
frame1 = ttk.Frame(notebook)
frame2 = ttk.Frame(notebook)
notebook.add(frame1, text='Analyze')
notebook.add(frame2, text='Generate')
notebook.pack(expand=True, fill='both')

# Analyze tab
pw_label = ttk.Label(frame1, text="Password:")
pw_label.pack(padx=8, pady=6)
pw_entry = ttk.Entry(frame1, width=50, show='*')
pw_entry.pack(padx=8, pady=6)
output = tk.Text(frame1, height=12)
output.pack(padx=8, pady=6, fill='x')

def run_analysis():
pw = pw_entry.get()
if not pw:
messagebox.showwarning("Input required", "Type a password to analyze")
return
# call the CLI script and show output
script = os.path.join(os.path.dirname(__file__), '..', 'analysis', 'password_analyzer.py')
cmd = [sys.executable, script, '--password', pw]
try:
res = subprocess.run(cmd, capture_output=True, text=True, check=True)
output.delete(1.0, tk.END)
output.insert(tk.END, res.stdout)
except subprocess.CalledProcessError as e:
output.delete(1.0, tk.END)
output.insert(tk.END, e.stdout + "\n" + e.stderr)

run_btn = ttk.Button(frame1, text="Analyze", command=run_analysis)
run_btn.pack(pady=6)

# Generate tab
names_label = ttk.Label(frame2, text="Names (comma separated):"); names_label.pack()
names_entry = ttk.Entry(frame2, width=60); names_entry.pack()
kw_label = ttk.Label(frame2, text="Keywords (comma separated):"); kw_label.pack()
kw_entry = ttk.Entry(frame2, width=60); kw_entry.pack()
years_label = ttk.Label(frame2, text="Year range (e.g., 1990-2025):"); years_label.pack()
years_entry = ttk.Entry(frame2, width=20); years_entry.pack()
out_label = ttk.Label(frame2, text="Output file:"); out_label.pack()
out_entry = ttk.Entry(frame2, width=60); out_entry.pack()
def browse():
f = filedialog.asksaveasfilename(defaultextension=".txt")
if f: out_entry.delete(0, tk.END); out_entry.insert(0, f)
browse_btn = ttk.Button(frame2, text="Browse", command=browse); browse_btn.pack(pady=6)

def gen_action():
out = out_entry.get()
if not out:
messagebox.showwarning("Missing", "Choose output file")
return
script = os.path.join(os.path.dirname(__file__), '..', 'generator', 'wordlist_generator.py')
cmd = [sys.executable, script,
'--names', names_entry.get(),
'--keywords', kw_entry.get(),
           '--years', years_entry.get() or '1990-2025',
           '-o', out]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        messagebox.showinfo("Done", res.stdout)
    except Exception as e:
        messagebox.showerror("Error", str(e))

gen_btn = ttk.Button(frame2, text="Generate", command=gen_action); gen_btn.pack(pady=10)

ROOT.mainloop()
