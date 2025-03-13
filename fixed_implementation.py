# Fixed implementation of the Discord contact functionality

def add_discord_contact(self, canvas):
    # Create frame for discord contact info
    contact_frame = tk.Frame(canvas, bg="#2d2d2d", padx=-150, pady=15, bd=1, relief="flat")
    # Position in bottom right corner
    canvas.create_window(600, 470, anchor="se", window=contact_frame)
    
    # Discord logo (simple text representation)
    discord_logo = tk.Label(contact_frame, text="ﾠ", font=("Arial", 10, "bold"), 
                           bg="#2d2d2d", fg="#7289DA")
    discord_logo.pack(side="left", padx=(0, 2))
    
    # Create Discord icon with custom Unicode character
    discord_icon = tk.Label(contact_frame, text="󰙯", font=("Segoe UI Symbol", 12), 
                           bg="#2d2d2d", fg="#7289DA")
    discord_icon.pack(side="left", padx=(0, 2))
    
    # Discord text
    discord_text = tk.Label(contact_frame, text="https://discord.gg/gKTWD53MeJ", 
                          bg="#2d2d2d", fg="white", font=("Arial", 8))
    discord_text.pack(side="left")
    # Make the text clickable - this line was missing
    discord_text.bind("<Button-1>", self.open_discord_link)

def open_discord_link(self, event):
    # Only the URL opening should be in this function, binding doesn't belong here
    webbrowser.open("https://discord.gg/gKTWD53MeJ")