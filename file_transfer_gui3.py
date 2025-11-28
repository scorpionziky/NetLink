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
Developed by: Scorp

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
        text="scorp@example.com",  # Replace with actual email
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
        text="https://github.com/scorp",  # Replace with actual GitHub URL
        font=('Arial', 9),
        foreground='#3498db',
        cursor='hand2'
    )
    github_link.pack(side=tk.LEFT, padx=(5, 0))
    github_link.bind('<Button-1>', lambda e: self._open_github())
    
    # Website
    website_frame = ttk.Frame(contact_frame)
    website_frame.pack(fill='x', padx=10, pady=5)
    ttk.Label(website_frame, text="Website:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
    website_link = ttk.Label(
        website_frame, 
        text="https://scorp-dev.com",  # Replace with actual website
        font=('Arial', 9),
        foreground='#3498db',
        cursor='hand2'
    )
    website_link.pack(side=tk.LEFT, padx=(5, 0))
    website_link.bind('<Button-1>', lambda e: self._open_website())
    
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
        text="© 2024 Scorp. All rights reserved.",
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