#!/usr/bin/env python3
"""
GUI File Transfer Application
Cross-platform graphical interface for file transfers
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
import threading
import socket
import os
import time
import webbrowser
import sys
from pathlib import Path
from transfer_server import TransferServer
from transfer_client import TransferClient
from service_discovery import ServiceDiscovery


class FileTransferGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("File Transfer Application")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Server thread reference
        self.server_thread = None
        self.server_running = False
        
        # Service discovery
        self.discovery = None
        self.machine_name = None
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.send_frame = ttk.Frame(self.notebook)
        self.receive_frame = ttk.Frame(self.notebook)
        self.about_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.send_frame, text='Send File')
        self.notebook.add(self.receive_frame, text='Receive Files')
        self.notebook.add(self.about_frame, text='About')
        
        self._create_send_tab()
        self._create_receive_tab()
        self._create_about_tab()
        
        # Status bar at bottom
        self.status_bar = ttk.Label(root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create menu bar
        self._create_menu_bar()

    def _create_menu_bar(self):
        """Create the menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Advanced menu
        advanced_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Advanced", menu=advanced_menu)
        advanced_menu.add_command(
            label="Manual Connection...",
            command=self._open_manual_connection_dialog)

        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(
            label="Preferences...",
            command=self._open_preferences_dialog
        )

    def _open_manual_connection_dialog(self):
        """Dialog for manual IP/port configuration"""
        current_host = self.host_entry.get().strip()
        current_port = self.send_port_entry.get().strip() or "5000"

        host = simpledialog.askstring(
            "Manual Connection",
            "Receiver IP Address:",
            initialvalue=current_host or ""
        )
        if host is None or not host.strip():
            return

        port_str = simpledialog.askstring(
            "Manual Connection",
            "Port:",
            initialvalue=current_port
        )
        if port_str is None:
            return

        try:
            int(port_str)
        except ValueError:
            messagebox.showerror("Error", "Port must be a number.")
            return

        self.host_entry.delete(0, tk.END)
        self.host_entry.insert(0, host.strip())
        self.send_port_entry.delete(0, tk.END)
        self.send_port_entry.insert(0, port_str.strip())

    def _open_preferences_dialog(self):
        """Preferences dialog for machine name, folder, default ports"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Preferences")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.geometry("400x200")

        # Machine name
        frame_name = ttk.Frame(dialog)
        frame_name.pack(fill="x", padx=10, pady=5)
        ttk.Label(frame_name, text="Machine Name:").pack(side=tk.LEFT)
        name_var = tk.StringVar(value=self.machine_name_entry.get())
        name_entry = ttk.Entry(frame_name, textvariable=name_var, width=25)
        name_entry.pack(side=tk.LEFT, padx=5)

        # Receive port
        frame_port = ttk.Frame(dialog)
        frame_port.pack(fill="x", padx=10, pady=5)
        ttk.Label(frame_port, text="Receive Port (default):").pack(side=tk.LEFT)
        recv_port_var = tk.StringVar(value=self.receive_port_entry.get())
        recv_port_entry = ttk.Entry(frame_port, textvariable=recv_port_var, width=8)
        recv_port_entry.pack(side=tk.LEFT, padx=5)

        # Save folder
        frame_dir = ttk.Frame(dialog)
        frame_dir.pack(fill="x", padx=10, pady=5)
        ttk.Label(frame_dir, text="Save Folder:").pack(anchor=tk.W)
        dir_var = tk.StringVar(value=self.output_dir_var.get())
        dir_entry = ttk.Entry(frame_dir, textvariable=dir_var)
        dir_entry.pack(side=tk.LEFT, fill="x", expand=True, padx=5)
        
        def _browse_prefs_dir():
            d = filedialog.askdirectory(title="Select save folder")
            if d:
                dir_var.set(d)
        
        ttk.Button(frame_dir, text="Browse", command=_browse_prefs_dir).pack(side=tk.LEFT)

        # Buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        def _save_prefs():
            # Validate port
            try:
                int(recv_port_var.get().strip())
            except ValueError:
                messagebox.showerror("Error", "Port must be a number.")
                return
            self.machine_name_entry.delete(0, tk.END)
            self.machine_name_entry.insert(0, name_var.get().strip())
            self.receive_port_entry.delete(0, tk.END)
            self.receive_port_entry.insert(0, recv_port_var.get().strip())
            self.output_dir_var.set(dir_var.get().strip())
            dialog.destroy()

        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Save", command=_save_prefs).pack(side=tk.RIGHT, padx=5)

    def _create_send_tab(self):
        """Create the send file tab"""
        # Main frame
        main_frame = ttk.Frame(self.send_frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left side - Machine selection
        left_frame = ttk.LabelFrame(main_frame, text="Receiver Selection")
        left_frame.pack(side=tk.LEFT, fill='both', expand=True, padx=5, pady=5)
        
        # Discovered machines
        ttk.Label(left_frame, text="Discovered Machines:").pack(anchor=tk.W, padx=5, pady=5)
        
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.machines_listbox = tk.Listbox(list_frame, height=8)
        scrollbar = ttk.Scrollbar(list_frame)
        
        self.machines_listbox.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.machines_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.machines_listbox.yview)
        self.machines_listbox.bind('<<ListboxSelect>>', self._on_machine_select)
        
        # Refresh button
        refresh_frame = ttk.Frame(left_frame)
        refresh_frame.pack(fill='x', padx=5, pady=5)
        ttk.Button(refresh_frame, text="Refresh Discovery", command=self._refresh_discovery).pack(side=tk.LEFT)
        
        # Manual connection
        manual_frame = ttk.LabelFrame(left_frame, text="Manual Connection")
        manual_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(manual_frame, text="IP Address:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.host_entry = ttk.Entry(manual_frame, width=15)
        self.host_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(manual_frame, text="Port:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.send_port_entry = ttk.Entry(manual_frame, width=8)
        self.send_port_entry.insert(0, "5000")
        self.send_port_entry.grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
        
        # Right side - File selection and controls
        right_frame = ttk.LabelFrame(main_frame, text="File Transfer")
        right_frame.pack(side=tk.RIGHT, fill='both', expand=True, padx=5, pady=5)
        
        # File selection
        ttk.Label(right_frame, text="File to send:").pack(anchor=tk.W, padx=5, pady=5)
        
        file_frame = ttk.Frame(right_frame)
        file_frame.pack(fill='x', padx=5, pady=5)
        
        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var)
        self.file_entry.pack(side=tk.LEFT, fill='x', expand=True)
        
        ttk.Button(file_frame, text="Browse", command=self._browse_file).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Selected receiver info
        self.selected_receiver_var = tk.StringVar(value="No receiver selected")
        ttk.Label(right_frame, textvariable=self.selected_receiver_var).pack(anchor=tk.W, padx=5, pady=5)
        
        # Send button
        self.send_btn = ttk.Button(right_frame, text="Send File", command=self._send_file)
        self.send_btn.pack(pady=10)
        
        # Progress bar
        self.send_progress = ttk.Progressbar(right_frame, mode='determinate')
        self.send_progress.pack(fill='x', padx=5, pady=5)
        
        # Log area
        log_frame = ttk.LabelFrame(right_frame, text="Transfer Log")
        log_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.send_log = scrolledtext.ScrolledText(log_frame, height=12, state='disabled')
        self.send_log.pack(fill='both', expand=True)

    def _create_receive_tab(self):
        """Create the receive files tab"""
        # Main frame
        main_frame = ttk.Frame(self.receive_frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left side - Configuration
        left_frame = ttk.LabelFrame(main_frame, text="Receiver Configuration")
        left_frame.pack(side=tk.LEFT, fill='both', padx=5, pady=5)
        
        # Machine name
        ttk.Label(left_frame, text="Machine Name:").pack(anchor=tk.W, padx=5, pady=2)
        self.machine_name_entry = ttk.Entry(left_frame)
        self.machine_name_entry.insert(0, socket.gethostname())
        self.machine_name_entry.pack(fill='x', padx=5, pady=2)
        
        # Port
        ttk.Label(left_frame, text="Listen Port:").pack(anchor=tk.W, padx=5, pady=2)
        self.receive_port_entry = ttk.Entry(left_frame)
        self.receive_port_entry.insert(0, "5000")
        self.receive_port_entry.pack(fill='x', padx=5, pady=2)
        
        # Output directory
        ttk.Label(left_frame, text="Save Files To:").pack(anchor=tk.W, padx=5, pady=2)
        
        dir_frame = ttk.Frame(left_frame)
        dir_frame.pack(fill='x', padx=5, pady=2)
        
        self.output_dir_var = tk.StringVar(value=os.path.join(os.getcwd(), "ReceivedFiles"))
        self.dir_entry = ttk.Entry(dir_frame, textvariable=self.output_dir_var)
        self.dir_entry.pack(side=tk.LEFT, fill='x', expand=True)
        
        ttk.Button(dir_frame, text="Browse", command=self._browse_directory).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Server controls
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill='x', padx=5, pady=10)
        
        self.start_server_btn = ttk.Button(btn_frame, text="Start Receiver", command=self._start_server)
        self.start_server_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_server_btn = ttk.Button(btn_frame, text="Stop Receiver", command=self._stop_server, state='disabled')
        self.stop_server_btn.pack(side=tk.LEFT)
        
        # Server status
        self.server_status_label = ttk.Label(left_frame, text="Status: Stopped", foreground="red")
        self.server_status_label.pack(anchor=tk.W, padx=5, pady=5)
        
        # IP address display
        local_ip = self._get_local_ip()
        ip_label = ttk.Label(left_frame, text=f"Your IP: {local_ip}", foreground="blue")
        ip_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # Right side - Log
        right_frame = ttk.LabelFrame(main_frame, text="Receiver Log")
        right_frame.pack(side=tk.RIGHT, fill='both', expand=True, padx=5, pady=5)
        
        self.receive_log = scrolledtext.ScrolledText(right_frame, height=20, state='disabled')
        self.receive_log.pack(fill='both', expand=True)

    def _create_about_tab(self):
        """Create the About tab with scrollbar"""
        # Main container with scrollbar
        main_container = ttk.Frame(self.about_frame)
        main_container.pack(fill='both', expand=True)
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(main_container, bg='white')
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Configure the canvas
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Update scroll region when the frame changes size
        def _configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        scrollable_frame.bind("<Configure>", _configure_scroll_region)
        
        # Application header
        header_frame = ttk.Frame(scrollable_frame)
        header_frame.pack(fill='x', pady=(0, 20), padx=20)
        
        # Application title with larger font
        title_label = ttk.Label(
            header_frame, 
            text="File Transfer Application", 
            font=('Arial', 16, 'bold'),
            foreground='#2c3e50'
        )
        title_label.pack(pady=(0, 10))
        
        # Version info with beta badge
        version_frame = ttk.Frame(header_frame)
        version_frame.pack()
        
        version_label = ttk.Label(
            version_frame,
            text="Version 0.1.2",
            font=('Arial', 12, 'bold')
        )
        version_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Beta testing badge
        beta_label = ttk.Label(
            version_frame,
            text="BETA TESTING",
            font=('Arial', 8, 'bold'),
            foreground='white',
            background='#e74c3c',
            padding=(6, 2)
        )
        beta_label.pack(side=tk.LEFT)
        
        # Separator
        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill='x', pady=20, padx=20)
        
        # Features section
        features_frame = ttk.LabelFrame(scrollable_frame, text="Features")
        features_frame.pack(fill='x', pady=(0, 20), padx=20)
        
        features_text = """
