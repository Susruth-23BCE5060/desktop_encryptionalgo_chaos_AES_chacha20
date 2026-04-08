'''import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import threading
import crypto_engine # Importing your backend logic

class ChaosApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chaos-AES-ChaCha Hybrid Vault")
        self.root.geometry("600x500")
        self.root.configure(bg="#f0f0f0")

        # --- HEADER ---
        title_label = tk.Label(root, text="Chaos-AES-ChaCha Hybrid Encryption", 
                               font=("Helvetica", 16, "bold"), bg="#f0f0f0", fg="#333")
        title_label.pack(pady=15)

        # --- INPUT SECTION ---
        frame_input = tk.Frame(root, bg="#f0f0f0")
        frame_input.pack(pady=10)

        tk.Label(frame_input, text="Enter Password:", bg="#f0f0f0", font=("Arial", 11)).grid(row=0, column=0, padx=5)
        self.entry_pass = tk.Entry(frame_input, show="*", width=30, font=("Arial", 11))
        self.entry_pass.grid(row=0, column=1, padx=5)

        # --- BUTTONS ---
        frame_btns = tk.Frame(root, bg="#f0f0f0")
        frame_btns.pack(pady=15)

        btn_enc = tk.Button(frame_btns, text="ENCRYPT FILE", bg="#d9534f", fg="white", 
                            font=("Arial", 10, "bold"), width=15, height=2, command=self.start_encrypt)
        btn_enc.grid(row=0, column=0, padx=10)

        btn_dec = tk.Button(frame_btns, text="DECRYPT FILE", bg="#5cb85c", fg="white", 
                            font=("Arial", 10, "bold"), width=15, height=2, command=self.start_decrypt)
        btn_dec.grid(row=0, column=1, padx=10)

        # --- LOG WINDOW (To show the Hybrid Logic working) ---
        tk.Label(root, text="Algorithm Switching Log (Real-time):", bg="#f0f0f0", font=("Arial", 10)).pack(anchor="w", padx=20)
        self.log_area = scrolledtext.ScrolledText(root, width=70, height=15, font=("Consolas", 9))
        self.log_area.pack(pady=5)

    def log_message(self, message):
        """Adds a message to the log window."""
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)

    def start_encrypt(self):
        password = self.entry_pass.get()
        if not password:
            messagebox.showerror("Error", "Please enter a password first!")
            return
        
        file_path = filedialog.askopenfilename(title="Select File to Encrypt")
        if not file_path: return

        self.log_area.delete(1.0, tk.END) # Clear logs
        self.log_message(f"--- Starting Encryption for: {os.path.basename(file_path)} ---")
        
        # Run in a separate thread so GUI doesn't freeze
        threading.Thread(target=self.run_engine, args=("ENC", file_path, password)).start()

    def start_decrypt(self):
        password = self.entry_pass.get()
        if not password:
            messagebox.showerror("Error", "Please enter a password first!")
            return

        file_path = filedialog.askopenfilename(title="Select .chaos File", filetypes=[("Chaos Files", "*.chaos")])
        if not file_path: return

        self.log_area.delete(1.0, tk.END)
        self.log_message(f"--- Starting Decryption for: {os.path.basename(file_path)} ---")
        
        threading.Thread(target=self.run_engine, args=("DEC", file_path, password)).start()

    def run_engine(self, mode, file_path, password):
        try:
            cipher = crypto_engine.HybridCipher(password)
            
            # We pass 'self.log_message' so the engine can print to our window!
            if mode == "ENC":
                out = cipher.encrypt_file(file_path, status_callback=self.log_message)
                self.log_message(f"\nSUCCESS! Encrypted file saved at:\n{out}")
                messagebox.showinfo("Success", "Encryption Complete!")
            else:
                out = cipher.decrypt_file(file_path, status_callback=self.log_message)
                self.log_message(f"\nSUCCESS! Restored file saved at:\n{out}")
                messagebox.showinfo("Success", "Decryption Complete!")
                
        except Exception as e:
            self.log_message(f"\nERROR: {str(e)}")
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = ChaosApp(root)
    root.mainloop()'''
