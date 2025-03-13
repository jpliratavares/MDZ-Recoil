# Fullscreen Game Mouse Detection Solution

## Problem
The original application wasn't working in fullscreen games because it was using `pynput` for mouse detection, which doesn't work in many fullscreen games due to security restrictions and how input focus works in those applications.

## Solution
The solution was to replace `pynput`'s mouse detection with Windows API hooks, which can detect mouse input regardless of application focus, including fullscreen games.

## Changes Made
1. Created a new module `mouse_hook.py` that implements Windows API low-level mouse hooks
2. Replaced `pynput.mouse.Controller` with our custom `MockMouseController`
3. Updated mouse button detection to use our custom `MockMouse.Button` class
4. Removed `pynput.mouse` import while keeping `pynput.keyboard` for keyboard detection

## Final Step Required
To complete the implementation, the `run_macro` method needs to be modified to install our custom mouse hook:

```python
def run_macro(self):
    # Install Windows hook to capture mouse events in fullscreen games
    mouse_hook.install_mouse_hook(self.on_mouse_click)
    
    try:
        while self.running:
            if self.shooting:
                self.apply_recoil()
            time.sleep(0.02)
    finally:
        # Always clean up the hook when thread ends
        mouse_hook.uninstall_mouse_hook()
```

This ensures that:
1. The Windows API mouse hook is installed when the macro starts
2. Mouse clicks are captured in all applications, including fullscreen games
3. The hook is properly cleaned up when the thread ends

With these changes, the application will now work properly in fullscreen games, detecting mouse clicks and performing the intended actions.