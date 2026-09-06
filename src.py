import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading
import os
import sys
import glob
import re

class ChdmanGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CHDMAN Converter GUI")
        self.root.geometry("550x380")
        self.root.resizable(False, False)
        
        # Determine the directory where this script/exe is running
        if getattr(sys, 'frozen', False):
            self.app_dir = os.path.dirname(sys.executable)
        else:
            self.app_dir = os.path.dirname(os.path.abspath(__file__))
            
        self.chdman_exe = os.path.join(self.app_dir, "chdman.exe")

        # Variables
        self.mode_var = tk.StringVar(value="cue2chd")
        self.process_var = tk.StringVar(value="single")
        self.input_path_var = tk.StringVar()
        self.output_dir_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready")
        self.progress_var = tk.DoubleVar(value=0.0)
        self.is_converting = False

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. Working Mode Selection
        mode_frame = ttk.LabelFrame(main_frame, text="Working Mode", padding="10")
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Radiobutton(mode_frame, text=".cue to .chd (Create CHD)", variable=self.mode_var, value="cue2chd").pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(mode_frame, text=".chd to .cue (Extract CHD)", variable=self.mode_var, value="chd2cue").pack(side=tk.LEFT)

        # 2. Processing Option
        process_frame = ttk.LabelFrame(main_frame, text="Processing Option", padding="10")
        process_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Radiobutton(process_frame, text="Single File", variable=self.process_var, value="single", command=self.on_process_change).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(process_frame, text="Batch Directory", variable=self.process_var, value="batch", command=self.on_process_change).pack(side=tk.LEFT)

        # 3. Path Selections
        path_frame = ttk.Frame(main_frame)
        path_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(path_frame, text="Input:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(path_frame, textvariable=self.input_path_var, width=50).grid(row=0, column=1, padx=10, pady=5)
        ttk.Button(path_frame, text="Browse...", command=self.browse_input).grid(row=0, column=2, pady=5)

        ttk.Label(path_frame, text="Output Dir:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(path_frame, textvariable=self.output_dir_var, width=50).grid(row=1, column=1, padx=10, pady=5)
        ttk.Button(path_frame, text="Browse...", command=self.browse_output).grid(row=1, column=2, pady=5)

        # 4. Progress and Status
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=(10, 20))
        ttk.Label(progress_frame, textvariable=self.status_var).pack(anchor=tk.W, pady=(0, 5))
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100, mode='determinate')
        self.progress_bar.pack(fill=tk.X)

        # 5. Bottom Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)
        
        self.start_btn = ttk.Button(btn_frame, text="Start Converting", command=self.start_conversion)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(btn_frame, text="Open Output Folder", command=self.open_output).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="Exit", command=self.root.quit).pack(side=tk.RIGHT)

    def on_process_change(self):
        # Clear input path when changing between single and batch to avoid confusion
        self.input_path_var.set("")

    def browse_input(self):
        process = self.process_var.get()
        mode = self.mode_var.get()
        
        if process == "single":
            ext = "*.cue" if mode == "cue2chd" else "*.chd"
            filetypes = [(f"{ext.replace('*', '').upper()} Files", ext)]
            path = filedialog.askopenfilename(title="Select Input File", filetypes=filetypes)
        else:
            path = filedialog.askdirectory(title="Select Input Directory")
            
        if path:
            self.input_path_var.set(os.path.normpath(path))

    def browse_output(self):
        path = filedialog.askdirectory(title="Select Target Output Directory")
        if path:
            self.output_dir_var.set(os.path.normpath(path))

    def open_output(self):
        folder = self.output_dir_var.get()
        if not folder or not os.path.exists(folder):
            # Fallback to input directory if output isn't set yet
            in_path = self.input_path_var.get()
            if os.path.isdir(in_path):
                folder = in_path
            elif os.path.isfile(in_path):
                folder = os.path.dirname(in_path)
                
        if folder and os.path.exists(folder):
            os.startfile(folder)
        else:
            messagebox.showinfo("Info", "Output directory not found or not set.")

    def start_conversion(self):
        if self.is_converting:
            return

        if not os.path.exists(self.chdman_exe):
            messagebox.showerror("Error", f"chdman.exe not found!\n\nPlease place it here:\n{self.chdman_exe}")
            return

        input_path = self.input_path_var.get()
        output_dir = self.output_dir_var.get()

        if not input_path:
            messagebox.showwarning("Warning", "Please select an input path.")
            return

        if not output_dir:
            # Default to input directory if no output directory selected
            output_dir = input_path if os.path.isdir(input_path) else os.path.dirname(input_path)
            self.output_dir_var.set(output_dir)

        self.is_converting = True
        self.start_btn.state(['disabled'])
        
        # Start conversion in a background thread to prevent UI freezing
        threading.Thread(target=self.run_conversion_thread, args=(input_path, output_dir), daemon=True).start()

    def update_ui(self, status=None, progress=None):
        if status is not None:
            self.status_var.set(status)
        if progress is not None:
            self.progress_var.set(progress)

    def conversion_done(self):
        self.is_converting = False
        self.start_btn.state(['!disabled'])
        self.update_ui(status="Conversion Complete!", progress=100.0)
        messagebox.showinfo("Success", "All tasks finished successfully.")

    def conversion_error(self, err_msg):
        self.is_converting = False
        self.start_btn.state(['!disabled'])
        self.update_ui(status="Error occurred.", progress=0.0)
        messagebox.showerror("Error", err_msg)

    def run_conversion_thread(self, input_path, output_dir):
        mode = self.mode_var.get()
        process = self.process_var.get()
        
        files_to_process = []
        if process == "batch":
            ext = "*.cue" if mode == "cue2chd" else "*.chd"
            search_pattern = os.path.join(input_path, ext)
            files_to_process = glob.glob(search_pattern)
        else:
            if os.path.isfile(input_path):
                files_to_process = [input_path]

        if not files_to_process:
            self.root.after(0, self.conversion_error, "No matching files found in the specified path.")
            return

        total_files = len(files_to_process)

        for idx, file_path in enumerate(files_to_process):
            filename = os.path.basename(file_path)
            base_name = os.path.splitext(filename)[0]
            
            self.root.after(0, self.update_ui, f"Converting ({idx+1}/{total_files}): {filename}", 0.0)

            if mode == "cue2chd":
                out_file = os.path.join(output_dir, base_name + ".chd")
                cmd = [self.chdman_exe, "createcd", "-i", file_path, "-o", out_file]
            else:
                out_file = os.path.join(output_dir, base_name + ".cue")
                cmd = [self.chdman_exe, "extractcd", "-i", file_path, "-o", out_file]

            try:
                # Read output byte by byte because chdman uses \r for progress updates without newlines
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
                
                buffer = b""
                while True:
                    char = proc.stdout.read(1)
                    if not char and proc.poll() is not None:
                        break
                    if char:
                        buffer += char
                        if char in (b'\r', b'\n'):
                            line = buffer.decode('utf-8', errors='ignore')
                            # Look for percentage (e.g., 45.3%)
                            match = re.search(r'(\d+\.\d+)%', line)
                            if match:
                                percent = float(match.group(1))
                                self.root.after(0, self.update_ui, None, percent)
                            buffer = b""
                            
                if proc.returncode != 0:
                    self.root.after(0, self.conversion_error, f"chdman failed on {filename}.\nEnsure the cue/chd and bin files are valid.")
                    return
                    
            except Exception as e:
                self.root.after(0, self.conversion_error, f"System Error:\n{str(e)}")
                return

        self.root.after(0, self.conversion_done)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChdmanGUI(root)
    root.mainloop()