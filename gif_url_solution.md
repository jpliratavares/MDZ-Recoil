# GIF URL Loading Solution

The problem is that the application fails when trying to load a GIF from a URL with the error message "Arquivo https://i.imgur.com/S19vxOB.gif não encontrado!" because it's treating the URL as a local file path.

## Solution Implementation

I've already added the required imports to main.py:
```python
import io
import requests
```

Now we need to modify the `load_frames` method in the `AnimatedGIF` class to handle URLs. The modified method should:

1. Check if the file path starts with "http://" or "https://"
2. If it's a URL, use requests to download the content and create an in-memory file object
3. If it's a local path, use the existing code

Here's how the `load_frames` method should be modified:

```python
def load_frames(self):
    # Check if it's a URL (starts with http:// or https://)
    if self.gif_file.startswith('http://') or self.gif_file.startswith('https://'):
        try:
            response = requests.get(self.gif_file)
            if response.status_code == 200:
                # Create an in-memory file-like object
                image_data = io.BytesIO(response.content)
                gif = Image.open(image_data)
            else:
                print(f"Failed to download {self.gif_file}, status code: {response.status_code}")
                return
        except Exception as e:
            print(f"Error downloading {self.gif_file}: {str(e)}")
            return
    else:
        # Handle local file
        if not os.path.exists(self.gif_file):
            print(f"Arquivo {self.gif_file} não encontrado!")
            return
        
        gif = Image.open(self.gif_file)
    
    # Rest of the method remains the same
    try:
        while True:
            resized_frame = ImageTk.PhotoImage(
                gif.resize((self.width, self.height), Image.LANCZOS)
            )
            self.frames.append(resized_frame)
            gif.seek(gif.tell() + 1)
           
    except EOFError:
        pass
    
    try:
        self.delay = gif.info['duration']
    except KeyError:
        self.delay = 100
```

This implementation will allow the application to load GIFs from URLs like "https://i.imgur.com/S19vxOB.gif" in addition to local files.