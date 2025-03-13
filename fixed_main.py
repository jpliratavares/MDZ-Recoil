import json
import tkinter as tk
from tkinter import ttk
from pynput import keyboard
from pynput import mouse
from pynput.mouse import Listener
import mouse_hook
import ctypes
import ctypes.wintypes
import atexit
import threading
import time
import random
from PIL import Image, ImageTk
import os
import webbrowser
import io
import requests

CONFIG_FILE = "config.json"
GIF_FILE = "./assets/background.gif"

class AnimatedGIF:
    def __init__(self, root, gif_file, width=600, height=600):
        self.root = root
        self.gif_file = gif_file
        self.width = width
        self.height = height
        self.frames = []
        self.current_frame = 0
        self.canvas = None
        self.delay = 0
        self.load_frames()
       
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