• Cross-platform compatibility (Windows, macOS, Linux)
• No external dependencies - Pure Python
• Automatic network discovery
• Secure local file transfers
• Real-time progress monitoring
• User-friendly graphical interface
• Support for large file transfers
• Easy to use and setup
• No installation required
• Open source project
• Regular updates and improvements
• Community driven development
"""
        features_label = ttk.Label(
            features_frame,
            text=features_text,
            justify=tk.LEFT,
            font=('Arial', 9)
        )
        features_label.pack(padx=10, pady=10, anchor=tk.W)
        
        # Author information
        author_frame = ttk.LabelFrame(scrollable_frame, text="Developer Information")
        author_frame.pack(fill='x', pady=(0, 20), padx=20)
        
        author_text = """
Developed by: Scorpionziky

This application was created to provide a simple, reliable 
file transfer solution for local networks without requiring 
any additional software installations.

The project aims to make file sharing between computers on 
the same network as easy as possible, while maintaining 
security and performance.

If you encounter any issues or have suggestions for 
improvements, please don't hesitate to contact me using 
the methods below.
"""
        author_label = ttk.Label(
            author_frame,
            text=author_text,
            justify=tk.LEFT,
            font=('Arial', 9)
        )
        author_label.pack(padx=10, pady=10, anchor=tk.W)
        
        # Contact methods
        contact_frame = ttk.LabelFrame(scrollable_frame, text="Contact & Support")
        contact_frame.pack(fill='x', pady=(0, 20), padx=20)
        
        # Email
        email_frame = ttk.Frame(contact_frame)
        email_frame.pack(fill='x', padx=10, pady=5)
        ttk.Label(email_frame, text="Email:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        email_link = ttk.Label(
            email_frame, 
            text="scorpionziky89@gmail.com",
            font=('Arial', 9),
            foreground='#3498db',
            cursor='hand2'
        )
        email_link.pack(side=tk.LEFT, padx=(5, 0))
        email_link.bind('<Button-1>', lambda e: self._open_email_client())
        
        # GitHub
        github_frame = ttk.Frame(contact_frame)
        github_frame.pack(fill='x', padx=10, pady=5)
        ttk.Label(github_frame, text="GitHub:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        github_link = ttk.Label(
            github_frame, 
            text="https://github.com/scorpionziky",
            font=('Arial', 9),
            foreground='#3498db',
            cursor='hand2'
        )
        github_link.pack(side=tk.LEFT, padx=(5, 0))
        github_link.bind('<Button-1>', lambda e: self._open_github())
        
        # Website
      #  website_frame = ttk.Frame(contact_frame)
      #  website_frame.pack(fill='x', padx=10, pady=5)
      #  ttk.Label(website_frame, text="Website:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
      #  website_link = ttk.Label(
      #      website_frame, 
      #      text="https://scorp-dev.com",
      #      font=('Arial', 9),
      #      foreground='#3498db',
      #      cursor='hand2'
      #  )
      #  website_link.pack(side=tk.LEFT, padx=(5, 0))
      #  website_link.bind('<Button-1>', lambda e: self._open_website()) 
        
        # Technical info
        tech_frame = ttk.LabelFrame(scrollable_frame, text="Technical Information")
        tech_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        tech_text = f"""