import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import threading
import crypto_engine

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ModernChaosApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Chaos-Hybrid Encryption Tool")
        self.geometry("800x600") # Made wider for logs
        self.resizable(False, False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Header ---
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#1a1a1a")
        self.header_frame.grid(row=0, column=0, sticky="ew", ipady=15)
        ctk.CTkLabel(self.header_frame, text="Chaos-AES-ChaCha Hybrid Vault", font=("Roboto Medium", 20), text_color="#ffffff").pack()

        # --- Tabs ---
        self.tabview = ctk.CTkTabview(self, width=700, height=250)
        self.tabview.grid(row=1, column=0, pady=10)
        self.tabview.add("Encryption")
        self.tabview.add("Decryption")

        self.setup_encryption_tab()
        self.setup_decryption_tab()

        # --- LOG WINDOW (The New Part) ---
        self.log_frame = ctk.CTkFrame(self, width=700, height=200)
        self.log_frame.grid(row=2, column=0, pady=10)
        
        ctk.CTkLabel(self.log_frame, text="Chaos Engine Live Logs:", text_color="gray").pack(anchor="w", padx=10, pady=5)
        
        self.log_box = ctk.CTkTextbox(self.log_frame, width=680, height=150, font=("Consolas", 12))
        self.log_box.pack(padx=10, pady=5)
        self.log_box.configure(state="disabled") # Read only

    def log_message(self, msg):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end") # Auto scroll to bottom
        self.log_box.configure(state="disabled")

    def setup_encryption_tab(self):
        tab = self.tabview.tab("Encryption")
        self.btn_select_enc = ctk.CTkButton(tab, text="Select File", command=self.select_file_enc)
        self.btn_select_enc.pack(pady=10)
        self.lbl_file_enc = ctk.CTkLabel(tab, text="No file selected", text_color="gray")
        self.lbl_file_enc.pack()
        self.entry_pass_enc = ctk.CTkEntry(tab, placeholder_text="Enter Password", show="*", width=200)
        self.entry_pass_enc.pack(pady=5)
        self.btn_run_enc = ctk.CTkButton(tab, text="LOCK FILE", fg_color="#c0392b", hover_color="#e74c3c", command=self.run_encryption)
        self.btn_run_enc.pack(pady=15)
        self.progress_enc = ctk.CTkProgressBar(tab, width=400)
        self.progress_enc.set(0)
        self.progress_enc.pack(pady=5)

    def setup_decryption_tab(self):
        tab = self.tabview.tab("Decryption")
        self.btn_select_dec = ctk.CTkButton(tab, text="Select .chaos File", command=self.select_file_dec)
        self.btn_select_dec.pack(pady=10)
        self.lbl_file_dec = ctk.CTkLabel(tab, text="No file selected", text_color="gray")
        self.lbl_file_dec.pack()
        self.entry_pass_dec = ctk.CTkEntry(tab, placeholder_text="Enter Password", show="*", width=200)
        self.entry_pass_dec.pack(pady=5)
        self.btn_run_dec = ctk.CTkButton(tab, text="UNLOCK FILE", fg_color="#27ae60", hover_color="#2ecc71", command=self.run_decryption)
        self.btn_run_dec.pack(pady=15)
        self.progress_dec = ctk.CTkProgressBar(tab, width=400)
        self.progress_dec.set(0)
        self.progress_dec.pack(pady=5)

    def select_file_enc(self):
        path = filedialog.askopenfilename()
        if path:
            self.selected_file_enc = path
            self.lbl_file_enc.configure(text=os.path.basename(path), text_color="white")

    def select_file_dec(self):
        path = filedialog.askopenfilename(filetypes=[("Chaos Files", "*.chaos")])
        if path:
            self.selected_file_dec = path
            self.lbl_file_dec.configure(text=os.path.basename(path), text_color="white")

    def update_progress(self, val):
        self.progress_enc.set(val)
        self.progress_dec.set(val)

    def run_encryption(self):
        password = self.entry_pass_enc.get()
        if not hasattr(self, 'selected_file_enc') or not password: return
        self.log_box.configure(state="normal"); self.log_box.delete("1.0", "end"); self.log_box.configure(state="disabled")
        self.btn_run_enc.configure(state="disabled", text="Encrypting...")
        threading.Thread(target=self.thread_engine, args=("ENC", self.selected_file_enc, password)).start()

    def run_decryption(self):
        password = self.entry_pass_dec.get()
        if not hasattr(self, 'selected_file_dec') or not password: return
        self.log_box.configure(state="normal"); self.log_box.delete("1.0", "end"); self.log_box.configure(state="disabled")
        self.btn_run_dec.configure(state="disabled", text="Decrypting...")
        threading.Thread(target=self.thread_engine, args=("DEC", self.selected_file_dec, password)).start()

    def thread_engine(self, mode, filepath, password):
        try:
            cipher = crypto_engine.HybridCipher(password)
            if mode == "ENC":
                cipher.encrypt_file(filepath, progress_callback=self.update_progress, log_callback=self.log_message)
                messagebox.showinfo("Success", "File Encrypted!")
                self.btn_run_enc.configure(state="normal", text="LOCK FILE")
            else:
                cipher.decrypt_file(filepath, progress_callback=self.update_progress, log_callback=self.log_message)
                messagebox.showinfo("Success", "File Restored!")
                self.btn_run_dec.configure(state="normal", text="UNLOCK FILE")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.btn_run_enc.configure(state="normal")
            self.btn_run_dec.configure(state="normal")

if __name__ == "__main__":
    app = ModernChaosApp()
    app.mainloop()