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
import sys, os
import shutil

import ctypes

# Definir constantes para simular movimentação do mouse
INPUT_MOUSE = 0
MOUSEEVENTF_MOVE = 0x0001

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]

class INPUT(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("mi", MOUSEINPUT)]

def send_mouse_move(dx, dy):
    """Envia movimento do mouse usando ctypes"""
    input_structure = INPUT()
    input_structure.type = INPUT_MOUSE
    input_structure.mi = MOUSEINPUT(dx, dy, 0, MOUSEEVENTF_MOVE, 0, None)
    
    # Envia o movimento do mouse para o sistema operacional
    ctypes.windll.user32.SendInput(1, ctypes.byref(input_structure), ctypes.sizeof(input_structure))


def get_config_dir():
    """Retorna o caminho do diretório de configuração do programa."""
    if sys.platform == "win32":
        return os.path.join(os.getenv("APPDATA"), "MDZRecoil")
    else:
        return os.path.join(os.path.expanduser("~"), ".config", "MDZRecoil")

def ensure_background_exists():
    """Garante que o background.gif esteja salvo no diretório de configuração."""
    config_dir = get_config_dir()
    os.makedirs(config_dir, exist_ok=True)  # Cria o diretório se não existir

    bg_path = os.path.join(config_dir, "background.gif")

    if not os.path.exists(bg_path):  # Copia apenas se ainda não existir
        try:
            shutil.copy(resource_path("background.gif"), bg_path)
        except Exception as e:
            print(f"Erro ao copiar background.gif: {e}")

    return bg_path