Python Version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}
Platform: {sys.platform}
Hostname: {socket.gethostname()}
Local IP: {self._get_local_ip()}
Application Directory: {os.path.dirname(os.path.abspath(__file__))}
"""
        tech_label = ttk.Label(
            tech_frame,
            text=tech_text,
            justify=tk.LEFT,
            font=('Arial', 8),
            foreground='#7f8c8d'
        )
        tech_label.pack(padx=10, pady=10, anchor=tk.W)
        
        # Additional information
        info_frame = ttk.LabelFrame(scrollable_frame, text="Additional Information")
        info_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        info_text = """
This application is built using Python's standard library only, 
making it lightweight and portable. It uses TCP sockets for 
reliable file transfers and UDP multicast for service discovery.

The application is designed for use on trusted local networks 
only. For security reasons, it does not include encryption or 
authentication features.

If you enjoy using this application, consider starring the 
project on GitHub or contributing to its development!
"""
        info_label = ttk.Label(
            info_frame,
            text=info_text,
            justify=tk.LEFT,
            font=('Arial', 8),
            foreground='#7f8c8d'
        )
        info_label.pack(padx=10, pady=10, anchor=tk.W)
        
        # Copyright notice
        copyright_label = ttk.Label(
            scrollable_frame,
            text="© 2025 Scorpionziky All rights reserved.",
            font=('Arial', 8),
            foreground='#95a5a6'
        )
        copyright_label.pack(pady=(20, 30))
        
        # Configure mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # For Linux
        def _on_scroll_up(event):
            canvas.yview_scroll(-1, "units")
        
        def _on_scroll_down(event):
            canvas.yview_scroll(1, "units")
        
        canvas.bind_all("<Button-4>", _on_scroll_up)
        canvas.bind_all("<Button-5>", _on_scroll_down)

    def _open_email_client(self):
        """Open default email client"""
        try:
            webbrowser.open("mailto:scorpionziky89@gmail.com")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open email client: {e}")

    def _open_github(self):
        """Open GitHub page"""
        try:
            webbrowser.open("https://github.com/scorpionziky")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open GitHub: {e}")

   # def _open_website(self):
   #     """Open website"""
   #     try:
   #         webbrowser.open("https://scorp-dev.com")
   #    except Exception as e:
   #         messagebox.showerror("Error", f"Could not open website: {e}")

    def _refresh_discovery(self):
        """Force refresh of discovered machines list"""
        if not self.discovery:
            messagebox.showinfo(
                "Discovery",
                "Service discovery is only active on receivers.\n"
                "Start the receiver on at least one machine to see it here."
            )
            return
        self._update_machines_list()
        self._log_send("Machine list updated.")

    def _on_machine_select(self, event):
        """Handle machine selection from listbox"""
        selection = self.machines_listbox.curselection()
        if selection:
            machine_name = self.machines_listbox.get(selection[0])
            if self.discovery:
                peers = self.discovery.get_peers()
                peer_info = peers.get(machine_name)
                if peer_info:
                    self.host_entry.delete(0, tk.END)
                    self.host_entry.insert(0, peer_info['ip'])
                    self.send_port_entry.delete(0, tk.END)
                    self.send_port_entry.insert(0, str(peer_info['port']))
                    self.selected_receiver_var.set(f"Selected: {machine_name} ({peer_info['ip']}:{peer_info['port']})")

    def _update_machines_list(self):
        """Update the list of discovered machines"""
        if not self.discovery:
            return
            
        peers = self.discovery.get_peers()
        
        # Update listbox
        self.machines_listbox.delete(0, tk.END)
        for name in sorted(peers.keys()):
            self.machines_listbox.insert(tk.END, name)

    def _browse_file(self):
        """Browse for file to send"""
        filename = filedialog.askopenfilename(title="Select file to send")
        if filename:
            self.file_path_var.set(filename)

    def _browse_directory(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(title="Select directory for received files")
        if directory:
            self.output_dir_var.set(directory)

    def _log_send(self, message):
        """Add message to send log"""
        self.send_log.config(state='normal')
        timestamp = time.strftime("%H:%M:%S")
        self.send_log.insert(tk.END, f"[{timestamp}] {message}\n")
        self.send_log.see(tk.END)
        self.send_log.config(state='disabled')
        self.status_bar.config(text=f"Send: {message}")

    def _log_receive(self, message):
        """Add message to receive log"""
        self.receive_log.config(state='normal')
        timestamp = time.strftime("%H:%M:%S")
        self.receive_log.insert(tk.END, f"[{timestamp}] {message}\n")
        self.receive_log.see(tk.END)
        self.receive_log.config(state='disabled')
        self.status_bar.config(text=f"Receive: {message}")

    def _send_file(self):
        """Send file in separate thread"""
        host = self.host_entry.get().strip()
        port_str = self.send_port_entry.get().strip()
        filepath = self.file_path_var.get()
        
        # Validation
        if not host:
            messagebox.showerror("Error", "Please enter receiver IP address")
            return
            
        try:
            port = int(port_str)
        except ValueError:
            messagebox.showerror("Error", "Port must be a number")
            return
            
        if not filepath or not os.path.exists(filepath):
            messagebox.showerror("Error", "Please select a valid file to send")
            return
            
        # Disable button during transfer
        self.send_btn.config(state='disabled')
        self.send_progress['value'] = 0
        self._log_send(f"Starting transfer to {host}:{port}...")
        
        # Run transfer in thread
        thread = threading.Thread(target=self._send_file_thread, args=(host, port, filepath))
        thread.daemon = True
        thread.start()

    def _send_file_thread(self, host, port, filepath):
        """Thread function to send file"""
        try:
            client = TransferClient(host, port)
            self._log_send(f"Connecting to {host}:{port}...")
            
            # We'll use the existing TransferClient but update progress
            filepath_obj = Path(filepath)
            filesize = filepath_obj.stat().st_size
            
            # Create a custom progress callback
            def progress_callback(sent, total):
                progress = (sent / total) * 100
                self.root.after(0, lambda: self.send_progress.config(value=progress))
                if sent == total:
                    self.root.after(0, lambda: self._log_send("Transfer complete!"))
            
            # For now, we'll use the standard client and simulate progress
            # In a real implementation, you'd modify TransferClient to accept a progress callback
            client.send_file(filepath)
            
            self.root.after(0, lambda: self._log_send("✓ File sent successfully!"))
            self.root.after(0, lambda: self.send_progress.config(value=100))
            
        except Exception as e:
            self.root.after(0, lambda: self._log_send(f"Error: {e}"))
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.root.after(0, lambda: self.send_btn.config(state='normal'))

    def _start_server(self):
        """Start the receiver server"""
        port_str = self.receive_port_entry.get().strip()
        output_dir = self.output_dir_var.get()
        machine_name = self.machine_name_entry.get().strip()
        
        if not machine_name:
            messagebox.showerror("Error", "Please enter a machine name")
            return
        
        try:
            port = int(port_str)
        except ValueError:
            messagebox.showerror("Error", "Port must be a number")
            return
            
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
            
        self.machine_name = machine_name
        self.server_running = True
        self.start_server_btn.config(state='disabled')
        self.stop_server_btn.config(state='normal')
        self.machine_name_entry.config(state='readonly')
        self.receive_port_entry.config(state='readonly')
        self.server_status_label.config(text="Status: Running", foreground="green")
        
        self._log_receive(f"Starting server on port {port}...")
        self._log_receive(f"Broadcasting as '{machine_name}'...")
        self._log_receive(f"Saving files to: {output_dir}")
        
        # Start service discovery
        try:
            self.discovery = ServiceDiscovery(
                machine_name, 
                port, 
                callback=lambda: self.root.after(0, self._update_machines_list)
            )
            self.discovery.start()
            self._log_receive("Service discovery started")
        except Exception as e:
            self._log_receive(f"Service discovery error: {e}")
        
        # Start server in thread
        self.server_thread = threading.Thread(target=self._run_server, args=(port, output_dir))
        self.server_thread.daemon = True
        self.server_thread.start()

    def _stop_server(self):
        """Stop the receiver server"""
        self.server_running = False
        self.start_server_btn.config(state='normal')
        self.stop_server_btn.config(state='disabled')
        self.machine_name_entry.config(state='normal')
        self.receive_port_entry.config(state='normal')
        self.server_status_label.config(text="Status: Stopped", foreground="red")
        self._log_receive("Server stopped")
        
        # Stop service discovery
        if self.discovery:
            self.discovery.stop()
            self.discovery = None
            self.machines_listbox.delete(0, tk.END)

    def _run_server(self, port, output_dir):
        """Run server in thread"""
        try:
            server = TransferServer(port=port, output_dir=output_dir)
            
            # Modify the server to work with our GUI
            original_receive_file = server._receive_file
            
            def gui_receive_file(conn):
                try:
                    # Get client address
                    peer_addr = conn.getpeername()
                    self.root.after(0, lambda: self._log_receive(f"Connection from {peer_addr[0]}:{peer_addr[1]}"))
                    
                    # Call original method
                    result = original_receive_file(conn)
                    
                    if result:
                        filename, filesize = result
                        self.root.after(0, lambda: self._log_receive(f"✓ Received: {filename} ({filesize} bytes)"))
                    
                except Exception as e:
                    self.root.after(0, lambda: self._log_receive(f"Error receiving file: {e}"))
            
            server._receive_file = gui_receive_file
            server.start()
            
        except Exception as e:
            self.root.after(0, lambda: self._log_receive(f"Server error: {e}"))
            self.root.after(0, lambda: messagebox.showerror("Server Error", str(e)))
        finally:
            self.root.after(0, self._stop_server)

    def _get_local_ip(self):
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"


def main():
    root = tk.Tk()
    app = FileTransferGUI(root)
    
    def on_closing():
        if app.server_running:
            app._stop_server()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == '__main__':
    main()