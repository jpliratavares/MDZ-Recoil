# Discord Link Fix Solution

To make the Discord link clickable, three changes are needed in the `main.py` file:

## 1. Add `self` parameter to the `open_discord_link` function

Change:
```python
def open_discord_link(event):
    webbrowser.open("https://discord.gg/your-server-link")
```

To:
```python
def open_discord_link(self, event):
    webbrowser.open("https://discord.gg/gKTWD53MeJ")
```

## 2. Update the Discord URL

Change the URL from `"https://discord.gg/your-server-link"` to `"https://discord.gg/gKTWD53MeJ"`

## 3. Add binding statement to make the text clickable

Add this line after creating the Discord text label:
```python
discord_text.bind("<Button-1>", self.open_discord_link)
```

## Complete Fixed Implementation

```python
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
    # Make the text clickable
    discord_text.bind("<Button-1>", self.open_discord_link)

def open_discord_link(self, event):
    webbrowser.open("https://discord.gg/gKTWD53MeJ")
```

### Explanation of Changes

1. Added `self` parameter to the `open_discord_link` method because it's a method within a class and needs access to the instance
2. Updated the Discord URL to the correct one
3. Added the binding statement to make the text clickable, which was missing in the original implementation

These changes will allow users to click on the Discord link and be taken to the correct Discord server.