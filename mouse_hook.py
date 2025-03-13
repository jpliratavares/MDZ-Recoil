import ctypes
import ctypes.wintypes
import atexit

# Windows API constants for mouse hooks
WH_MOUSE_LL = 14
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_RBUTTONDOWN = 0x0204
WM_RBUTTONUP = 0x0205

# Create variable to store the hook handle
mouse_hook = None

# Define the callback function type for the mouse hook
CMPFUNC = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.wintypes.WPARAM, ctypes.POINTER(ctypes.c_void_p))

# Mock mouse button objects to maintain compatibility with existing code
class MouseButton:
    def __init__(self, name):
        self.name = name
    
    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        return self.name == other.name

class MockMouse:
    class Button:
        left = MouseButton("left")
        right = MouseButton("right")

# Shared variable to track mouse button states
mouse_state = {'left': False, 'right': False}
callback_handler = None

# Callback function for the low-level mouse hook
def mouse_hook_proc(n_code, w_param, l_param):
    global callback_handler
    
    if n_code >= 0:
        if w_param == WM_LBUTTONDOWN:
            mouse_state['left'] = True
            if callback_handler:
                callback_handler(0, 0, MockMouse.Button.left, True)
        elif w_param == WM_LBUTTONUP:
            mouse_state['left'] = False
            if callback_handler:
                callback_handler(0, 0, MockMouse.Button.left, False)
        elif w_param == WM_RBUTTONDOWN:
            mouse_state['right'] = True
            if callback_handler:
                callback_handler(0, 0, MockMouse.Button.right, True)
        elif w_param == WM_RBUTTONUP:
            mouse_state['right'] = False
            if callback_handler:
                callback_handler(0, 0, MockMouse.Button.right, False)
                
    return ctypes.windll.user32.CallNextHookEx(mouse_hook, n_code, w_param, l_param)

# Keep a reference to the callback to prevent garbage collection
mouse_callback = None

# Function to install the mouse hook
def install_mouse_hook(callback=None):
    global mouse_hook, mouse_callback, callback_handler
    
    callback_handler = callback
    mouse_callback = CMPFUNC(mouse_hook_proc)
    
    mouse_hook = ctypes.windll.user32.SetWindowsHookExA(
        WH_MOUSE_LL, 
        mouse_callback, 
        ctypes.windll.kernel32.GetModuleHandleA(None), 
        0
    )
    if not mouse_hook:
        return False
    return True

# Function to uninstall the mouse hook
def uninstall_mouse_hook():
    global mouse_hook
    if mouse_hook:
        ctypes.windll.user32.UnhookWindowsHookEx(mouse_hook)
        mouse_hook = None

# Register hook cleanup at exit
atexit.register(uninstall_mouse_hook)

# Mock mouse controller class to maintain compatibility with existing code
class MockMouseController:
    @staticmethod
    def move(dx, dy):
        point = ctypes.wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
        ctypes.windll.user32.SetCursorPos(point.x + int(dx), point.y + int(dy))
        
    def click(self, button):
        # Simulate a mouse click using Win32 API
        mouse_event = ctypes.windll.user32.mouse_event
        if button.name == 'left':
            mouse_event(0x0002, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTDOWN
            mouse_event(0x0004, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTUP
        elif button.name == 'right':
            mouse_event(0x0008, 0, 0, 0, 0)  # MOUSEEVENTF_RIGHTDOWN
            mouse_event(0x0010, 0, 0, 0, 0)  # MOUSEEVENTF_RIGHTUP