def resource_path(relative_path):
    """Retorna o caminho correto do arquivo, dentro ou fora do executável."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)  # Caminho dentro do executável
    return os.path.join(os.getcwd(), relative_path)  # Caminho normal durante desenvolvimento

GIF_FILE = ensure_background_exists()
CONFIG_FILE = "config.json"



class FlameEffect:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.flames = []
        self.create_flames()
        
    def create_flames(self):
        flame_count = 50
        for _ in range(flame_count):
            side = random.choice(['top', 'bottom', 'left', 'right'])
            if side == 'top':
                x = random.randint(0, self.width)
                y = 0
            elif side == 'bottom':
                x = random.randint(0, self.width)
                y = self.height
            elif side == 'left':
                x = 0
                y = random.randint(0, self.height)
            else:
                x = self.width
                y = random.randint(0, self.height)
                
            flame = {
                'x': x,
                'y': y,
                'size': random.randint(10, 20),
                'speed': random.uniform(1, 3),
                'opacity': random.uniform(0.3, 0.8),
                'id': None
            }
            self.flames.append(flame)
            
    def animate_flames(self):
        for flame in self.flames:
            if flame['id'] is not None:
                self.canvas.delete(flame['id'])
                
            r = int(255 * (1 - flame['opacity']))
            flame['id'] = self.canvas.create_oval(
                flame['x'] - flame['size'],
                flame['y'] - flame['size'],
                flame['x'] + flame['size'],
                flame['y'] + flame['size'],
                fill=f'#{r:02x}0000',
                outline='',
                stipple='gray50'
            )
            
            flame['y'] -= flame['speed']
            flame['opacity'] -= 0.02
            
            if flame['opacity'] <= 0:
                flame['opacity'] = random.uniform(0.3, 0.8)
                side = random.choice(['top', 'bottom', 'left', 'right'])
                if side == 'top':
                    flame['x'] = random.randint(0, self.width)
                    flame['y'] = self.height
                elif side == 'bottom':
                    flame['x'] = random.randint(0, self.width)
                    flame['y'] = 0
                elif side == 'left':
                    flame['x'] = self.width
                    flame['y'] = random.randint(0, self.height)
                else:
                    flame['x'] = 0
                    flame['y'] = random.randint(0, self.height)
                    
        self.canvas.after(50, self.animate_flames)

def load_config():
    default_config = {
        "horizontal_recoil": 0,
        "vertical_recoil": 0,
        "activation_key": "F1",
        "toggle_key": "F2",
        "mouse_activation": "left_click",
        "background_file": ensure_background_exists(),
        "rapid_fire_enabled": False,
        "rapid_fire_key": "F3",
        "rapid_fire_interval": 15,
        "rapid_fire_mouse_button": "left_click",
        "tbag_enabled": False,
        "tbag_key": "F4",
        "tbag_interval": 50,
        "tbag_button": "ctrl",
        "hide_toggle_key": "F6",  # Adicionando a tecla para esconder/mostrar a janela
    }
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        config = default_config
   
    for key in default_config:
        if key not in config:
            config[key] = default_config[key]
   
    save_config(config)
    return config

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

config = load_config()

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
   
    def setup_canvas(self, parent):
        self.canvas = tk.Canvas(parent, width=self.width, height=self.height,
                                highlightthickness=0)
        self.canvas.pack(expand=True, fill="both")
       
        if self.frames:
            self.image_id = self.canvas.create_image(
                self.width // 2, self.height // 2,
                image=self.frames[0]
            )
            self.update_frame()
       
        return self.canvas
   
    def update_frame(self):
        if not self.frames:
            return
       
        self.canvas.itemconfig(self.image_id, image=self.frames[self.current_frame])
        self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.root.after(self.delay, self.update_frame)

class RecoilControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MDZ Recoil")
        self.root.geometry("600x480")
        self.root.minsize(600, 480)
        self.root.attributes("-topmost", True)
        
        # Create a canvas for the flame effect
        self.flame_canvas = tk.Canvas(root, width=600, height=480, 
                                    bg='black', highlightthickness=0)
        self.flame_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Initialize flame effect
        self.flame_effect = FlameEffect(self.flame_canvas, 600, 480)
        self.flame_effect.animate_flames()
        
        # Create a frame for the main content with some padding for the flames
        self.main_frame = tk.Frame(root, bg='#1c1c1c')
        self.main_frame.place(relx=0.02, rely=0.02, 
                            relwidth=0.96, relheight=0.96)
        
        self.running = False
        self.shooting = False
        self.rapid_fire_active = False
        self.tbag_active = False
        self.tbag_thread = None
        
        # Flag para controlar o estado de visibilidade da janela
        self.window_hidden = False
    
        self.mouse_controller = mouse_hook.MockMouseController()
        self.keyboard_controller = keyboard.Controller()
        self.listener_thread = None
        self.rapid_fire_thread = None
   
        self.x = 0
        self.y = 0
    
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press, on_release=self.on_key_release)
        self.keyboard_listener.start()
        self.mouse_listener = Listener(on_click=self.on_mouse_click)
        self.mouse_listener.start()
    
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.style.configure('TCombobox',
                             fieldbackground='#1c1c1c',
                             background='#8b0000',
                             foreground='white',
                             arrowcolor='white',
                             selectbackground='#aa0000',
                             selectforeground='white')
    
        self.style.map('TCombobox',
                       fieldbackground=[('readonly', '#1c1c1c')],
                       selectbackground=[('readonly', '#aa0000')],
                       background=[('readonly', '#8b0000'), ('active', '#9c0000')],
                       foreground=[('readonly', 'white')],
                       selectforeground=[('readonly', 'white')])
    
        self.root.option_add('*TCombobox*Listbox.background', '#661a1a')
        self.root.option_add('*TCombobox*Listbox.foreground', 'white')
        self.root.option_add('*TCombobox*Listbox.selectBackground', '#aa0000')
        self.root.option_add('*TCombobox*Listbox.selectForeground', 'white')
    
        self.animated_bg = AnimatedGIF(root, config["background_file"])
    
        self.setup_custom_titlebar()
        self.show_welcome_screen()

    def show_welcome_screen(self):
        self.clear_screen()
        
        canvas = self.animated_bg.setup_canvas(self.root)
        frame = tk.Frame(canvas, bg="#1c1c1c")
        canvas_window = canvas.create_window(300, 220, window=frame)
        
        logo_label = tk.Label(frame, text="MDZ RECOIL", fg="#ff0000", bg="#1c1c1c", 
                            font=("Impact", 36, "bold"))
        logo_label.pack(pady=20)
        
        welcome_label = tk.Label(frame, text="Bem-vindo ao MDZ Recoil", fg="white", bg="#1c1c1c", 
                                font=("Arial", 16, "bold"))
        welcome_label.pack(pady=15)
        
        description_text = """
        Software de controle de recoil para jogos FPS.
        Configure o movimento vertical e horizontal,
        ative/desative com teclas de atalho e personalize
        as configurações avançadas conforme necessário.
        """
        description_label = tk.Label(frame, text=description_text, justify="center", 
                                    fg="lightgray", bg="#1c1c1c", wraplength=400,
                                    font=("Arial", 10))
        description_label.pack(pady=20)
        
        enter_button = tk.Button(frame, text="Iniciar Configuração", command=self.show_movement_screen,
                                bg="#8b0000", fg="white", font=("Arial", 14, "bold"),
                                relief="flat", padx=20, pady=10, activebackground="#aa0000")
        enter_button.pack(pady=30)
        
        version_label = tk.Label(frame, text="v1.1.0", fg="#666666", bg="#1c1c1c", 
                                font=("Arial", 8))
        version_label.pack(pady=15)
        
        # Add Discord contact in bottom right
        self.add_discord_contact(canvas)
   
    def setup_custom_titlebar(self):
        self.titlebar = tk.Frame(self.root, bg="#8b0000", relief="flat", height=40)
        self.titlebar.pack(fill="x")
       
        self.titlebar.bind('<Button-1>', self.get_pos)
        self.titlebar.bind('<B1-Motion>', self.move_window)
       
        self.title_label = tk.Label(self.titlebar, text="MDZ Recoil", fg="white", bg="#8b0000", font=("Arial", 12, "bold"))
        self.title_label.pack(side="left", padx=10)
        self.title_label.bind('<Button-1>', self.get_pos)
        self.title_label.bind('<B1-Motion>', self.move_window)
       
        button_container = tk.Frame(self.titlebar, bg="#8b0000")
        button_container.pack(side="right", padx=5)
       
        self.minimize_button = tk.Button(button_container, text="─", bg="#555555", fg="white",
                                         command=self.minimize_window, font=("Arial", 10, "bold"),
                                         relief="flat", width=4, height=1, bd=0,
                                         activebackground="#777777")
        self.minimize_button.pack(side="left", padx=2, pady=2)
       
        self.close_button = tk.Button(button_container, text="✖", bg="#c0392b", fg="white",
                                      command=self.root.destroy, font=("Arial", 10, "bold"),
                                      relief="flat", width=4, height=1, bd=0,
                                      activebackground="#e74c3c")
        self.close_button.pack(side="left", padx=2, pady=2)
    
    # New method to add Discord contact to bottom right
    def add_discord_contact(self, canvas):
        # Create frame for discord contact info
        contact_frame = tk.Frame(canvas, bg="#2d2d2d", padx=15, pady=15, bd=1, relief="flat")
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
    def open_discord_link(self, event):
        
        webbrowser.open("https://discord.gg/gKTWD53MeJ")
        
        discord_text.bind("<Button-1>", open_discord_link)
    def get_pos(self, event):
        self.x = event.x
        self.y = event.y
   
    def move_window(self, event):
        x = self.root.winfo_pointerx() - self.x
        y = self.root.winfo_pointery() - self.y
        self.root.geometry(f"+{x}+{y}")
   
    # Nova função para alternar a visibilidade da janela com F6
    def toggle_window_visibility(self):
        if self.window_hidden:
            self.restore_window()
        else:
            self.minimize_window()
        self.window_hidden = not self.window_hidden
   
    def minimize_window(self):
        self.root.withdraw()
        self.create_taskbar_icon()
   
    def create_taskbar_icon(self):
        self.icon_window = tk.Toplevel(self.root)
        self.icon_window.title("MDZ Recoil")
        self.icon_window.geometry("1x1+0+0")
        self.icon_window.overrideredirect(False)
        self.icon_window.attributes("-toolwindow", True)
       
        restore_button = tk.Button(self.icon_window, text="Restore", command=self.restore_window)
        restore_button.pack()
       
        self.icon_window.protocol("WM_DELETE_WINDOW", self.root.destroy)
   
    def restore_window(self):
        self.root.deiconify()
        if hasattr(self, 'icon_window'):
            self.icon_window.destroy()
   
    def on_key_press(self, key):
        try:
            key_char = key.char
        except AttributeError:
            key_char = str(key).replace("Key.", "")
       
        if key_char.lower() == config["toggle_key"].lower():
            self.toggle_macro()
        
        if config["rapid_fire_enabled"] and key_char.lower() == config["rapid_fire_key"].lower():
            self.rapid_fire_active = True
            if not self.rapid_fire_thread or not self.rapid_fire_thread.is_alive():
                self.rapid_fire_thread = threading.Thread(target=self.run_rapid_fire, daemon=True)
                self.rapid_fire_thread.start()
        
        if config["tbag_enabled"] and key_char.lower() == config["tbag_key"].lower():
            self.tbag_active = True
            if not self.tbag_thread or not self.tbag_thread.is_alive():
                self.tbag_thread = threading.Thread(target=self.run_tbag, daemon=True)
                self.tbag_thread.start()
        
        # Nova verificação para a tecla F6 para mostrar/esconder a janela
        if key_char.lower() == config["hide_toggle_key"].lower():
            self.toggle_window_visibility()
   
    def on_key_release(self, key):
        try:
            key_char = key.char
        except AttributeError:
            key_char = str(key).replace("Key.", "")
            
        # Deactivate rapid fire when the designated key is released
        if key_char.lower() == config["rapid_fire_key"].lower():
            self.rapid_fire_active = False
            
        # Desativar T-bag quando a tecla designada for solta
        if key_char.lower() == config["tbag_key"].lower():
            self.tbag_active = False
   
    def on_mouse_click(self, x, y, button, pressed):
        if self.running and ((config["mouse_activation"] == "left_click" and button == mouse_hook.MockMouse.Button.left) or
                             (config["mouse_activation"] == "right_click" and button == mouse_hook.MockMouse.Button.right) or
                             (config["mouse_activation"] == "both" and button in [mouse_hook.MockMouse.Button.left, mouse_hook.MockMouse.Button.right])):
            self.shooting = pressed
   
    def toggle_macro(self):
        self.running = not self.running
        self.update_status_label()
        if self.running:
            if not self.listener_thread or not self.listener_thread.is_alive():
                self.listener_thread = threading.Thread(target=self.run_macro, daemon=True)
                self.listener_thread.start()
   
    def run_macro(self):
        while self.running:
            if self.shooting:
                self.apply_recoil()
            time.sleep(0.02)
    
    def run_rapid_fire(self):
        while self.rapid_fire_active:
            # Simulate mouse click based on configuration
            if config["rapid_fire_mouse_button"] == "left_click":
                self.mouse_controller.click(mouse.Button.left)
            elif config["rapid_fire_mouse_button"] == "right_click":
                self.mouse_controller.click(mouse.Button.right)
            elif config["rapid_fire_mouse_button"] == "both":
                self.mouse_controller.click(mouse.Button.left)
                time.sleep(0.001)  # Small delay between clicks
                self.mouse_controller.click(mouse.Button.right)
            
            # Adiciona um pequeno delay para evitar loops muito rápidos
            time.sleep(config["rapid_fire_interval"] / 1000)  # Convert ms to seconds
    
    def run_tbag(self):
        """Função para executar o t-bag (agachar repetidamente)"""
        tbag_key = config["tbag_button"]
        # Converte para o formato que o pynput espera
        if len(tbag_key) == 1:  # Caractere único
            key_obj = tbag_key
        else:  # Teclas especiais
            try:
                key_obj = getattr(keyboard.Key, tbag_key)
            except AttributeError:
                # Se não for uma tecla especial, usa como está
                key_obj = tbag_key
        
        while self.tbag_active:
            # Pressiona a tecla de agachar
            self.keyboard_controller.press(key_obj)
            time.sleep(config["tbag_interval"] / 2000)  # Metade do intervalo para pressionar
            
            # Solta a tecla de agachar
            self.keyboard_controller.release(key_obj)
            time.sleep(config["tbag_interval"] / 2000)  # Metade do intervalo para soltar
   
    def apply_recoil(self):
        horizontal = config["horizontal_recoil"]
        vertical = config["vertical_recoil"]
        jitter_x = random.uniform(-1, 1)
        jitter_y = random.uniform(-1, 1)
    
        dx = int(jitter_x + horizontal)
        dy = int(jitter_y + vertical)
    
        send_mouse_move(dx, dy)  # Agora usando ctypes

   
    def save_movement_settings(self):
        config["vertical_recoil"] = self.vertical_scale.get()
        config["horizontal_recoil"] = self.horizontal_scale.get()
        save_config(config)
   
    def save_config_settings(self):
        # Salva as configurações básicas que sempre estarão disponíveis
        if hasattr(self, 'activation_key_var'):
            config["activation_key"] = self.activation_key_var.get()
        if hasattr(self, 'toggle_key_var'):
            config["toggle_key"] = self.toggle_key_var.get()
        if hasattr(self, 'mouse_activation_var'):
            config["mouse_activation"] = self.mouse_activation_var.get()
        if hasattr(self, 'bg_file_var'):
            config["background_file"] = self.bg_file_var.get()
        if hasattr(self, 'hide_toggle_key_var'):
            config["hide_toggle_key"] = self.hide_toggle_key_var.get()
        
        # Salva as configurações do Rapid Fire
        if hasattr(self, 'rapid_fire_enabled_var'):
            config["rapid_fire_enabled"] = self.rapid_fire_enabled_var.get()
        if hasattr(self, 'rapid_fire_key_var'):
            config["rapid_fire_key"] = self.rapid_fire_key_var.get()
        if hasattr(self, 'rapid_fire_interval_var'):
            try:
                interval = int(self.rapid_fire_interval_var.get())
                if interval < 1:  # Garantir valor mínimo
                    interval = 1
                config["rapid_fire_interval"] = interval
            except ValueError:
                config["rapid_fire_interval"] = 15  # Default to 15ms if invalid input
        if hasattr(self, 'rapid_fire_mouse_button_var'):
            config["rapid_fire_mouse_button"] = self.rapid_fire_mouse_button_var.get()
            
        # Salva as configurações do T-bag
        if hasattr(self, 'tbag_enabled_var'):
            config["tbag_enabled"] = self.tbag_enabled_var.get()
        if hasattr(self, 'tbag_key_var'):
            config["tbag_key"] = self.tbag_key_var.get()
        if hasattr(self, 'tbag_interval_var'):
            try:
                interval = int(self.tbag_interval_var.get())
                if interval < 1:  # Garantir valor mínimo
                    interval = 1
                config["tbag_interval"] = interval
            except ValueError:
                config["tbag_interval"] = 50  # Default to 50ms if invalid input
        if hasattr(self, 'tbag_button_var'):
            config["tbag_button"] = self.tbag_button_var.get()
        
        save_config(config)
        self.show_movement_screen()
   
    def update_status_label(self):
        if hasattr(self, 'status_label'):
            status_text = "Status: " + ("Ativo" if self.running else "Inativo")
            status_color = "#00ff00" if self.running else "#ff0000"
            self.status_label.config(text=status_text, fg=status_color)
            
        if hasattr(self, 'rapid_fire_status_label'):
            rf_status_text = "Rapid Fire: " + ("Ativado" if config["rapid_fire_enabled"] else "Desativado")
            rf_status_color = "#00ff00" if config["rapid_fire_enabled"] else "#ff0000"
            self.rapid_fire_status_label.config(text=rf_status_text, fg=rf_status_color)
            
        if hasattr(self, 'tbag_status_label'):
            tbag_status_text = "T-Bag: " + ("Ativado" if config["tbag_enabled"] else "Desativado")
            tbag_status_color = "#00ff00" if config["tbag_enabled"] else "#ff0000"
            self.tbag_status_label.config(text=tbag_status_text, fg=tbag_status_color)
            
        if hasattr(self, 'hide_window_status_label'):
            hide_status_text = "Tecla Esconder: " + config["hide_toggle_key"]
            self.hide_window_status_label.config(text=hide_status_text)
   
    def show_movement_screen(self):
        self.clear_screen()
       
        # Configura o canvas para o fundo animado
        canvas = self.animated_bg.setup_canvas(self.root)
       
        # Frame transparente para os controles
        frame = tk.Frame(canvas, bg="#1c1c1c")
        frame.configure(bg='#1c1c1c')
       
        # Adiciona frame ao canvas usando window_create
        canvas_window = canvas.create_window(300, 220, window=frame)  # Ajustado para centralizar melhor
       
        # Status label
        self.status_label = tk.Label(frame, text="Status: Inativo", fg="#ff0000", bg="#1c1c1c", font=("Arial", 12, "bold"))
        self.status_label.pack(pady=10)
        
        # Rapid Fire status label
        self.rapid_fire_status_label = tk.Label(frame, 
                                              text=f"Rapid Fire: {'Ativado' if config['rapid_fire_enabled'] else 'Desativado'}", 
                                              fg="#00ff00" if config['rapid_fire_enabled'] else "#ff0000", 
                                              bg="#1c1c1c", 
                                              font=("Arial", 12, "bold"))
        self.rapid_fire_status_label.pack(pady=5)
        
        # T-Bag status label
        self.tbag_status_label = tk.Label(frame, 
                                        text=f"T-Bag: {'Ativado' if config['tbag_enabled'] else 'Desativado'}", 
                                        fg="#00ff00" if config['tbag_enabled'] else "#ff0000", 
                                        bg="#1c1c1c", 
                                        font=("Arial", 12, "bold"))
        self.tbag_status_label.pack(pady=5)
        
        # Hide Window status label
        self.hide_window_status_label = tk.Label(frame,
                                              text=f"Tecla Esconder: {config['hide_toggle_key']}",
                                              fg="white", bg="#1c1c1c", font=("Arial", 12))
        self.hide_window_status_label.pack(pady=5)
       
        tk.Label(frame, text="Movimento Vertical:", fg="white", bg="#1c1c1c").pack(pady=5)
        self.vertical_scale = ttk.Scale(frame, from_=0, to=20, orient="horizontal", command=lambda x: self.update_scale_value("vertical", x))
        self.vertical_scale.set(config["vertical_recoil"])
        self.vertical_scale.pack(pady=5)
        self.vertical_value_label = tk.Label(frame, text=str(config["vertical_recoil"]), fg="white", bg="#1c1c1c", cursor="hand2")
        self.vertical_value_label.pack()
        self.vertical_value_label.bind("<Button-1>", lambda e: self.open_value_input_dialog("vertical"))
       
        tk.Label(frame, text="Movimento Horizontal:", fg="white", bg="#1c1c1c").pack(pady=5)
        self.horizontal_scale = ttk.Scale(frame, from_=-10, to=10, orient="horizontal", command=lambda x: self.update_scale_value("horizontal", x))
        self.horizontal_scale.set(config["horizontal_recoil"])
        self.horizontal_scale.pack(pady=5)
        self.horizontal_value_label = tk.Label(frame, text=str(config["horizontal_recoil"]), fg="white", bg="#1c1c1c", cursor="hand2")
        self.horizontal_value_label.pack()
        self.horizontal_value_label.bind("<Button-1>", lambda e: self.open_value_input_dialog("horizontal"))
       
        buttons_frame = tk.Frame(frame, bg="#1c1c1c")
        buttons_frame.pack(pady=20)
       
        tk.Button(buttons_frame, text="Ativar/Desativar (F2)", command=self.toggle_macro, font=("Arial", 12, "bold"),
                  bg="#333333", fg="white", relief="flat", padx=10, pady=5, activebackground="#555555").pack(side="left", padx=10)
       
        tk.Button(buttons_frame, text="Salvar Configurações", command=self.save_movement_settings, font=("Arial", 12, "bold"),
                  bg="#333333", fg="white", relief="flat", padx=10, pady=5, activebackground="#555555").pack(side="left", padx=10)
       
        config_buttons_frame = tk.Frame(frame, bg="#1c1c1c")
        config_buttons_frame.pack(pady=10)
        
        tk.Button(config_buttons_frame, text="Config. Recoil", command=self.show_config_screen, font=("Arial", 12, "bold"),
                  bg="#333333", fg="white", relief="flat", padx=10, pady=5, activebackground="#555555").pack(side="left", padx=5)
                  
        tk.Button(config_buttons_frame, text="Config. Rapid Fire", command=self.show_rapid_fire_config, font=("Arial", 12, "bold"),
                  bg="#333333", fg="white", relief="flat", padx=10, pady=5, activebackground="#555555").pack(side="left", padx=5)
                  
        tk.Button(config_buttons_frame, text="Config. T-Bag", command=self.show_tbag_config, font=("Arial", 12, "bold"),
                  bg="#333333", fg="white", relief="flat", padx=10, pady=5, activebackground="#555555").pack(side="left", padx=5)
        
        # Add Discord contact in bottom right
        self.add_discord_contact(canvas)
   
    def update_scale_value(self, scale_type, value):
        value = float(value)
        rounded_value = round(value, 1)
       
        if scale_type == "vertical":
            self.vertical_value_label.config(text=str(rounded_value))
        elif scale_type == "horizontal":
            self.horizontal_value_label.config(text=str(rounded_value))
            
    def open_value_input_dialog(self, scale_type):
        dialog = tk.Toplevel(self.root)
        dialog.title("Inserir Valor Personalizado")
        dialog.geometry("300x150")
        dialog.configure(bg="#1c1c1c")
        dialog.attributes("-topmost", True)
        
        # Center the dialog on the screen
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Frame to hold contents
        frame = tk.Frame(dialog, bg="#1c1c1c")
        frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # Label
        if scale_type == "vertical":
            label_text = "Insira o valor para o recoil vertical (0-20):"
            min_val = 0
            max_val = 20
            current_val = float(self.vertical_value_label.cget("text"))
        else:  # horizontal
            label_text = "Insira o valor para o recoil horizontal (-10-10):"
            min_val = -10
            max_val = 10
            current_val = float(self.horizontal_value_label.cget("text"))
            
        tk.Label(frame, text=label_text, fg="white", bg="#1c1c1c").pack(pady=5)
        
        # Entry field
        entry_var = tk.StringVar(value=str(current_val))
        entry = tk.Entry(frame, textvariable=entry_var, bg="#333333", fg="white", 
                        insertbackground="white", justify="center")
        entry.pack(pady=10, fill=tk.X)
        entry.select_range(0, tk.END)
        entry.focus_set()
        
        # Button frame
        btn_frame = tk.Frame(frame, bg="#1c1c1c")
        btn_frame.pack(pady=10, fill=tk.X)
        
        # Error label
        error_label = tk.Label(frame, text="", fg="#ff0000", bg="#1c1c1c")
        error_label.pack(pady=5)
        
        def apply_value():
            try:
                value = float(entry_var.get().replace(",", "."))
                if value < min_val or value > max_val:
                    raise ValueError(f"O valor deve estar entre {min_val} e {max_val}")
                    
                # Round to one decimal place
                value = round(value, 1)
                
                if scale_type == "vertical":
                    self.vertical_scale.set(value)
                    self.vertical_value_label.config(text=str(value))
                else:  # horizontal
                    self.horizontal_scale.set(value)
                    self.horizontal_value_label.config(text=str(value))
                    
                dialog.destroy()
            except ValueError as e:
                error_label.config(text=str(e))
                entry.select_range(0, tk.END)
                entry.focus_set()
        
        # Apply and Cancel buttons
        tk.Button(btn_frame, text="Aplicar", command=apply_value, 
                bg="#333333", fg="white", activebackground="#555555").pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        tk.Button(btn_frame, text="Cancelar", command=dialog.destroy, 
                bg="#333333", fg="white", activebackground="#555555").pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # Handle Enter key
        entry.bind("<Return>", lambda event: apply_value())
        
        # Make dialog modal
        dialog.transient(self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)

    def create_key_selector(self, parent, label_text, initial_value, callback=None):
        frame = tk.Frame(parent, bg="#1c1c1c")
        frame.pack(pady=5)
        
        label = tk.Label(frame, text=label_text, fg="white", bg="#1c1c1c")
        label.pack(side="left", padx=5)
        
        button_var = tk.StringVar(value=initial_value)
        
        def on_button_click():
            button.config(text="Pressione uma tecla...", bg="#aa0000")
            self.root.bind('<Key>', lambda event: handle_key_press(event))
        
        def handle_key_press(event):
            # Convert key press to a string representation
            if event.keysym.startswith('F') and event.keysym[1:].isdigit():
                # Handle function keys (F1-F12)
                key_name = event.keysym
            elif event.keysym.startswith('KP_'):
                # Handle numpad keys
                key_name = f"numpad_{event.keysym[3:]}"
            else:
                # Handle other keys
                key_name = event.keysym
            
            button_var.set(key_name)
            button.config(text=f"Tecla: {key_name}", bg="#333333")
            self.root.unbind('<Key>')
            
            if callback:
                callback(key_name)
        
        button = tk.Button(frame, textvariable=button_var, 
                          command=on_button_click,
                          bg="#333333", fg="white", width=20)
        button.pack(side="left", padx=5)
        
        # Format the initial display text
        button.config(text=f"Tecla: {initial_value}")
        
        return button_var
    def show_rapid_fire_config(self):
        self.clear_screen()
        
        # Configura o canvas para o fundo animado
        canvas = self.animated_bg.setup_canvas(self.root)
        
        # Frame transparente para os controles
        frame = tk.Frame(canvas, bg="#1c1c1c")
        
        # Adiciona frame ao canvas usando window_create
        canvas_window = canvas.create_window(300, 220, window=frame)
        
        tk.Label(frame, text="Configurações Rapid Fire", font=("Arial", 16, "bold"), fg="white", bg="#1c1c1c").pack(pady=10)
        
        # Rapid Fire Enabled checkbox
        self.rapid_fire_enabled_var = tk.BooleanVar(value=config["rapid_fire_enabled"])
        
        checkbox_frame = tk.Frame(frame, bg="#1c1c1c")
        checkbox_frame.pack(pady=5)
        
        # Criando checkbutton customizado
        checkbox = tk.Checkbutton(checkbox_frame, variable=self.rapid_fire_enabled_var,
                                  bg="#1c1c1c", activebackground="#1c1c1c", 
                                  selectcolor="#333333", bd=0, highlightthickness=0)
        checkbox.pack(side="left")
        
        # Adicionando texto separadamente
        checkbox_label = tk.Label(checkbox_frame, text="Ativar Rapid Fire", fg="white", bg="#1c1c1c")
        checkbox_label.pack(side="left")
        
        # Rapid Fire Key selector
        self.rapid_fire_key_var = self.create_key_selector(
            frame,
            "Tecla de Ativação Rapid Fire:",
            config["rapid_fire_key"]
        )
        
        # Rapid Fire Interval entry
        interval_frame = tk.Frame(frame, bg="#1c1c1c")
        interval_frame.pack(pady=5)
        
        tk.Label(interval_frame, text="Intervalo (ms):", fg="white", bg="#1c1c1c").pack(side="left", padx=5)
        self.rapid_fire_interval_var = tk.StringVar(value=str(config["rapid_fire_interval"]))
        interval_entry = tk.Entry(interval_frame, textvariable=self.rapid_fire_interval_var, width=5, bg="#333333", fg="white")
        interval_entry.pack(side="left")
        
        # Mouse Button for Rapid Fire
        tk.Label(frame, text="Botão do Mouse:", fg="white", bg="#1c1c1c").pack(pady=5)
        self.rapid_fire_mouse_button_var = tk.StringVar(value=config["rapid_fire_mouse_button"])
        mouse_button_options = ["left_click", "right_click", "both"]
        self.mouse_button_dropdown = ttk.Combobox(frame, textvariable=self.rapid_fire_mouse_button_var, values=mouse_button_options, state="readonly")
        self.mouse_button_dropdown.pack(pady=5)
        
        
        # Explanation text
        explanation_text = """
        Rapid Fire: Quando ativado, simula cliques automáticos
        enquanto a tecla configurada estiver pressionada.
        Intervalo: Tempo em milissegundos entre cada clique (15ms = 10 cliques por segundo).
        """
        explanation_label = tk.Label(frame, text=explanation_text, justify="left", fg="lightgray", bg="#1c1c1c", wraplength=400)
        explanation_label.pack(pady=10)
        
        buttons_frame = tk.Frame(frame, bg="#1c1c1c")
        buttons_frame.pack(pady=20)
        
        tk.Button(buttons_frame, text="Salvar", command=self.save_config_settings, font=("Arial", 12, "bold"),
                  bg="#333333", fg="white", relief="flat", padx=10, pady=5, activebackground="#555555").pack(side="left", padx=10)
        
        tk.Button(buttons_frame, text="Voltar", command=self.show_movement_screen, font=("Arial", 12, "bold"),
                  bg="#333333", fg="white", relief="flat", padx=10, pady=5, activebackground="#555555").pack(side="left", padx=10)
   
    def show_tbag_config(self):
        """Mostra a tela de configuração do T-Bag"""
        self.clear_screen()
        
        # Configura o canvas para o fundo animado
        canvas = self.animated_bg.setup_canvas(self.root)
        
        # Frame transparente para os controles
        frame = tk.Frame(canvas, bg="#1c1c1c")
        
        # Adiciona frame ao canvas usando window_create
        canvas_window = canvas.create_window(300, 220, window=frame)
        
        tk.Label(frame, text="Configurações T-Bag", font=("Arial", 16, "bold"), fg="white", bg="#1c1c1c").pack(pady=10)
        
        # Rapid Fire Enabled checkbox
        self.tbag_enabled_var = tk.BooleanVar(value=config["tbag_enabled"])
        
        checkbox_frame = tk.Frame(frame, bg="#1c1c1c")
        checkbox_frame.pack(pady=5)
        
        # Criando checkbutton customizado
        checkbox = tk.Checkbutton(checkbox_frame, variable=self.tbag_enabled_var,
                                  bg="#1c1c1c", activebackground="#1c1c1c", 
                                  selectcolor="#333333", bd=0, highlightthickness=0)
        checkbox.pack(side="left")
        
        # Adicionando texto separadamente
        checkbox_label = tk.Label(checkbox_frame, text="Ativar T-Bag", fg="white", bg="#1c1c1c")
        checkbox_label.pack(side="left")
        
        # T-Bag Key selector
        self.tbah_key_var = self.create_key_selector(
            frame,
            "Tecla de Ativação T-Bag:",
            config["tbag_key"]
        )
        
        # Rapid Fire Interval entry
        interval_frame = tk.Frame(frame, bg="#1c1c1c")
        interval_frame.pack(pady=5)
        
        tk.Label(interval_frame, text="Intervalo (ms):", fg="white", bg="#1c1c1c").pack(side="left", padx=5)
        self.tbag_interval_var = tk.StringVar(value=str(config["tbag_interval"]))
        interval_entry = tk.Entry(interval_frame, textvariable=self.tbag_interval_var, width=5, bg="#333333", fg="white")
        interval_entry.pack(side="left")
        
        # Mouse Button for Rapid Fire
        tk.Label(frame, text="Tecla de Agachar:", fg="white", bg="#1c1c1c").pack(pady=5)
        self.tbag_button_var = self.create_key_selector(
            frame,
            "Tecla de Agachar T-Bag:",
            config["tbag_button"]
        )


        buttons_frame = tk.Frame(frame, bg="#1c1c1c")
        buttons_frame.pack(pady=20)
        
        tk.Button(buttons_frame, text="Salvar", command=self.save_config_settings, font=("Arial", 12, "bold"),
                  bg="#333333", fg="white", relief="flat", padx=10, pady=5, activebackground="#555555").pack(side="left", padx=10)
        
        tk.Button(buttons_frame, text="Voltar", command=self.show_movement_screen, font=("Arial", 12, "bold"),
                  bg="#333333", fg="white", relief="flat", padx=10, pady=5, activebackground="#555555").pack(side="left", padx=10)
   
        
    def show_config_screen(self):
        self.clear_screen()
        
        # Configura o canvas para o fundo animado
        canvas = self.animated_bg.setup_canvas(self.root)
        
        # Frame transparente para os controles
        frame = tk.Frame(canvas, bg="#1c1c1c")
        
        # Adiciona frame ao canvas usando window_create
        canvas_window = canvas.create_window(300, 220, window=frame)
        
        tk.Label(frame, text="Config. Recoil", font=("Arial", 16, "bold"), fg="white", bg="#1c1c1c").pack(pady=10)
        
        # Activation key selector
        self.activation_key_var = self.create_key_selector(
            frame, 
            "Tecla de Ativação:", 
            config["activation_key"]
        )
        
        # Toggle key selector
        self.toggle_key_var = self.create_key_selector(
            frame, 
            "Tecla de Alternar:", 
            config["toggle_key"]
        )
        
        # Mouse activation dropdown (unchanged)
        tk.Label(frame, text="Ativação do Mouse:", fg="white", bg="#1c1c1c").pack(pady=5)
        self.mouse_activation_var = tk.StringVar(value=config["mouse_activation"])
        mouse_options = ["left_click", "right_click", "both"]
        self.mouse_dropdown = ttk.Combobox(frame, textvariable=self.mouse_activation_var, values=mouse_options, state="readonly")
        self.mouse_dropdown.pack(pady=5)
        buttons_frame = tk.Frame(frame, bg="#1c1c1c")
        buttons_frame.pack(pady=20)
        
        tk.Button(buttons_frame, text="Salvar", command=self.save_config_settings, font=("Arial", 12, "bold"),
                  bg="#333333", fg="white", relief="flat", padx=10, pady=5, activebackground="#555555").pack(side="left", padx=10)
        
        tk.Button(buttons_frame, text="Voltar", command=self.show_movement_screen, font=("Arial", 12, "bold"),
                  bg="#333333", fg="white", relief="flat", padx=10, pady=5, activebackground="#555555").pack(side="left", padx=10)
   
       
        # Background G
       
        # Background GIF selection

        tk.Entry(frame, textvariable=self.bg_file_var, bg="#333333", fg="white").pack(pady=5)
       
        buttons_frame = tk.Frame(frame, bg="#1c1c1c")
        buttons_frame.pack(pady=20)
       
        tk.Button(buttons_frame, text="Salvar", command=self.save_config_settings, font=("Arial", 12, "bold"),
                  bg="#333333", fg="white", relief="flat", padx=10, pady=5, activebackground="#555555").pack(side="left", padx=10)
       
        tk.Button(buttons_frame, text="Voltar", command=self.show_movement_screen, font=("Arial", 12, "bold"),
                  bg="#333333", fg="white", relief="flat", padx=10, pady=5, activebackground="#555555").pack(side="left", padx=10)
   
    def clear_screen(self):
        for widget in self.root.winfo_children():
            if widget != self.titlebar:
                widget.destroy()
        if not hasattr(self, 'titlebar') or not self.titlebar.winfo_exists():
            self.setup_custom_titlebar()

def create_key_selector(self, parent, label_text, initial_value, callback=None):
    frame = tk.Frame(parent, bg="#1c1c1c")
    frame.pack(pady=5)
    
    label = tk.Label(frame, text=label_text, fg="white", bg="#1c1c1c")
    label.pack(side="left", padx=5)
    
    button_var = tk.StringVar(value=initial_value)
    
if __name__ == "__main__":
    root = tk.Tk()
    root.overrideredirect(True)
    app = RecoilControlApp(root)
    root.mainloop()