# Rapid Fire Feature Fix

## Issue
The error occurs in the `run_rapid_fire` method when trying to access `mouse.Button.left` in line 450:

```
NameError: name 'mouse' is not defined
```

## Root Cause
Even though the `mouse` module is imported at the top level of the file, it's not available within the thread where `run_rapid_fire` is executed. This is because each thread has its own scope, and top-level imports aren't automatically inherited by new threads.

## Solution
Add a local import statement inside the `run_rapid_fire` method:

```python
def run_rapid_fire(self):
    from pynput import mouse  # Local import to ensure availability in this thread
    while self.rapid_fire_active:
        # Rest of the code remains unchanged
        # ...
```

This ensures that the `mouse` module is properly imported within the thread's scope, making the `Button` class available when needed.

## Implementation Steps
1. Open main.py
2. Add the line `from pynput import mouse` at the beginning of the `run_rapid_fire` method (line 447)
3. Save the file

This change allows the rapid fire feature to work correctly by ensuring that the mouse module is available in the thread's execution context.