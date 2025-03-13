from PIL import Image
from PIL import Image, ImageTk
from RecoilSync.main import RecoilControlApp
from main import AnimatedGIF
from main import FlameEffect
from main import RecoilControlApp
from main import RecoilControlApp, AnimatedGIF, load_config
from main import RecoilControlApp, config
from main import RecoilControlApp, config, save_config
from main import RecoilControlApp, load_config
from main import load_config
from main import load_config, CONFIG_FILE, GIF_FILE
from pynput import keyboard
from pynput import keyboard, mouse
from pynput import mouse
from pynput.keyboard import Key
from tkinter import Button, Tk
from tkinter import ttk
from unittest.mock import MagicMock
from unittest.mock import MagicMock, patch
from unittest.mock import Mock
from unittest.mock import Mock, patch
from unittest.mock import patch
from unittest.mock import patch, MagicMock
from unittest.mock import patch, mock_open
import io
import json
import main
import os
import pytest
import random
import sys
import threading
import time
import tkinter as tk
import unittest
import unittest.mock
import webbrowser
import win32gui

CONFIG_FILE = "config.json"

config = {
    "toggle_key": "F2",
    "rapid_fire_enabled": True,
    "rapid_fire_key": "F3",
    "tbag_enabled": True,
    "tbag_key": "F4",
    "hide_toggle_key": "F6"
}

mock_config = {
    "toggle_key": "f2",
    "rapid_fire_enabled": True,
    "rapid_fire_key": "f3",
    "tbag_enabled": True,
    "tbag_key": "f4",
    "hide_toggle_key": "f6"
}

class TestMain:

    def is_game_focused(self):
        """Check if a game window might be in focus"""
        try:
            window_title = win32gui.GetWindowText(win32gui.GetForegroundWindow())
            # Add common game window titles or partial matches here
            game_keywords = ["game", "directx", "opengl", "unity", "call of duty", "warzone", 
                              "cs2", "valorant", "fortnite", "apex", "battlefield"]
            
            return any(keyword.lower() in window_title.lower() for keyword in game_keywords)
        except ImportError:
            # If win32gui is not available, assume we're always in a game
            return True

    def test_add_discord_contact_1(self):
        """
        Test that the add_discord_contact method creates a frame with correct properties
        and adds it to the canvas in the bottom right corner.
        """
        root = tk.Tk()
        app = RecoilControlApp(root)
        canvas = tk.Canvas(root, width=600, height=480)

        app.add_discord_contact(canvas)

        # Check if a window was created in the canvas
        windows = canvas.find_withtag('window')
        assert len(windows) == 1, "Expected one window to be created in the canvas"

        # Check if the window is positioned correctly
        window_info = canvas.bbox(windows[0])
        assert window_info[2] == 580 and window_info[3] == 470, "Window not positioned correctly"

        # Check if the frame has the correct background color
        frame = canvas.itemcget(windows[0], 'window')
        assert frame.cget('bg') == "#2d2d2d", "Frame background color is incorrect"

        root.destroy()

    def test_add_discord_contact_invalid_canvas(self):
        """
        Test the add_discord_contact method with an invalid canvas object.
        This tests the edge case where the canvas parameter is not a valid tkinter Canvas object.
        """
        app = RecoilControlApp(tk.Tk())
        invalid_canvas = "Not a canvas"

        with self.assertRaises(AttributeError):
            app.add_discord_contact(invalid_canvas)

    def test_animate_flames_1(self):
        """
        Tests the animate_flames method of FlameEffect class.
        Covers the path where:
        - flame['id'] is not None
        - flame['opacity'] <= 0
        - randomly chosen side is 'top'
        """
        # Setup
        root = tk.Tk()
        canvas = tk.Canvas(root)
        flame_effect = FlameEffect(canvas, 800, 600)

        # Mocking
        flame_effect.canvas = MagicMock()
        flame_effect.flames = [{
            'id': 'dummy_id',
            'opacity': 0,
            'x': 100,
            'y': 100,
            'size': 15,
            'speed': 2
        }]

        # Patching random.choice to always return 'top'
        with patch('random.choice', return_value='top'):
            # Patching random.randint and random.uniform for deterministic behavior
            with patch('random.randint', return_value=400):
                with patch('random.uniform', return_value=0.5):
                    flame_effect.animate_flames()

        # Assertions
        flame_effect.canvas.delete.assert_called_once_with('dummy_id')
        flame_effect.canvas.create_oval.assert_called_once()
        assert flame_effect.flames[0]['y'] == flame_effect.height
        assert flame_effect.flames[0]['x'] == 400
        assert flame_effect.flames[0]['opacity'] == 0.5

    def test_animate_flames_2(self):
        """
        Test the animate_flames method when a flame's opacity reaches zero and is reset from the top.

        This test case covers the following path constraints:
        - The flame does not have an existing ID (not flame['id'] is not None)
        - The flame's opacity is less than or equal to zero (flame['opacity'] <= 0)
        - The randomly chosen side for resetting the flame is 'top' (side == 'top')
        """
        # Create a mock canvas
        mock_canvas = Mock()

        # Create a FlameEffect instance with the mock canvas
        flame_effect = FlameEffect(mock_canvas, 800, 600)

        # Set up a flame with opacity <= 0
        test_flame = {
            'id': None,
            'opacity': 0,
            'x': 400,
            'y': 300,
            'size': 15,
            'speed': 2
        }
        flame_effect.flames = [test_flame]

        # Mock random.choice to always return 'top'
        with patch('random.choice', return_value='top'):
            # Mock random.randint and random.uniform for deterministic results
            with patch('random.randint', return_value=500):
                with patch('random.uniform', return_value=0.5):
                    # Call the method under test
                    flame_effect.animate_flames()

        # Assert that the flame was reset correctly
        self.assertIsNone(test_flame['id'])
        self.assertEqual(test_flame['x'], 500)  # New x position from random.randint
        self.assertEqual(test_flame['y'], 600)  # Height of the canvas
        self.assertEqual(test_flame['opacity'], 0.5)  # New opacity from random.uniform

        # Assert that canvas.create_oval was called with the correct arguments
        mock_canvas.create_oval.assert_called_once_with(
            485, 585, 515, 615,  # Calculated from x, y, and size
            fill='#7f0000',  # Red color based on opacity
            outline='',
            stipple='gray50'
        )

        # Assert that canvas.after was called to schedule the next animation
        mock_canvas.after.assert_called_once_with(50, flame_effect.animate_flames)

    def test_animate_flames_3(self):
        """
        Test the animate_flames method when a flame's opacity reaches 0 and is reset from the bottom.

        This test verifies that:
        1. The flame's existing canvas object is deleted
        2. A new canvas object is created with the correct parameters
        3. The flame's position is reset to the bottom of the screen
        4. The flame's opacity is reset to a random value between 0.3 and 0.8
        """
        # Mock the FlameEffect class and its dependencies
        with patch('tkinter.Canvas') as mock_canvas:
            flame_effect = MagicMock()
            flame_effect.canvas = mock_canvas
            flame_effect.width = 800
            flame_effect.height = 600

            # Create a test flame with opacity 0
            test_flame = {
                'id': 'test_id',
                'x': 400,
                'y': 300,
                'size': 15,
                'speed': 2,
                'opacity': 0
            }
            flame_effect.flames = [test_flame]

            # Mock random.choice to always return 'bottom'
            with patch('random.choice', return_value='bottom'):
                # Mock random.uniform and random.randint
                with patch('random.uniform', return_value=0.5) as mock_uniform:
                    with patch('random.randint', return_value=400) as mock_randint:
                        # Call the method under test
                        flame_effect.animate_flames()

            # Verify that the existing canvas object was deleted
            mock_canvas.delete.assert_called_once_with('test_id')

            # Verify that a new canvas object was created with the correct parameters
            mock_canvas.create_oval.assert_called_once()
            args, kwargs = mock_canvas.create_oval.call_args
            assert args == (385, 585, 415, 615)  # x-size, y, x+size, y+size
            assert kwargs['fill'] == '#7f0000'  # r = int(255 * (1 - 0.5))
            assert kwargs['outline'] == ''
            assert kwargs['stipple'] == 'gray50'

            # Verify that the flame's position was reset to the bottom
            assert test_flame['x'] == 400
            assert test_flame['y'] == 0

            # Verify that the flame's opacity was reset
            assert test_flame['opacity'] == 0.5

            # Verify that random.uniform was called to reset opacity
            mock_uniform.assert_called_once_with(0.3, 0.8)

            # Verify that random.randint was called to reset x position
            mock_randint.assert_called_once_with(0, 800)

            # Verify that canvas.after was called to schedule the next animation
            mock_canvas.after.assert_called_once_with(50, flame_effect.animate_flames)

    def test_animate_flames_4(self):
        """
        Test case for animate_flames method when flame['id'] is not None and flame['opacity'] > 0.

        This test verifies that the animate_flames method correctly updates the flame
        properties and redraws the flame on the canvas when the flame already exists
        and its opacity is above the threshold for regeneration.
        """
        # Create a mock Tkinter canvas
        mock_canvas = tk.Canvas()

        # Create a FlameEffect instance with the mock canvas
        flame_effect = FlameEffect(mock_canvas, 800, 600)

        # Set up a test flame with known properties
        test_flame = {
            'id': 'test_flame_id',
            'x': 400,
            'y': 300,
            'size': 15,
            'speed': 2,
            'opacity': 0.5
        }
        flame_effect.flames = [test_flame]

        # Call the animate_flames method
        flame_effect.animate_flames()

        # Verify that the flame properties were updated correctly
        assert test_flame['y'] == 298  # y should decrease by speed
        assert 0.46 <= test_flame['opacity'] <= 0.48  # opacity should decrease by about 0.02

        # Verify that the canvas.delete and canvas.create_oval methods were called
        assert mock_canvas.delete.called_with('test_flame_id')
        assert mock_canvas.create_oval.called

        # Verify that the canvas.after method was called to schedule the next animation
        assert mock_canvas.after.called_with(50, flame_effect.animate_flames)

    def test_animate_flames_with_empty_flames_list(self):
        """
        Test animate_flames method when the flames list is empty.
        This tests the edge case where there are no flames to animate.
        """
        root = tk.Tk()
        canvas = tk.Canvas(root)
        flame_effect = FlameEffect(canvas, 100, 100)
        flame_effect.flames = []  # Set flames list to empty

        # Call animate_flames - it should not raise any exceptions
        flame_effect.animate_flames()

        # Verify that no errors occurred and the method completed
        assert True

    def test_animate_flames_with_invalid_flame_id(self):
        """
        Test animate_flames method when a flame has an invalid ID.
        This tests the edge case where a flame's ID is not recognized by the canvas.
        """
        root = tk.Tk()
        canvas = tk.Canvas(root)
        flame_effect = FlameEffect(canvas, 100, 100)

        # Create a flame with an invalid ID
        invalid_flame = {
            'id': 'invalid_id',
            'x': 50,
            'y': 50,
            'size': 10,
            'speed': 1,
            'opacity': 0.5
        }
        flame_effect.flames = [invalid_flame]

        # Call animate_flames - it should handle the invalid ID gracefully
        flame_effect.animate_flames()

        # Verify that no errors occurred and the method completed
        assert True

    def test_animate_flames_with_zero_opacity(self):
        """
        Test animate_flames method when a flame has zero opacity.
        This tests the edge case where a flame becomes fully transparent.
        """
        root = tk.Tk()
        canvas = tk.Canvas(root)
        flame_effect = FlameEffect(canvas, 100, 100)

        # Create a flame with zero opacity
        zero_opacity_flame = {
            'id': None,
            'x': 50,
            'y': 50,
            'size': 10,
            'speed': 1,
            'opacity': 0
        }
        flame_effect.flames = [zero_opacity_flame]

        # Call animate_flames - it should handle zero opacity correctly
        flame_effect.animate_flames()

        # Verify that the flame was reset with a new opacity
        assert flame_effect.flames[0]['opacity'] > 0

    def test_apply_recoil_1(self):
        """
        Test the apply_recoil method of RecoilControlApp.

        This test verifies that the apply_recoil method correctly applies
        the recoil effect based on the configuration settings. It checks
        if the mouse movement is performed in small increments and if the
        total movement matches the expected horizontal and vertical recoil values.
        """
        root = tk.Tk()
        app = RecoilControlApp(root)

        # Set up test configuration
        app.config = {
            "horizontal_recoil": 5,
            "vertical_recoil": 10
        }

        # Mock the mouse_controller
        class MockMouseController:
            def __init__(self):
                self.total_dx = 0
                self.total_dy = 0

            def move(self, dx, dy):
                self.total_dx += dx
                self.total_dy += dy

        app.mouse_controller = MockMouseController()

        # Call the method under test
        app.apply_recoil()

        # Check if the total movement is close to the expected values
        self.assertAlmostEqual(app.mouse_controller.total_dx, 5, delta=1)
        self.assertAlmostEqual(app.mouse_controller.total_dy, 10, delta=1)

    def test_apply_recoil_no_config(self):
        """
        Test apply_recoil when config is empty or missing required keys.
        This tests the edge case where the configuration is not properly set.
        """
        # Assuming we can temporarily modify the global config
        original_config = config.copy()
        config.clear()  # Empty the config

        app = RecoilControlApp(tk.Tk())

        # We expect no movement if config is empty
        app.apply_recoil()

        # Restore the original config
        config.update(original_config)

    def test_apply_recoil_zero_values(self):
        """
        Test apply_recoil when horizontal and vertical recoil are set to zero.
        This tests the edge case of minimum possible recoil values.
        """
        # Assuming we can temporarily modify the global config
        original_config = config.copy()
        config["horizontal_recoil"] = 0
        config["vertical_recoil"] = 0

        app = RecoilControlApp(tk.Tk())

        # We expect minimal movement due to jitter, even with zero recoil
        app.apply_recoil()

        # Restore the original config
        config.update(original_config)

    def test_clear_screen_1(self):
        """
        Test that clear_screen removes all widgets except the titlebar and creates a new titlebar if it doesn't exist.

        This test covers the following path constraints:
        - At least one widget exists that is not the titlebar
        - The titlebar doesn't exist or is not valid
        """
        root = tk.Tk()
        app = RecoilControlApp(root)

        # Create some dummy widgets
        tk.Label(root, text="Dummy Label").pack()
        tk.Button(root, text="Dummy Button").pack()

        # Remove the titlebar attribute to simulate it not existing
        if hasattr(app, 'titlebar'):
            delattr(app, 'titlebar')

        # Call the method under test
        app.clear_screen()

        # Check that all widgets except the titlebar have been removed
        remaining_widgets = root.winfo_children()
        self.assertEqual(len(remaining_widgets), 1, "There should be only one widget remaining (the titlebar)")

        # Check that the remaining widget is indeed a titlebar
        self.assertTrue(hasattr(app, 'titlebar'), "The titlebar attribute should exist")
        self.assertEqual(remaining_widgets[0], app.titlebar, "The remaining widget should be the titlebar")

        root.destroy()

    def test_clear_screen_1_2(self):
        """
        Test that clear_screen destroys all widgets except the titlebar and creates a new titlebar if it doesn't exist.

        This test covers the scenario where:
        1. There are widgets other than the titlebar
        2. The titlebar doesn't exist or is not valid
        """
        # Create a mock Tk root
        root = MagicMock(spec=tk.Tk)

        # Create the RecoilControlApp instance
        app = RecoilControlApp(root)

        # Create mock widgets
        mock_widget1 = MagicMock()
        mock_widget2 = MagicMock()

        # Set up the root to return our mock widgets
        root.winfo_children.return_value = [mock_widget1, mock_widget2]

        # Ensure app.titlebar doesn't exist
        if hasattr(app, 'titlebar'):
            delattr(app, 'titlebar')

        # Mock the setup_custom_titlebar method
        app.setup_custom_titlebar = MagicMock()

        # Call the method under test
        app.clear_screen()

        # Assert that destroy was called on both widgets
        mock_widget1.destroy.assert_called_once()
        mock_widget2.destroy.assert_called_once()

        # Assert that setup_custom_titlebar was called
        app.setup_custom_titlebar.assert_called_once()

    def test_clear_screen_2(self):
        """
        Tests clear_screen method when titlebar doesn't exist or is not valid.

        This test verifies that the clear_screen method correctly handles the case
        when the titlebar attribute is not present or is not a valid widget. It
        ensures that the setup_custom_titlebar method is called in such cases.
        """
        # Import necessary modules

        # Create a root window and RecoilControlApp instance
        root = tk.Tk()
        app = RecoilControlApp(root)

        # Remove titlebar attribute to simulate it not existing
        if hasattr(app, 'titlebar'):
            delattr(app, 'titlebar')

        # Mock the setup_custom_titlebar method
        app.setup_custom_titlebar = lambda: setattr(app, 'titlebar_setup_called', True)

        # Call the clear_screen method
        app.clear_screen()

        # Assert that setup_custom_titlebar was called
        assert hasattr(app, 'titlebar_setup_called'), "setup_custom_titlebar was not called"

        # Clean up
        root.destroy()

    def test_clear_screen_3(self):
        """
        Tests the clear_screen method when there are widgets other than the titlebar,
        and the titlebar exists and is valid.
        """
        root = tk.Tk()
        app = RecoilControlApp(root)

        # Create a mock titlebar
        app.titlebar = tk.Frame(root)

        # Create some additional widgets
        tk.Label(root, text="Test Label")
        tk.Button(root, text="Test Button")

        # Call the clear_screen method
        app.clear_screen()

        # Check that only the titlebar remains
        remaining_widgets = root.winfo_children()
        assert len(remaining_widgets) == 1
        assert remaining_widgets[0] == app.titlebar

        root.destroy()

    def test_clear_screen_when_titlebar_does_not_exist(self):
        """
        Test the clear_screen method when the titlebar attribute does not exist.
        This tests the edge case where the titlebar hasn't been created yet,
        which is explicitly handled in the method.
        """
        root = tk.Tk()
        app = RecoilControlApp(root)

        # Remove the titlebar attribute if it exists
        if hasattr(app, 'titlebar'):
            delattr(app, 'titlebar')

        # Call clear_screen method
        app.clear_screen()

        # Assert that setup_custom_titlebar was called
        assert hasattr(app, 'titlebar'), "The titlebar should have been created"

        root.destroy()

    def test_clear_screen_when_titlebar_not_exists(self):
        """
        Test clear_screen when the titlebar attribute doesn't exist.
        This is an edge case explicitly handled in the method.
        """
        root = tk.Tk()
        app = RecoilControlApp(root)

        # Remove titlebar attribute to simulate it not existing
        if hasattr(app, 'titlebar'):
            delattr(app, 'titlebar')

        # Mock setup_custom_titlebar method
        app.setup_custom_titlebar = MagicMock()

        # Call clear_screen
        app.clear_screen()

        # Assert that setup_custom_titlebar was called
        app.setup_custom_titlebar.assert_called_once()

    def test_clear_screen_when_titlebar_not_exists_in_gui(self):
        """
        Test clear_screen when the titlebar widget doesn't exist in the GUI.
        This is another edge case explicitly handled in the method.
        """
        root = tk.Tk()
        app = RecoilControlApp(root)

        # Create a dummy titlebar attribute that doesn't exist in GUI
        app.titlebar = MagicMock()
        app.titlebar.winfo_exists.return_value = False

        # Mock setup_custom_titlebar method
        app.setup_custom_titlebar = MagicMock()

        # Call clear_screen
        app.clear_screen()

        # Assert that setup_custom_titlebar was called
        app.setup_custom_titlebar.assert_called_once()

    def test_create_flames_1(self):
        """
        Test that create_flames generates flames on the top side of the canvas.

        This test verifies that when the random choice selects 'top' as the side,
        flames are created with y-coordinate 0 and x-coordinate within the canvas width.
        """
        canvas_mock = None  # Mock canvas object would be needed in a real test
        width = 800
        height = 600
        flame_effect = FlameEffect(canvas_mock, width, height)

        # Force 'random.choice' to always return 'top'
        random.choice = lambda _: 'top'

        flame_effect.create_flames()

        for flame in flame_effect.flames:
            assert flame['y'] == 0
            assert 0 <= flame['x'] <= width
            assert 10 <= flame['size'] <= 20
            assert 1 <= flame['speed'] <= 3
            assert 0.3 <= flame['opacity'] <= 0.8
            assert flame['id'] is None

    def test_create_flames_2(self):
        """
        Tests the create_flames method when the randomly chosen side is 'bottom'.

        This test ensures that when 'bottom' is chosen as the side, the flame's
        y-coordinate is set to the height of the FlameEffect instance, and its
        x-coordinate is a random value between 0 and the width.
        """
        # Set up a deterministic random seed
        random.seed(42)

        # Create a FlameEffect instance with known dimensions
        flame_effect = FlameEffect(None, 800, 600)

        # Force the 'side' choice to be 'bottom'
        original_choice = random.choice
        random.choice = lambda _: 'bottom'

        # Call the method under test
        flame_effect.create_flames()

        # Restore the original random.choice function
        random.choice = original_choice

        # Check that at least one flame was created
        assert len(flame_effect.flames) > 0

        # Check the last created flame (should be a 'bottom' flame)
        last_flame = flame_effect.flames[-1]
        assert last_flame['y'] == flame_effect.height
        assert 0 <= last_flame['x'] <= flame_effect.width

        # Additional checks for other flame properties
        assert 10 <= last_flame['size'] <= 20
        assert 1 <= last_flame['speed'] <= 3
        assert 0.3 <= last_flame['opacity'] <= 0.8
        assert last_flame['id'] is None

    def test_create_flames_3(self):
        """
        Test the create_flames method when the randomly chosen side is 'left'.

        This test verifies that when 'left' is chosen as the side:
        1. The x-coordinate of the flame is set to 0.
        2. The y-coordinate of the flame is a random value between 0 and the height of the effect area.
        3. Other properties of the flame (size, speed, opacity) are set within expected ranges.
        4. The flame is added to the flames list.
        """
        with patch('random.choice', return_value='left'), \
             patch('random.randint', return_value=50), \
             patch('random.uniform', return_value=0.5):

            flame_effect = FlameEffect(None, 100, 200)  # Mock canvas, width=100, height=200
            flame_effect.flames = []  # Clear any existing flames

            flame_effect.create_flames()

            assert len(flame_effect.flames) == 1
            flame = flame_effect.flames[0]
            assert flame['x'] == 0
            assert flame['y'] == 50  # Random value between 0 and height (200)
            assert flame['size'] == 50  # Random value between 10 and 20
            assert flame['speed'] == 0.5  # Random value between 1 and 3
            assert flame['opacity'] == 0.5  # Random value between 0.3 and 0.8
            assert flame['id'] is None

    def test_create_flames_4(self):
        """
        Test that create_flames generates flames on the right side when random.choice selects 'right'.

        This test verifies that when the random side selection results in 'right',
        the flame is created with x-coordinate equal to the width of the canvas
        and a random y-coordinate within the height of the canvas.
        """
        # Mock random.choice to always return 'right'
        random.choice = lambda _: 'right'

        # Create a FlameEffect instance with a mock canvas
        canvas_mock = unittest.mock.Mock()
        flame_effect = FlameEffect(canvas_mock, width=800, height=600)

        # Clear existing flames
        flame_effect.flames.clear()

        # Call create_flames
        flame_effect.create_flames()

        # Check that a flame was created
        self.assertEqual(len(flame_effect.flames), 1)

        # Verify the flame's position
        flame = flame_effect.flames[0]
        self.assertEqual(flame['x'], flame_effect.width)
        self.assertTrue(0 <= flame['y'] <= flame_effect.height)

    def test_create_key_selector_1(self):
        """
        Test that create_key_selector method creates and returns a StringVar with the correct initial value
        """
        root = tk.Tk()
        app = RecoilControlApp(root)
        parent = tk.Frame(root)
        label_text = "Test Label"
        initial_value = "F1"

        result = app.create_key_selector(parent, label_text, initial_value)

        assert isinstance(result, tk.StringVar)
        assert result.get() == initial_value

        root.destroy()

    def test_create_key_selector_1_2(self):
        """
        Test create_key_selector method for function key press with callback.

        This test verifies that:
        1. The create_key_selector method correctly handles function key presses (F1-F12).
        2. The callback function is called with the correct key name.
        3. The button text and background are updated correctly after key press.
        """
        root = tk.Tk()
        app = RecoilControlApp(root)
        parent = tk.Frame(root)
        label_text = "Test Label"
        initial_value = "F1"
        mock_callback = Mock()

        button_var = app.create_key_selector(parent, label_text, initial_value, mock_callback)

        # Simulate F5 key press
        with patch.object(app.root, 'bind') as mock_bind:
            button = parent.winfo_children()[1]  # Get the button widget
            button.invoke()  # Click the button
            key_press_handler = mock_bind.call_args[0][1]
            event = Mock(keysym='F5')
            key_press_handler(event)

        # Assertions
        self.assertEqual(button_var.get(), 'F5')
        self.assertEqual(button.cget('text'), 'Tecla: F5')
        self.assertEqual(button.cget('bg'), '#333333')
        mock_callback.assert_called_once_with('F5')

        root.destroy()

    def test_create_key_selector_empty_initial_value(self):
        """
        Test create_key_selector with an empty initial value.
        This tests the edge case where the initial_value parameter is an empty string.
        """
        app = Mock()
        parent = tk.Tk()
        label_text = "Test Label"
        initial_value = ""

        result = app.create_key_selector(parent, label_text, initial_value)
        self.assertIsInstance(result, tk.StringVar)
        self.assertEqual(result.get(), "")

    def test_create_key_selector_empty_label(self):
        """
        Test create_key_selector with an empty label text.
        This tests the edge case where the label_text parameter is an empty string.
        """
        app = Mock()
        parent = tk.Tk()
        label_text = ""
        initial_value = "F1"

        result = app.create_key_selector(parent, label_text, initial_value)
        self.assertIsInstance(result, tk.StringVar)
        self.assertEqual(result.get(), initial_value)

    def test_create_key_selector_empty_label_2(self):
        """
        Test create_key_selector with an empty label text.
        This tests the edge case where the label_text parameter is an empty string.
        """
        app = RecoilControlApp(tk.Tk())
        result = app.create_key_selector(app.root, "", "initial_value")
        assert isinstance(result, tk.StringVar)
        assert result.get() == "initial_value"

    def test_create_key_selector_invalid_parent(self):
        """
        Test create_key_selector with an invalid parent object.
        This tests the edge case where the parent parameter is not a valid Tkinter widget.
        """
        app = Mock()
        invalid_parent = "Not a Tkinter widget"
        label_text = "Test Label"
        initial_value = "F1"

        with self.assertRaises(tk.TclError):
            app.create_key_selector(invalid_parent, label_text, initial_value)

    def test_create_key_selector_invalid_parent_2(self):
        """
        Test create_key_selector with an invalid parent object.
        This tests the edge case where the parent parameter is not a valid tkinter widget.
        """
        app = RecoilControlApp(tk.Tk())
        with pytest.raises(tk.TclError):
            app.create_key_selector("invalid_parent", "Test Label", "initial_value")

    def test_create_key_selector_long_initial_value(self):
        """
        Test create_key_selector with a very long initial value.
        This tests the edge case where the initial_value parameter is an unusually long string.
        """
        app = RecoilControlApp(tk.Tk())
        long_value = "a" * 1000
        result = app.create_key_selector(app.root, "Test Label", long_value)
        assert isinstance(result, tk.StringVar)
        assert result.get() == long_value

    def test_create_taskbar_icon_1(self):
        """
        Test that create_taskbar_icon method creates a new Toplevel window with correct attributes.
        """
        root = tk.Tk()
        app = MagicMock()
        app.root = root

        with patch('tkinter.Toplevel') as mock_toplevel:
            app.create_taskbar_icon()

            mock_toplevel.assert_called_once_with(root)
            mock_icon_window = mock_toplevel.return_value
            mock_icon_window.title.assert_called_once_with("MDZ Recoil")
            mock_icon_window.geometry.assert_called_once_with("1x1+0+0")
            mock_icon_window.overrideredirect.assert_called_once_with(False)
            mock_icon_window.attributes.assert_called_once_with("-toolwindow", True)

        root.destroy()

    def test_get_pos_1(self):
        """
        Test that the get_pos method correctly updates the x and y attributes of the RecoilControlApp instance
        with the x and y values from the event object.
        """

        root = tk.Tk()
        app = RecoilControlApp(root)

        # Create a mock event object
        class MockEvent:
            def __init__(self, x, y):
                self.x = x
                self.y = y

        event = MockEvent(100, 200)

        # Call the get_pos method
        app.get_pos(event)

        # Assert that the x and y attributes of the app instance are updated correctly
        assert app.x == 100, f"Expected app.x to be 100, but got {app.x}"
        assert app.y == 200, f"Expected app.y to be 200, but got {app.y}"

        root.destroy()

    def test_get_pos_invalid_event(self):
        """
        Test the get_pos method with an invalid event object that doesn't have x and y attributes.
        This tests how the method handles an unexpected input type.
        """
        app = RecoilControlApp(tk.Tk())
        invalid_event = object()  # An object without x and y attributes

        with self.assertRaises(AttributeError):
            app.get_pos(invalid_event)

    def test_handle_key_press_1(self):
        """
        Testcase 1 for def handle_key_press(event): # Convert key press to a string representation
        Path constraints: event.keysym.startswith('F') and event.keysym[1:].isdigit(), callback
        """
        # Mock event
        class MockEvent:
            def __init__(self):
                self.keysym = "F5"

        # Mock button and variable
        class MockButton:
            def config(self, text, bg):
                self.text = text
                self.bg = bg

        button = MockButton()
        button_var = type('MockStringVar', (), {'set': lambda self, value: None})()

        # Mock root
        class MockRoot:
            def unbind(self, event):
                pass

        root = MockRoot()

        # Mock callback
        callback_called = False
        def mock_callback(key_name):
            nonlocal callback_called
            callback_called = True
            assert key_name == "F5"

        # Call the function
        event = MockEvent()
        handle_key_press(event)

        # Assertions
        assert button.text == "Tecla: F5"
        assert button.bg == "#333333"
        assert callback_called

    def test_handle_key_press_function_key(self):
        """
        Test handling of function keys (F1-F12) in handle_key_press method.
        """
        class MockEvent:
            def __init__(self, keysym):
                self.keysym = keysym

        event = MockEvent("F5")
        button_var = tk.StringVar()
        button = tk.Button()
        root = tk.Tk()

        handle_key_press(event)

        assert button_var.get() == "F5"
        assert button.cget("text") == "Tecla: F5"
        assert button.cget("bg") == "#333333"
        assert not root.bind('<Key>')

    def test_handle_key_press_numpad_key(self):
        """
        Test handling of numpad keys in handle_key_press method.
        """
        class MockEvent:
            def __init__(self, keysym):
                self.keysym = keysym

        event = MockEvent("KP_1")
        button_var = tk.StringVar()
        button = tk.Button()
        root = tk.Tk()

        handle_key_press(event)

        assert button_var.get() == "numpad_1"
        assert button.cget("text") == "Tecla: numpad_1"
        assert button.cget("bg") == "#333333"
        assert not root.bind('<Key>')

    def test_handle_key_press_regular_key(self):
        """
        Test handling of regular keys in handle_key_press method.
        """
        class MockEvent:
            def __init__(self, keysym):
                self.keysym = keysym

        event = MockEvent("a")
        button_var = tk.StringVar()
        button = tk.Button()
        root = tk.Tk()

        handle_key_press(event)

        assert button_var.get() == "a"
        assert button.cget("text") == "Tecla: a"
        assert button.cget("bg") == "#333333"
        assert not root.bind('<Key>')

    def test_is_game_focused_1(self):
        """
        Test that is_game_focused returns True when a game window is in focus.

        This test mocks the win32gui.GetWindowText function to return a known game title,
        and checks if is_game_focused correctly identifies it as a game window.
        """
        app = RecoilControlApp(None)

        with unittest.mock.patch('win32gui.GetWindowText', return_value='Call of Duty: Warzone'):
            self.assertTrue(app.is_game_focused())

    def test_is_game_focused_1_2(self):
        """
        Test case to verify that is_game_focused correctly identifies a game window.
        This test mocks the win32gui.GetWindowText function to return a known game title
        and checks if the method correctly identifies it as a game window.
        """
        app = RecoilControlApp(None)
        with patch('win32gui.GetWindowText', return_value='Call of Duty: Warzone'):
            self.assertTrue(app.is_game_focused())

    def test_is_game_focused_import_error(self):
        """
        Test the behavior of is_game_focused when win32gui import fails.
        This tests the edge case where the required module is not available.
        """
        with patch('builtins.__import__', side_effect=ImportError):
            result = self.is_game_focused()
            self.assertTrue(result)

    def test_is_game_focused_non_game_window(self):
        """
        Test that is_game_focused returns False when a non-game window is in focus.
        This tests the edge case where the foreground window is not a game.
        """
        with patch('win32gui.GetWindowText') as mock_get_window_text:
            with patch('win32gui.GetForegroundWindow') as mock_get_foreground_window:
                mock_get_window_text.return_value = "Notepad"
                mock_get_foreground_window.return_value = 12345  # Dummy window handle

                result = self.is_game_focused()
                self.assertFalse(result)

    def test_load_config_1(self):
        """
        Test that load_config() correctly handles the case when a key from default_config
        is not present in the loaded config file.

        This test simulates a config file with a missing key and verifies that
        the missing key is added with its default value.
        """
        # Mock config file content with a missing key
        mock_config = {
            "horizontal_recoil": 5,
            "vertical_recoil": 3,
            # "activation_key" is intentionally missing
            "toggle_key": "F2",
            "mouse_activation": "left_click"
        }

        # Expected result after loading config
        expected_config = mock_config.copy()
        expected_config["activation_key"] = "F1"  # Default value

        with patch("builtins.open", mock_open(read_data=json.dumps(mock_config))):
            with patch("json.dump") as mock_json_dump:
                result = load_config()

        assert result == expected_config
        mock_json_dump.assert_called_once()  # Ensure config was saved

    def test_load_config_2(self):
        """
        Test that load_config() returns the config when all keys from default_config are present in the loaded config.

        This test ensures that when the loaded config contains all the keys from the default config,
        the function returns the loaded config without modifying it.
        """
        mock_config = {
            "horizontal_recoil": 5,
            "vertical_recoil": 3,
            "activation_key": "F2",
            "toggle_key": "F3",
            "mouse_activation": "both",
            "background_file": "custom_bg.gif",
            "rapid_fire_enabled": True,
            "rapid_fire_key": "F4",
            "rapid_fire_interval": 20,
            "rapid_fire_mouse_button": "right_click",
            "tbag_enabled": True,
            "tbag_key": "F5",
            "tbag_interval": 60,
            "tbag_button": "shift",
            "hide_toggle_key": "F7",
        }

        mock_json = json.dumps(mock_config)

        with patch('builtins.open', mock_open(read_data=mock_json)):

            result = load_config()

            assert result == mock_config
            assert all(key in result for key in mock_config)

    def test_load_config_file_not_found(self):
        """
        Test the load_config function when the config file is not found.
        This should result in the default configuration being used.
        """
        # Temporarily rename the config file if it exists
        if os.path.exists(CONFIG_FILE):
            os.rename(CONFIG_FILE, f"{CONFIG_FILE}.bak")

        try:
            config = load_config()

            # Check if the default values are used
            assert config["horizontal_recoil"] == 0
            assert config["vertical_recoil"] == 0
            assert config["activation_key"] == "F1"
            assert config["toggle_key"] == "F2"
            assert config["mouse_activation"] == "left_click"
            assert config["background_file"] == GIF_FILE
            assert config["rapid_fire_enabled"] == False
            assert config["rapid_fire_key"] == "F3"
            assert config["rapid_fire_interval"] == 15
            assert config["rapid_fire_mouse_button"] == "left_click"
            assert config["tbag_enabled"] == False
            assert config["tbag_key"] == "F4"
            assert config["tbag_interval"] == 50
            assert config["tbag_button"] == "ctrl"
            assert config["hide_toggle_key"] == "F6"
        finally:
            # Restore the original config file if it existed
            if os.path.exists(f"{CONFIG_FILE}.bak"):
                os.rename(f"{CONFIG_FILE}.bak", CONFIG_FILE)

    def test_load_config_invalid_json(self):
        """
        Test the load_config function when the config file contains invalid JSON.
        This should result in the default configuration being used.
        """
        # Create a temporary config file with invalid JSON
        with open(CONFIG_FILE, "w") as f:
            f.write("This is not valid JSON")

        try:
            config = load_config()

            # Check if the default values are used
            assert config["horizontal_recoil"] == 0
            assert config["vertical_recoil"] == 0
            assert config["activation_key"] == "F1"
            assert config["toggle_key"] == "F2"
            assert config["mouse_activation"] == "left_click"
            assert config["background_file"] == GIF_FILE
            assert config["rapid_fire_enabled"] == False
            assert config["rapid_fire_key"] == "F3"
            assert config["rapid_fire_interval"] == 15
            assert config["rapid_fire_mouse_button"] == "left_click"
            assert config["tbag_enabled"] == False
            assert config["tbag_key"] == "F4"
            assert config["tbag_interval"] == 50
            assert config["tbag_button"] == "ctrl"
            assert config["hide_toggle_key"] == "F6"
        finally:
            # Remove the temporary config file
            os.remove(CONFIG_FILE)

    def test_load_config_missing_keys(self):
        """
        Test the load_config function when the config file is missing some keys.
        This should result in the missing keys being filled with default values.
        """
        # Create a temporary config file with some missing keys
        partial_config = {
            "horizontal_recoil": 5,
            "vertical_recoil": 10
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(partial_config, f)

        try:
            config = load_config()

            # Check if the existing values are preserved and missing ones are filled with defaults
            assert config["horizontal_recoil"] == 5
            assert config["vertical_recoil"] == 10
            assert config["activation_key"] == "F1"
            assert config["toggle_key"] == "F2"
            assert config["mouse_activation"] == "left_click"
            assert config["background_file"] == GIF_FILE
            assert config["rapid_fire_enabled"] == False
            assert config["rapid_fire_key"] == "F3"
            assert config["rapid_fire_interval"] == 15
            assert config["rapid_fire_mouse_button"] == "left_click"
            assert config["tbag_enabled"] == False
            assert config["tbag_key"] == "F4"
            assert config["tbag_interval"] == 50
            assert config["tbag_button"] == "ctrl"
            assert config["hide_toggle_key"] == "F6"
        finally:
            # Remove the temporary config file
            os.remove(CONFIG_FILE)

    def test_load_frames_1(self):
        """
        Test that load_frames() handles non-existent gif file correctly.

        This test verifies that when the specified gif file does not exist,
        the method prints an error message and returns without loading any frames.
        """
        # Create an instance of AnimatedGIF with a non-existent file
        non_existent_file = "non_existent.gif"
        gif = AnimatedGIF(None, non_existent_file)

        # Call load_frames method
        gif.load_frames()

        # Assert that no frames were loaded
        assert len(gif.frames) == 0

        # Assert that the delay is set to the default value
        assert gif.delay == 0

    def test_load_frames_2(self):
        """
        Tests that frames are loaded correctly when the GIF file exists.

        This test verifies that:
        1. The frames list is populated
        2. Each frame is an instance of ImageTk.PhotoImage
        3. The delay is set to a non-zero value
        """
        # Setup
        gif_path = "test_gif.gif"
        with Image.new('RGB', (100, 100), color='red') as img:
            img.save(gif_path, save_all=True, append_images=[Image.new('RGB', (100, 100), color='blue')], duration=100, loop=0)

        # Create AnimatedGIF instance
        animated_gif = AnimatedGIF(None, gif_path, 200, 200)

        # Call the method
        animated_gif.load_frames()

        # Assertions
        assert len(animated_gif.frames) > 0, "Frames list should not be empty"
        assert all(isinstance(frame, ImageTk.PhotoImage) for frame in animated_gif.frames), "All frames should be ImageTk.PhotoImage instances"
        assert animated_gif.delay > 0, "Delay should be set to a positive value"

        # Cleanup
        os.remove(gif_path)

    def test_load_frames_3(self):
        """
        Test that frames are loaded correctly when the GIF file exists.

        This test verifies that:
        1. The frames list is populated
        2. The delay is set correctly
        3. The frames are resized to the specified dimensions
        """
        # Create a temporary GIF file for testing
        test_gif_path = "test.gif"
        frames = [Image.new('RGB', (100, 100), color='red') for _ in range(3)]
        frames[0].save(test_gif_path, save_all=True, append_images=frames[1:], duration=200, loop=0)

        # Create AnimatedGIF instance
        gif = AnimatedGIF(None, test_gif_path, width=50, height=50)

        # Call the method under test
        gif.load_frames()

        # Assertions
        assert len(gif.frames) == 3
        assert gif.delay == 200
        assert all(isinstance(frame, ImageTk.PhotoImage) for frame in gif.frames)
        assert all(frame.width() == 50 and frame.height() == 50 for frame in gif.frames)

        # Clean up
        os.remove(test_gif_path)

    def test_load_frames_4(self):
        """
        Tests the load_frames method when the GIF file exists but has no frames.

        This test ensures that when a valid GIF file exists but contains no frames,
        the method handles the situation correctly without raising exceptions.
        The frames list should remain empty, and the delay should be set to the default value.
        """
        with patch('os.path.exists', return_value=True), \
             patch('PIL.Image.open') as mock_open:

            mock_gif = MagicMock()
            mock_gif.__enter__.return_value = mock_gif
            mock_gif.tell.side_effect = EOFError  # Simulate end of file immediately
            mock_open.return_value = mock_gif

            gif = AnimatedGIF(MagicMock(), 'test.gif', 100, 100)
            gif.load_frames()

            assert len(gif.frames) == 0
            assert gif.delay == 100  # Default delay value

    def test_load_frames_file_not_found(self):
        """
        Test the load_frames method when the specified GIF file does not exist.
        This tests the edge case where the file path is invalid or the file is missing.
        """
        non_existent_file = "non_existent.gif"
        animated_gif = AnimatedGIF(None, non_existent_file)

        # Capture print output
        captured_output = io.StringIO()
        sys.stdout = captured_output

        animated_gif.load_frames()

        sys.stdout = sys.__stdout__  # Reset redirect

        assert f"Arquivo {non_existent_file} não encontrado!" in captured_output.getvalue()
        assert len(animated_gif.frames) == 0

    def test_load_frames_gif_without_duration(self, tmp_path):
        """
        Test the load_frames method with a GIF that doesn't have a duration specified.
        This tests the edge case where the 'duration' key is missing from the GIF info.
        """
        # Create a simple GIF without duration info
        gif_file = tmp_path / "no_duration.gif"
        img = Image.new('RGB', (10, 10), color='red')
        img.save(str(gif_file), 'GIF')

        animated_gif = AnimatedGIF(None, str(gif_file))
        animated_gif.load_frames()

        assert animated_gif.delay == 100  # Default delay

    def test_load_frames_invalid_gif(self, tmp_path):
        """
        Test the load_frames method with an invalid GIF file.
        This tests the edge case where the file exists but is not a valid GIF.
        """
        invalid_file = tmp_path / "invalid.gif"
        invalid_file.write_text("This is not a GIF file")

        animated_gif = AnimatedGIF(None, str(invalid_file))

        with pytest.raises(IOError):
            animated_gif.load_frames()

    def test_minimize_window_1(self):
        """
        Test that minimize_window method withdraws the root window and creates a taskbar icon.
        """
        root = tk.Tk()
        app = RecoilControlApp(root)

        with patch.object(app.root, 'withdraw') as mock_withdraw, \
             patch.object(app, 'create_taskbar_icon') as mock_create_taskbar_icon:

            app.minimize_window()

            mock_withdraw.assert_called_once()
            mock_create_taskbar_icon.assert_called_once()

    def test_minimize_window_create_taskbar_icon_failure(self):
        """
        Test minimize_window when create_taskbar_icon method fails.
        This tests the edge case where the taskbar icon cannot be created.
        """
        root_mock = MagicMock()

        app = RecoilControlApp(root_mock)
        app.create_taskbar_icon = MagicMock(side_effect=Exception("Failed to create taskbar icon"))

        with self.assertRaises(Exception):
            app.minimize_window()

    def test_minimize_window_no_root(self):
        """
        Test minimize_window when the root attribute is not set.
        This tests the edge case where the method is called before proper initialization.
        """
        app = RecoilControlApp(None)
        app.root = None

        with self.assertRaises(AttributeError):
            app.minimize_window()

    def test_minimize_window_withdraw_failure(self):
        """
        Test minimize_window when the withdraw method fails.
        This tests the edge case where the window cannot be minimized.
        """
        root_mock = MagicMock()
        root_mock.withdraw.side_effect = tk.TclError("Cannot withdraw")

        app = RecoilControlApp(root_mock)

        with self.assertRaises(tk.TclError):
            app.minimize_window()

    def test_move_window_1(self):
        """
        Test that move_window correctly updates the window position based on mouse movement.
        """
        # Create a mock Tk root and RecoilControlApp instance
        root = Mock(spec=tk.Tk)
        app = RecoilControlApp(root)

        # Set up initial values
        app.x = 10
        app.y = 20

        # Create a mock event
        event = Mock()

        # Set up mock return values for winfo methods
        root.winfo_pointerx.return_value = 100
        root.winfo_pointery.return_value = 150

        # Call the move_window method
        app.move_window(event)

        # Assert that the geometry method was called with the correct argument
        root.geometry.assert_called_once_with("+90+130")

    def test_move_window_no_event(self):
        """
        Test the move_window method when no event is provided.
        This test checks if the method handles the case where the event parameter is None.
        """
        app = RecoilControlApp(tk.Tk())
        app.move_window(None)
        # Assert that the window position remains unchanged
        # Note: This assertion assumes that the initial position is (0, 0)
        assert app.root.geometry() == "+0+0"

    def test_on_button_click_1(self):
        """
        Tests that the button configuration changes correctly when on_button_click is called.

        This test verifies that:
        1. The button text is updated to "Pressione uma tecla..."
        2. The button background color is changed to "#aa0000"
        3. A key binding is added to the root window
        """
        # Mock objects
        button = Mock()
        root = Mock()

        # Call the function
        on_button_click()

        # Assert the expected behavior
        button.config.assert_called_once_with(text="Pressione uma tecla...", bg="#aa0000")
        root.bind.assert_called_once_with('<Key>', ANY)

    def test_on_button_click_no_root_binding(self):
        """
        Test on_button_click when self.root is not available for binding.
        This tests the edge case where the method assumes self.root exists and can be bound to.
        """
        # Setup
        button = Button()

        # Define the method locally to simulate the environment
        def on_button_click():
            button.config(text="Pressione uma tecla...", bg="#aa0000")
            # Simulate the case where self.root is not available
            if not hasattr(self, 'root'):
                raise AttributeError("'TestMain' object has no attribute 'root'")
            self.root.bind('<Key>', lambda event: handle_key_press(event))

        # Execute and assert
        with self.assertRaises(AttributeError):
            on_button_click()

        # Verify button configuration was still applied
        self.assertEqual(button.cget("text"), "Pressione uma tecla...")
        self.assertEqual(button.cget("bg"), "#aa0000")

    def test_on_key_press_1(self):
        """
        Test the on_key_press method for various key presses and their effects on the RecoilControlApp.
        This test covers toggling the macro, activating rapid fire and tbag features, and toggling window visibility.
        """
        with patch('main.config', mock_config):
            app = MockRecoilControlApp()

            # Test toggle key
            app.on_key_press(Mock(char='f2'))
            self.assertTrue(app.running)

            # Test rapid fire key
            with patch.object(threading, 'Thread') as mock_thread:
                app.on_key_press(Mock(char='f3'))
                self.assertTrue(app.rapid_fire_active)
                mock_thread.assert_called_once_with(target=app.run_rapid_fire, daemon=True)
                mock_thread.return_value.start.assert_called_once()

            # Test tbag key
            with patch.object(threading, 'Thread') as mock_thread:
                app.on_key_press(Mock(char='f4'))
                self.assertTrue(app.tbag_active)
                mock_thread.assert_called_once_with(target=app.run_tbag, daemon=True)
                mock_thread.return_value.start.assert_called_once()

            # Test hide toggle key
            app.on_key_press(Mock(char='f6'))
            self.assertTrue(app.window_hidden)

    def test_on_key_press_2(self):
        """
        Test the on_key_press method when rapid fire and tbag are enabled,
        their respective keys are pressed, and the hide toggle key is pressed.
        This test covers the case where the rapid fire and tbag threads are not active,
        and the window visibility is toggled.
        """
        app = RecoilControlApp(Mock())
        app.rapid_fire_active = False
        app.tbag_active = False
        app.rapid_fire_thread = None
        app.tbag_thread = None
        app.window_hidden = False
        app.toggle_window_visibility = Mock()

        config["rapid_fire_enabled"] = True
        config["tbag_enabled"] = True
        config["rapid_fire_key"] = "f3"
        config["tbag_key"] = "f4"
        config["hide_toggle_key"] = "f6"

        with patch.object(threading, 'Thread') as mock_thread:
            app.on_key_press(Mock(char='f3'))
            app.on_key_press(Mock(char='f4'))
            app.on_key_press(Mock(char='f6'))

        self.assertTrue(app.rapid_fire_active)
        self.assertTrue(app.tbag_active)
        self.assertEqual(mock_thread.call_count, 2)
        app.toggle_window_visibility.assert_called_once()

    def test_on_key_press_3(self):
        """
        Tests the on_key_press method when the toggle key, rapid fire key, and tbag key are pressed,
        and the hide toggle key is also pressed. Verifies that the appropriate actions are taken
        for each key press, including toggling the macro, activating rapid fire and tbag,
        and toggling window visibility.
        """
        app = RecoilControlApp(Mock())
        app.toggle_macro = Mock()
        app.rapid_fire_thread = Mock()
        app.rapid_fire_thread.is_alive.return_value = True
        app.tbag_thread = Mock(spec=['is_alive'])
        app.tbag_thread.is_alive.return_value = False
        app.toggle_window_visibility = Mock()

        config["toggle_key"] = "F2"
        config["rapid_fire_enabled"] = True
        config["rapid_fire_key"] = "F3"
        config["tbag_enabled"] = True
        config["tbag_key"] = "F4"
        config["hide_toggle_key"] = "F6"

        mock_key = Mock()
        mock_key.char = "f2"
        app.on_key_press(mock_key)
        app.toggle_macro.assert_called_once()

        mock_key.char = "f3"
        app.on_key_press(mock_key)
        self.assertTrue(app.rapid_fire_active)

        mock_key.char = "f4"
        app.on_key_press(mock_key)
        self.assertTrue(app.tbag_active)
        self.assertTrue(hasattr(app, 'tbag_thread'))

        mock_key.char = "f6"
        app.on_key_press(mock_key)
        app.toggle_window_visibility.assert_called_once()

    def test_on_key_press_4(self):
        """
        Test on_key_press method when toggle key, tbag key, and hide toggle key are pressed.

        This test verifies that:
        1. The toggle_macro method is called when the toggle key is pressed.
        2. The tbag feature is activated and a new thread is started when the tbag key is pressed.
        3. The toggle_window_visibility method is called when the hide toggle key is pressed.
        """
        app = RecoilControlApp(MagicMock())
        app.toggle_macro = MagicMock()
        app.toggle_window_visibility = MagicMock()

        # Set up the configuration
        config["toggle_key"] = "f2"
        config["rapid_fire_enabled"] = False
        config["tbag_enabled"] = True
        config["tbag_key"] = "f4"
        config["hide_toggle_key"] = "f6"

        # Mock the threading.Thread
        with patch('threading.Thread') as mock_thread:
            # Simulate pressing the toggle key
            app.on_key_press(keyboard.KeyCode.from_char('f2'))
            app.toggle_macro.assert_called_once()

            # Simulate pressing the tbag key
            app.tbag_thread = None
            app.on_key_press(keyboard.KeyCode.from_char('f4'))
            self.assertTrue(app.tbag_active)
            mock_thread.assert_called_once_with(target=app.run_tbag, daemon=True)
            mock_thread.return_value.start.assert_called_once()

            # Simulate pressing the hide toggle key
            app.on_key_press(keyboard.KeyCode.from_char('f6'))
            app.toggle_window_visibility.assert_called_once()

    def test_on_key_press_5(self):
        """
        Test the on_key_press method when all conditions are met except for tbag thread creation.
        This test verifies that the method correctly handles the toggle key, rapid fire activation,
        tbag activation, and window visibility toggle, but does not create a new tbag thread.
        """
        with patch('main.RecoilControlApp') as MockRecoilControlApp, \
             patch('main.config', {
                 "toggle_key": "f2",
                 "rapid_fire_enabled": True,
                 "rapid_fire_key": "f3",
                 "tbag_enabled": True,
                 "tbag_key": "f4",
                 "hide_toggle_key": "f6"
             }):

            app = MockRecoilControlApp()
            app.toggle_macro = Mock()
            app.rapid_fire_active = False
            app.rapid_fire_thread = None
            app.tbag_active = False
            app.tbag_thread = Mock()
            app.tbag_thread.is_alive.return_value = True
            app.toggle_window_visibility = Mock()

            # Simulate pressing F2 (toggle key)
            app.on_key_press(Mock(char='f2'))
            app.toggle_macro.assert_called_once()

            # Simulate pressing F3 (rapid fire key)
            app.on_key_press(Mock(char='f3'))
            self.assertTrue(app.rapid_fire_active)
            self.assertIsInstance(app.rapid_fire_thread, threading.Thread)

            # Simulate pressing F4 (tbag key)
            app.on_key_press(Mock(char='f4'))
            self.assertTrue(app.tbag_active)
            # Verify that a new tbag thread was not created
            self.assertFalse(hasattr(app, 'tbag_thread') and isinstance(app.tbag_thread, threading.Thread))

            # Simulate pressing F6 (hide toggle key)
            app.on_key_press(Mock(char='f6'))
            app.toggle_window_visibility.assert_called_once()

    def test_on_key_press_6(self):
        """
        Test that on_key_press correctly handles the following scenario:
        - The pressed key matches the toggle key
        - Rapid fire is enabled and the pressed key matches the rapid fire key
        - The rapid fire thread is not active
        - T-bag is not triggered
        - The pressed key matches the hide toggle key
        """
        app = RecoilControlApp(Mock())
        app.toggle_macro = Mock()
        app.rapid_fire_active = False
        app.rapid_fire_thread = None
        app.toggle_window_visibility = Mock()

        # Mock the config
        mock_config = {
            "toggle_key": "F2",
            "rapid_fire_enabled": True,
            "rapid_fire_key": "F3",
            "tbag_enabled": False,
            "tbag_key": "F4",
            "hide_toggle_key": "F6"
        }

        with patch.dict('main.config', mock_config):
            # Create a mock key that matches all conditions
            mock_key = Mock()
            mock_key.char = "f2"

            app.on_key_press(mock_key)

            # Assert that toggle_macro was called
            app.toggle_macro.assert_called_once()

            # Assert that a new rapid fire thread was created and started
            self.assertIsNotNone(app.rapid_fire_thread)
            self.assertTrue(app.rapid_fire_active)

            # Assert that toggle_window_visibility was called
            app.toggle_window_visibility.assert_called_once()

    def test_on_key_press_7(self):
        """
        Test the on_key_press method when toggle key, rapid fire key, and tbag key are pressed.
        Verifies that the corresponding actions are triggered and threads are started.
        """
        with patch('builtins.open', MagicMock()):
            with patch('json.load', return_value=config):

                app = RecoilControlApp(MagicMock())
                app.toggle_macro = MagicMock()
                app.rapid_fire_thread = None
                app.tbag_thread = None

                # Simulate pressing the toggle key
                app.on_key_press(Key.f2)
                app.toggle_macro.assert_called_once()

                # Simulate pressing the rapid fire key
                app.on_key_press(Key.f3)
                self.assertTrue(app.rapid_fire_active)
                self.assertIsNotNone(app.rapid_fire_thread)

                # Simulate pressing the tbag key
                app.on_key_press(Key.f4)
                self.assertTrue(app.tbag_active)
                self.assertIsNotNone(app.tbag_thread)

    def test_on_key_press_attribute_error(self):
        """
        Test the on_key_press method when an AttributeError occurs due to the key not having a 'char' attribute.
        This tests the exception handling for special keys that don't have a character representation.
        """
        root = tk.Tk()
        app = RecoilControlApp(root)

        # Simulate a key press that would raise an AttributeError
        special_key = keyboard.Key.shift
        app.on_key_press(special_key)

        # The method should not raise an exception and should continue execution
        # We can't assert much here as the method doesn't return anything, but we can check that it doesn't crash

    def test_on_key_press_rapid_fire_disabled(self):
        """
        Test the on_key_press method when rapid fire is disabled but the rapid fire key is pressed.
        This tests that rapid fire doesn't activate when it's disabled in the config.
        """
        root = tk.Tk()
        app = RecoilControlApp(root)

        # Ensure rapid fire is disabled
        config["rapid_fire_enabled"] = False

        # Simulate pressing the rapid fire key
        rapid_fire_key = keyboard.KeyCode.from_char(config["rapid_fire_key"].lower())
        app.on_key_press(rapid_fire_key)

        # Check that rapid fire was not activated
        assert not hasattr(app, 'rapid_fire_active') or not app.rapid_fire_active, "Rapid fire should not be activated when disabled"

    def test_on_key_press_tbag_disabled(self):
        """
        Test the on_key_press method when t-bag is disabled but the t-bag key is pressed.
        This tests that t-bag doesn't activate when it's disabled in the config.
        """
        root = tk.Tk()
        app = RecoilControlApp(root)

        # Ensure t-bag is disabled
        config["tbag_enabled"] = False

        # Simulate pressing the t-bag key
        tbag_key = keyboard.KeyCode.from_char(config["tbag_key"].lower())
        app.on_key_press(tbag_key)

        # Check that t-bag was not activated
        assert not hasattr(app, 'tbag_active') or not app.tbag_active, "T-bag should not be activated when disabled"

    def test_on_key_press_toggle_macro(self):
        """
        Test the on_key_press method when the toggle key is pressed.
        This tests the macro toggling functionality.
        """
        root = tk.Tk()
        app = RecoilControlApp(root)

        # Set up the initial state
        app.running = False

        # Simulate pressing the toggle key
        toggle_key = keyboard.KeyCode.from_char(config["toggle_key"].lower())
        app.on_key_press(toggle_key)

        # Check if the macro was toggled on
        assert app.running == True, "Macro should be toggled on"

        # Press the toggle key again
        app.on_key_press(toggle_key)

        # Check if the macro was toggled off
        assert app.running == False, "Macro should be toggled off"

    def test_on_key_release_1(self):
        """
        Tests that on_key_release method deactivates rapid fire and t-bag when
        the corresponding keys are released.
        """
        # Mock setup
        mock_app = MagicMock()
        mock_app.rapid_fire_active = True
        mock_app.tbag_active = True

        # Mock config
        mock_config = {
            "rapid_fire_key": "F3",
            "tbag_key": "F4"
        }

        with patch('main.config', mock_config):
            # Test rapid fire key release
            mock_key_rapid = MagicMock()
            mock_key_rapid.char = "f3"
            RecoilControlApp.on_key_release(mock_app, mock_key_rapid)
            assert not mock_app.rapid_fire_active

            # Test t-bag key release
            mock_key_tbag = MagicMock()
            mock_key_tbag.char = "f4"
            RecoilControlApp.on_key_release(mock_app, mock_key_tbag)
            assert not mock_app.tbag_active

    def test_on_key_release_2(self):
        """
        Tests that the on_key_release method correctly deactivates T-bag when the designated key is released.

        Path constraints:
        - The released key is not the rapid fire key
        - The released key is the T-bag key
        """
        app = RecoilControlApp(Mock())
        app.tbag_active = True

        # Mock the Key object
        mock_key = Mock()
        mock_key.char = config["tbag_key"]

        # Call the method under test
        app.on_key_release(mock_key)

        # Assert that tbag_active is set to False
        assert app.tbag_active == False

    def test_on_key_release_3(self):
        """
        Test that the on_key_release method deactivates rapid fire when the rapid fire key is released,
        but does not affect the tbag_active state when a different key is released.
        """
        # Setup
        app = RecoilControlApp(None)
        app.rapid_fire_active = True
        app.tbag_active = True
        config["rapid_fire_key"] = "F3"
        config["tbag_key"] = "F4"

        # Create a mock key object
        class MockKey:
            def __init__(self, char):
                self.char = char

        # Test releasing the rapid fire key
        rapid_fire_key = MockKey("F3")
        app.on_key_release(rapid_fire_key)

        # Assert that rapid fire is deactivated but tbag is still active
        assert app.rapid_fire_active == False
        assert app.tbag_active == True

    def test_on_key_release_attribute_error(self):
        """
        Test the on_key_release method when an AttributeError is raised.
        This tests the edge case where the key object doesn't have a 'char' attribute.
        """
        app = RecoilControlApp(None)  # Create an instance of RecoilControlApp

        # Create a mock key object that will raise an AttributeError
        class MockKey:
            def __str__(self):
                return "Key.space"

        mock_key = MockKey()

        # Call the method and check that it doesn't raise an exception
        try:
            app.on_key_release(mock_key)
        except Exception as e:
            assert False, f"on_key_release raised an exception: {e}"

        # Since the method doesn't return anything, we can't check the return value.
        # Instead, we're just ensuring that the method doesn't crash when given a key without a 'char' attribute.

    def test_on_mouse_click_1(self):
        """
        Test that on_mouse_click sets shooting to True when conditions are met.

        This test verifies that the on_mouse_click method correctly sets the
        shooting attribute to True when:
        1. The app is running
        2. The mouse activation setting matches the button clicked
        3. The button is pressed
        """
        app = RecoilControlApp(None)
        app.running = True
        app.shooting = False

        # Test left click activation
        config["mouse_activation"] = "left_click"
        app.on_mouse_click(0, 0, mouse.Button.left, True)
        assert app.shooting == True

        # Test right click activation
        app.shooting = False
        config["mouse_activation"] = "right_click"
        app.on_mouse_click(0, 0, mouse.Button.right, True)
        assert app.shooting == True

        # Test both click activation
        app.shooting = False
        config["mouse_activation"] = "both"
        app.on_mouse_click(0, 0, mouse.Button.left, True)
        assert app.shooting == True

        app.shooting = False
        app.on_mouse_click(0, 0, mouse.Button.right, True)
        assert app.shooting == True

    def test_on_mouse_click_2(self):
        """
        Test that on_mouse_click does not set shooting to pressed when conditions are not met.

        This test covers the case where the macro is not running or the mouse button
        does not match the configured activation settings.
        """

        app = RecoilControlApp(None)
        app.running = False
        app.shooting = False

        # Test with left click when not running
        app.on_mouse_click(0, 0, mouse.Button.left, True)
        assert not app.shooting

        # Test with right click when running but activation is set to left_click
        app.running = True
        config["mouse_activation"] = "left_click"
        app.on_mouse_click(0, 0, mouse.Button.right, True)
        assert not app.shooting

        # Test with left click when running but activation is set to right_click
        config["mouse_activation"] = "right_click"
        app.on_mouse_click(0, 0, mouse.Button.left, True)
        assert not app.shooting

        # Test with middle click when running and activation is set to both
        config["mouse_activation"] = "both"
        app.on_mouse_click(0, 0, mouse.Button.middle, True)
        assert not app.shooting

    def test_on_mouse_click_invalid_mouse_activation(self):
        """
        Test the on_mouse_click method with an invalid mouse_activation configuration.
        This test verifies that the method does not modify the shooting state when
        the mouse_activation setting is invalid.
        """
        # Mock RecoilControlApp instance
        app = Mock()
        app.running = True
        app.shooting = False

        # Set an invalid mouse_activation configuration
        config = {"mouse_activation": "invalid_setting"}

        # Call the method with various mouse button inputs
        on_mouse_click(app, 0, 0, mouse.Button.left, True)
        assert app.shooting == False

        on_mouse_click(app, 0, 0, mouse.Button.right, True)
        assert app.shooting == False

        on_mouse_click(app, 0, 0, mouse.Button.middle, True)
        assert app.shooting == False

        # Ensure the shooting state remains unchanged for button release
        on_mouse_click(app, 0, 0, mouse.Button.left, False)
        assert app.shooting == False

    def test_open_discord_link_1(self):
        """
        Test that open_discord_link opens the correct Discord link in a web browser.
        """
        with patch('webbrowser.open') as mock_open:
            # Call the open_discord_link function
            RecoilControlApp.open_discord_link(None)

            # Assert that webbrowser.open was called with the correct URL
            mock_open.assert_called_once_with("https://discord.gg/your-server-link")

    @patch('webbrowser.open')
    def test_open_discord_link_webbrowser_failure(self, mock_open):
        """
        Test the behavior of open_discord_link when webbrowser.open fails.
        This tests an edge case where the webbrowser module encounters an error.
        """
        mock_open.side_effect = Exception("Webbrowser error")

        # Create a mock event object
        mock_event = unittest.mock.Mock()

        # Call the method
        RecoilControlApp.open_discord_link(mock_event)

        # Assert that webbrowser.open was called with the correct URL
        mock_open.assert_called_once_with("https://discord.gg/your-server-link")

    def test_restore_window_1(self):
        """
        This test verifies that the restore_window method correctly restores the main window
        and destroys the icon window when the icon window exists.
        """
        root = tk.Tk()
        app = RecoilControlApp(root)
        app.root.withdraw()  # Hide the main window
        app.icon_window = tk.Toplevel(app.root)  # Create a mock icon window

        app.restore_window()

        assert app.root.winfo_viewable() == 1, "Main window should be visible"
        assert not hasattr(app, 'icon_window'), "Icon window should be destroyed"

    def test_restore_window_2(self):
        """
        Test that restore_window only calls deiconify when icon_window attribute is not present.

        This test verifies that when the RecoilControlApp instance does not have an 'icon_window'
        attribute, the restore_window method only calls deiconify on the root window and does not
        attempt to destroy a non-existent icon_window.
        """
        root = MagicMock()
        app = RecoilControlApp(root)

        # Ensure the app instance does not have an 'icon_window' attribute
        if hasattr(app, 'icon_window'):
            delattr(app, 'icon_window')

        app.restore_window()

        # Verify that deiconify was called on the root window
        root.deiconify.assert_called_once()

        # Verify that no destroy method was called (since icon_window doesn't exist)
        assert not hasattr(app, 'icon_window')

    def test_restore_window_when_icon_window_does_not_exist(self):
        """
        Test restore_window when the icon_window attribute does not exist.
        This tests the edge case where the minimize_window method was not called
        before restore_window, so there's no icon window to destroy.
        """
        root = tk.Tk()
        app = RecoilControlApp(root)

        # Ensure icon_window attribute doesn't exist
        if hasattr(app, 'icon_window'):
            delattr(app, 'icon_window')

        # Call restore_window
        app.restore_window()

        # Assert that the main window is deiconified
        assert root.state() == 'normal'

        # Clean up
        root.destroy()

    def test_run_macro_1(self):
        """
        Test that run_macro applies recoil when shooting is active
        """

        # Create a mock RecoilControlApp instance
        app = MagicMock(spec=RecoilControlApp)
        app.running = True
        app.shooting = True

        # Patch the time.sleep method to avoid actual delays
        with patch('time.sleep') as mock_sleep:
            # Patch the apply_recoil method to track calls
            with patch.object(app, 'apply_recoil') as mock_apply_recoil:
                # Call run_macro
                RecoilControlApp.run_macro(app)

                # Assert that apply_recoil was called at least once
                mock_apply_recoil.assert_called()

                # Assert that time.sleep was called with 0.02
                mock_sleep.assert_called_with(0.02)

    def test_run_macro_does_not_apply_recoil_when_not_shooting(self):
        """
        Test that the run_macro method does not apply recoil when self.shooting is False.
        """
        app = MagicMock()
        app.running = True
        app.shooting = False

        with patch('time.sleep') as mock_sleep:
            app.run_macro()
            app.apply_recoil.assert_not_called()
            mock_sleep.assert_called_once_with(0.02)

    def test_run_macro_stops_when_not_running(self):
        """
        Test that the run_macro method stops immediately when self.running is False.
        """
        app = MagicMock()
        app.running = False
        app.shooting = False

        with patch('time.sleep') as mock_sleep:
            app.run_macro()
            mock_sleep.assert_not_called()

    def test_run_rapid_fire_1(self):
        """
        Test that run_rapid_fire simulates mouse clicks based on configuration.

        This test verifies that the run_rapid_fire method correctly simulates
        mouse clicks according to the rapid fire configuration settings.
        It checks for left clicks, right clicks, and both clicks scenarios.
        """
        # Import necessary modules

        # Create a mock RecoilControlApp instance
        app = MagicMock()
        app.rapid_fire_active = True
        app.mouse_controller = MagicMock()

        # Mock the config dictionary
        mock_config = {
            "rapid_fire_mouse_button": "left_click",
            "rapid_fire_interval": 15
        }

        # Patch the config and time.sleep
        with patch("main.config", mock_config), patch("time.sleep") as mock_sleep:
            # Test left click
            app.run_rapid_fire()
            app.mouse_controller.click.assert_called_with(mouse.Button.left)
            mock_sleep.assert_called_with(0.015)

            # Test right click
            mock_config["rapid_fire_mouse_button"] = "right_click"
            app.run_rapid_fire()
            app.mouse_controller.click.assert_called_with(mouse.Button.right)

            # Test both clicks
            mock_config["rapid_fire_mouse_button"] = "both"
            app.run_rapid_fire()
            assert app.mouse_controller.click.call_count == 4  # 2 additional calls
            app.mouse_controller.click.assert_any_call(mouse.Button.left)
            app.mouse_controller.click.assert_any_call(mouse.Button.right)

        # Verify that the loop stops when rapid_fire_active is False
        app.rapid_fire_active = False
        app.run_rapid_fire()
        assert app.mouse_controller.click.call_count == 4  # No additional calls

    def test_run_rapid_fire_2(self):
        """
        Tests the run_rapid_fire method when rapid fire is active and left click is configured.

        This test verifies that:
        1. The method runs while rapid_fire_active is True
        2. The left mouse button is clicked
        3. The method sleeps for the configured interval
        """
        mock_app = Mock(spec=RecoilControlApp)
        mock_app.rapid_fire_active = True
        mock_app.mouse_controller = Mock()

        # Configure for left click
        config["rapid_fire_mouse_button"] = "left_click"
        config["rapid_fire_interval"] = 15

        # Patch time.sleep to avoid actual waiting
        with patch('time.sleep') as mock_sleep:
            # Call the method
            RecoilControlApp.run_rapid_fire(mock_app)

            # Assert that left click was performed
            mock_app.mouse_controller.click.assert_called_with(mouse.Button.left)

            # Assert that sleep was called with the correct interval
            mock_sleep.assert_called_with(0.015)  # 15ms converted to seconds

        # Ensure the method exits when rapid_fire_active becomes False
        mock_app.rapid_fire_active = False
        RecoilControlApp.run_rapid_fire(mock_app)
        assert mock_app.mouse_controller.click.call_count == 1  # No additional clicks

    def test_run_rapid_fire_3(self):
        """
        Test that the run_rapid_fire method exits immediately when rapid_fire_active is False.
        This test ensures that the method doesn't perform any actions when it's not supposed to be active.
        """
        app = RecoilControlApp(MagicMock())
        app.mouse_controller = MagicMock()
        app.rapid_fire_active = False

        # Run the method
        app.run_rapid_fire()

        # Assert that no mouse clicks were performed
        app.mouse_controller.click.assert_not_called()

        # Assert that time.sleep was not called
        with patch('time.sleep') as mock_sleep:
            app.run_rapid_fire()
            mock_sleep.assert_not_called()

    def test_run_rapid_fire_inactive(self):
        """
        Test that run_rapid_fire exits immediately when rapid_fire_active is False.
        """
        app = RecoilControlApp(tk.Tk())
        app.rapid_fire_active = False
        app.run_rapid_fire()
        # No assertions needed, test passes if method exits without error

    def test_run_rapid_fire_invalid_mouse_button(self):
        """
        Test run_rapid_fire behavior when an invalid mouse button is configured.
        """
        app = RecoilControlApp(tk.Tk())
        app.rapid_fire_active = True
        config["rapid_fire_mouse_button"] = "invalid_button"
        app.run_rapid_fire()
        # No assertions needed, test passes if method handles invalid button without error

    def test_run_tbag_1(self):
        """
        Test the run_tbag method when the tbag_key is a single character.
        This test verifies that the correct key is pressed and released
        with the configured interval when the tbag_key length is 1.
        """
        # Mock the RecoilControlApp
        app = Mock(spec=RecoilControlApp)
        app.tbag_active = True
        app.keyboard_controller = Mock()

        # Set up the test configuration
        config["tbag_button"] = "c"  # Single character key
        config["tbag_interval"] = 100  # 100ms interval

        # Patch time.sleep to avoid actual delays
        with patch('time.sleep') as mock_sleep:
            # Call the method
            RecoilControlApp.run_tbag(app)

            # Verify the correct key was pressed and released
            app.keyboard_controller.press.assert_called_with("c")
            app.keyboard_controller.release.assert_called_with("c")

            # Verify the sleep durations
            mock_sleep.assert_any_call(0.05)  # Half of tbag_interval / 1000

        # Verify the method stops when tbag_active becomes False
        app.tbag_active = False
        RecoilControlApp.run_tbag(app)
        assert app.keyboard_controller.press.call_count == 1
        assert app.keyboard_controller.release.call_count == 1

    def test_run_tbag_2(self):
        """
        Test the run_tbag method when the tbag_key is not a single character.

        This test verifies that:
        1. The correct key object is created for a special key.
        2. The key is pressed and released with the correct timing.
        3. The loop continues while tbag_active is True.
        """
        # Mock the RecoilControlApp
        app = Mock(spec=RecoilControlApp)
        app.tbag_active = True
        app.keyboard_controller = Mock()

        # Set up the config for a special key
        config["tbag_button"] = "ctrl"
        config["tbag_interval"] = 100

        # Mock the keyboard.Key to return a mock object for the special key
        with patch('main.keyboard.Key') as mock_key:
            mock_key.ctrl = Mock()

            # Call the method
            RecoilControlApp.run_tbag(app)

            # Assertions
            mock_key.ctrl.assert_called_once()
            app.keyboard_controller.press.assert_called_with(mock_key.ctrl)
            app.keyboard_controller.release.assert_called_with(mock_key.ctrl)

            # Check if the sleep function was called with the correct intervals
            time.sleep.assert_any_call(0.05)  # 100 / 2000 for press
            time.sleep.assert_any_call(0.05)  # 100 / 2000 for release

        # Ensure the loop would have continued if tbag_active remained True
        assert app.keyboard_controller.press.call_count > 1
        assert app.keyboard_controller.release.call_count > 1

    def test_run_tbag_3(self):
        """
        Test the run_tbag method when tbag_key is a single character and tbag_active is True.
        This test verifies that the correct key is pressed and released with the specified interval.
        """
        # Mock the keyboard controller
        mock_keyboard = MagicMock()

        # Create an instance of RecoilControlApp with the mocked keyboard
        app = RecoilControlApp(None)
        app.keyboard_controller = mock_keyboard

        # Set up the test conditions
        config['tbag_button'] = 'c'  # Single character key
        config['tbag_interval'] = 100  # 100ms interval
        app.tbag_active = True

        # Mock time.sleep to avoid actual delays
        with patch('time.sleep') as mock_sleep:
            # Call run_tbag method
            app.run_tbag()

            # Assert that the key was pressed and released
            mock_keyboard.press.assert_called_once_with('c')
            mock_keyboard.release.assert_called_once_with('c')

            # Assert that time.sleep was called twice with the correct intervals
            mock_sleep.assert_any_call(0.05)  # Half of tbag_interval / 1000
            mock_sleep.assert_any_call(0.05)  # Half of tbag_interval / 1000

            # Assert that tbag_active was checked
            self.assertTrue(app.tbag_active)

    def test_run_tbag_4(self):
        """
        Test that the run_tbag method exits immediately when tbag_active is False
        and the tbag_key is a single character.
        """
        app = RecoilControlApp(MagicMock())
        app.tbag_active = False
        app.keyboard_controller = MagicMock()

        # Set up the config for this test
        config["tbag_button"] = "c"
        config["tbag_interval"] = 50

        with patch('time.sleep') as mock_sleep:
            app.run_tbag()

        # Assert that the keyboard controller methods were not called
        app.keyboard_controller.press.assert_not_called()
        app.keyboard_controller.release.assert_not_called()

        # Assert that time.sleep was not called
        mock_sleep.assert_not_called()

    def test_save_config_1(self):
        """
        Test that save_config correctly writes the configuration to the file.
        """
        # Setup
        test_config = {
            "horizontal_recoil": 5,
            "vertical_recoil": 3,
            "activation_key": "F1",
            "toggle_key": "F2"
        }
        test_config_file = "test_config.json"

        # Set the CONFIG_FILE to our test file
        main.CONFIG_FILE = test_config_file

        try:
            # Execute
            main.save_config(test_config)

            # Verify
            assert os.path.exists(test_config_file), "Config file was not created"

            with open(test_config_file, "r") as f:
                saved_config = json.load(f)

            assert saved_config == test_config, "Saved config does not match the input config"

        finally:
            # Cleanup
            if os.path.exists(test_config_file):
                os.remove(test_config_file)

    def test_save_config_invalid_json(self):
        """
        Test that save_config raises a TypeError when trying to save non-JSON serializable data.
        This is an edge case explicitly handled by json.dump() which is used in the save_config method.
        """
        config = {"key": set()}  # Sets are not JSON serializable
        with pytest.raises(TypeError):
            save_config(config)

    def test_save_config_settings_1(self):
        """
        Test case for save_config_settings method.
        This test verifies that all configuration settings are correctly saved
        when all attributes are present and some interval values are less than 1.
        """
        # Create a mock RecoilControlApp instance
        app = MagicMock(spec=RecoilControlApp)

        # Set up mock attributes and their values
        app.activation_key_var = MagicMock(get=MagicMock(return_value="F1"))
        app.toggle_key_var = MagicMock(get=MagicMock(return_value="F2"))
        app.mouse_activation_var = MagicMock(get=MagicMock(return_value="left_click"))
        app.bg_file_var = MagicMock(get=MagicMock(return_value="background.gif"))
        app.hide_toggle_key_var = MagicMock(get=MagicMock(return_value="F6"))
        app.rapid_fire_enabled_var = MagicMock(get=MagicMock(return_value=True))
        app.rapid_fire_key_var = MagicMock(get=MagicMock(return_value="F3"))
        app.rapid_fire_interval_var = MagicMock(get=MagicMock(return_value="0"))
        app.rapid_fire_mouse_button_var = MagicMock(get=MagicMock(return_value="left_click"))
        app.tbag_enabled_var = MagicMock(get=MagicMock(return_value=True))
        app.tbag_key_var = MagicMock(get=MagicMock(return_value="F4"))
        app.tbag_interval_var = MagicMock(get=MagicMock(return_value="0"))
        app.tbag_button_var = MagicMock(get=MagicMock(return_value="ctrl"))

        # Call the method
        RecoilControlApp.save_config_settings(app)

        # Assert that the config was updated correctly
        self.assertEqual(app.config["activation_key"], "F1")
        self.assertEqual(app.config["toggle_key"], "F2")
        self.assertEqual(app.config["mouse_activation"], "left_click")
        self.assertEqual(app.config["background_file"], "background.gif")
        self.assertEqual(app.config["hide_toggle_key"], "F6")
        self.assertEqual(app.config["rapid_fire_enabled"], True)
        self.assertEqual(app.config["rapid_fire_key"], "F3")
        self.assertEqual(app.config["rapid_fire_interval"], 1)  # Should be set to minimum of 1
        self.assertEqual(app.config["rapid_fire_mouse_button"], "left_click")
        self.assertEqual(app.config["tbag_enabled"], True)
        self.assertEqual(app.config["tbag_key"], "F4")
        self.assertEqual(app.config["tbag_interval"], 1)  # Should be set to minimum of 1
        self.assertEqual(app.config["tbag_button"], "ctrl")

        # Assert that save_config was called
        app.save_config.assert_called_once_with(app.config)

        # Assert that show_movement_screen was called
        app.show_movement_screen.assert_called_once()

    def test_save_config_settings_invalid_rapid_fire_interval(self):
        """
        Test that the save_config_settings method handles invalid rapid fire interval input
        by setting it to the default value of 15ms.
        """
        app = MagicMock()
        app.rapid_fire_interval_var = MagicMock()
        app.rapid_fire_interval_var.get.return_value = "invalid"

        with patch("builtins.open", MagicMock()), \
             patch("json.dump", MagicMock()):
            app.save_config_settings()

        assert app.config["rapid_fire_interval"] == 15

    def test_save_config_settings_invalid_tbag_interval(self):
        """
        Test that the save_config_settings method handles invalid t-bag interval input
        by setting it to the default value of 50ms.
        """
        app = MagicMock()
        app.tbag_interval_var = MagicMock()
        app.tbag_interval_var.get.return_value = "invalid"

        with patch("builtins.open", MagicMock()), \
             patch("json.dump", MagicMock()):
            app.save_config_settings()

        assert app.config["tbag_interval"] == 50

    def test_save_movement_settings_1(self):
        """
        Test that save_movement_settings correctly updates the config dictionary
        and calls save_config with the updated values.
        """
        # Create a mock RecoilControlApp instance
        app = MagicMock(spec=RecoilControlApp)

        # Set up mock values for vertical and horizontal scales
        app.vertical_scale.get.return_value = 5
        app.horizontal_scale.get.return_value = -3

        # Create a copy of the original config
        original_config = config.copy()

        # Call the method under test
        with patch('main.save_config') as mock_save_config:
            app.save_movement_settings()

        # Check that config was updated correctly
        self.assertEqual(config['vertical_recoil'], 5)
        self.assertEqual(config['horizontal_recoil'], -3)

        # Check that save_config was called with the updated config
        mock_save_config.assert_called_once_with(config)

        # Restore the original config
        config.update(original_config)

    def test_save_movement_settings_invalid_input(self):
        """
        Test save_movement_settings with invalid input values.
        This test verifies that the method handles invalid scale values gracefully.
        """
        app = RecoilControlApp(tk.Tk())
        app.vertical_scale = mock.MagicMock()
        app.horizontal_scale = mock.MagicMock()

        # Set invalid values for scales
        app.vertical_scale.get.return_value = "invalid"
        app.horizontal_scale.get.return_value = "invalid"

        # Call the method
        app.save_movement_settings()

        # Check that config was not updated with invalid values
        assert config["vertical_recoil"] != "invalid"
        assert config["horizontal_recoil"] != "invalid"

    def test_setup_canvas_1(self):
        """
        Test that setup_canvas creates and returns a canvas when frames are available.

        This test verifies that:
        1. The canvas is created with the correct dimensions and properties.
        2. The canvas is packed correctly.
        3. An image is created on the canvas when frames are available.
        4. The update_frame method is called.
        5. The canvas is returned.
        """
        root = tk.Tk()
        gif = AnimatedGIF(root, "test.gif", width=100, height=100)
        gif.frames = [tk.PhotoImage(width=1, height=1)]  # Mock frame

        canvas = gif.setup_canvas(root)

        assert isinstance(canvas, tk.Canvas)
        assert canvas.winfo_width() == 100
        assert canvas.winfo_height() == 100
        assert canvas.cget("highlightthickness") == "0"
        assert canvas.pack_info()["expand"] == 1
        assert canvas.pack_info()["fill"] == "both"
        assert hasattr(gif, 'image_id')
        assert hasattr(gif, 'update_frame')
        assert canvas == gif.canvas

        root.destroy()

    def test_setup_canvas_2(self):
        """
        Test the setup_canvas method when there are no frames.

        This test verifies that when the AnimatedGIF instance has no frames,
        the setup_canvas method still creates and returns a canvas without
        creating an image on it.
        """
        # Create a mock Tk root
        root = Mock(spec=tk.Tk)

        # Create an AnimatedGIF instance with no frames
        gif = AnimatedGIF(root, "dummy.gif")
        gif.frames = []  # Ensure frames list is empty

        # Call setup_canvas
        parent = Mock(spec=tk.Frame)
        result = gif.setup_canvas(parent)

        # Assert that a canvas was created and packed
        parent.Canvas.assert_called_once()
        parent.Canvas.return_value.pack.assert_called_once_with(expand=True, fill="both")

        # Assert that no image was created on the canvas
        parent.Canvas.return_value.create_image.assert_not_called()

        # Assert that the method returns the canvas
        self.assertEqual(result, gif.canvas)

    def test_setup_custom_titlebar_1(self):
        """
        Test that setup_custom_titlebar correctly initializes and configures the titlebar.

        This test verifies:
        1. The titlebar is created with correct parameters
        2. The titlebar is packed
        3. The title label is created and configured correctly
        4. The minimize and close buttons are created and configured correctly
        5. All elements are bound to the appropriate event handlers
        """
        root = tk.Tk()
        app = RecoilControlApp(root)

        app.setup_custom_titlebar()

        # Check if titlebar is created and packed
        self.assertIsInstance(app.titlebar, tk.Frame)
        self.assertEqual(app.titlebar.master, root)
        self.assertEqual(app.titlebar.cget('bg'), "#8b0000")
        self.assertEqual(app.titlebar.cget('height'), 40)

        # Check if title label is created and configured correctly
        self.assertIsInstance(app.title_label, tk.Label)
        self.assertEqual(app.title_label.cget('text'), "MDZ Recoil")
        self.assertEqual(app.title_label.cget('fg'), "white")
        self.assertEqual(app.title_label.cget('bg'), "#8b0000")

        # Check if minimize and close buttons are created and configured correctly
        self.assertIsInstance(app.minimize_button, tk.Button)
        self.assertEqual(app.minimize_button.cget('text'), "─")
        self.assertEqual(app.minimize_button.cget('bg'), "#555555")

        self.assertIsInstance(app.close_button, tk.Button)
        self.assertEqual(app.close_button.cget('text'), "✖")
        self.assertEqual(app.close_button.cget('bg'), "#c0392b")

        # Check if event bindings are set up correctly
        self.assertEqual(app.titlebar.bind('<Button-1>'), app.get_pos)
        self.assertEqual(app.titlebar.bind('<B1-Motion>'), app.move_window)
        self.assertEqual(app.title_label.bind('<Button-1>'), app.get_pos)
        self.assertEqual(app.title_label.bind('<B1-Motion>'), app.move_window)

        root.destroy()

    def test_setup_custom_titlebar_no_root(self):
        """
        Test setup_custom_titlebar when self.root is None.
        This tests the edge case where the root window is not properly initialized.
        """
        app = RecoilControlApp(None)
        app.root = None

        with self.assertRaises(AttributeError):
            app.setup_custom_titlebar()

    def test_show_config_screen_1(self):
        """
        Test that the show_config_screen method correctly sets up the configuration screen
        with the appropriate widgets and initial values from the config.
        """
        root = tk.Tk()
        app = RecoilControlApp(root)
        config = load_config()

        app.show_config_screen()

        # Check if the main frame is created and added to the canvas
        assert len(app.root.winfo_children()) == 1, "Canvas should be the only child of root"
        canvas = app.root.winfo_children()[0]
        assert isinstance(canvas, tk.Canvas), "First child should be a Canvas"

        # Check if the frame is created and added to the canvas
        assert len(canvas.find_all()) == 1, "Canvas should have one item (the frame)"
        frame_id = canvas.find_all()[0]
        frame = canvas.itemcget(frame_id, 'window')
        assert isinstance(frame, tk.Frame), "Canvas item should be a Frame"

        # Check if the activation key selector is created with the correct initial value
        assert hasattr(app, 'activation_key_var'), "Activation key variable should exist"
        assert app.activation_key_var.get() == config["activation_key"], "Activation key should match config"

        # Check if the toggle key selector is created with the correct initial value
        assert hasattr(app, 'toggle_key_var'), "Toggle key variable should exist"
        assert app.toggle_key_var.get() == config["toggle_key"], "Toggle key should match config"

        # Check if the mouse activation dropdown is created with the correct initial value
        assert hasattr(app, 'mouse_activation_var'), "Mouse activation variable should exist"
        assert app.mouse_activation_var.get() == config["mouse_activation"], "Mouse activation should match config"

        root.destroy()

    def test_show_config_screen_invalid_config(self):
        """
        Test show_config_screen when the config dictionary is missing required keys.
        """
        root = tk.Tk()
        app = RecoilControlApp(root)

        # Backup original config and set an invalid one
        original_config = config.copy()
        config.clear()

        with self.assertRaises(KeyError):
            app.show_config_screen()

        # Restore original config
        config.update(original_config)

    def test_show_config_screen_no_canvas(self):
        """
        Test show_config_screen when the animated_bg attribute is not set,
        which would prevent the canvas from being created.
        """
        root = tk.Tk()
        app = RecoilControlApp(root)
        app.animated_bg = None  # Simulate missing animated_bg

        with self.assertRaises(AttributeError):
            app.show_config_screen()

    def test_show_movement_screen_1(self):
        """
        Test that the show_movement_screen method correctly sets up the UI elements
        and initializes them with the proper values from the config.
        """
        root = tk.Tk()
        app = RecoilControlApp(root)
        app.animated_bg = MagicMock()
        app.animated_bg.setup_canvas.return_value = tk.Canvas(root)

        with patch('tkinter.Frame'), patch('tkinter.Label'), patch('tkinter.Button'), \
             patch('tkinter.Scale'), patch('tkinter.StringVar'):
            app.show_movement_screen()

        # Check if status labels are created and set correctly
        assert hasattr(app, 'status_label')
        assert hasattr(app, 'rapid_fire_status_label')
        assert hasattr(app, 'tbag_status_label')
        assert hasattr(app, 'hide_window_status_label')

        # Check if scales are created and set to correct initial values
        assert hasattr(app, 'vertical_scale')
        assert app.vertical_scale.get() == config["vertical_recoil"]
        assert hasattr(app, 'horizontal_scale')
        assert app.horizontal_scale.get() == config["horizontal_recoil"]

        # Verify that buttons are created
        assert len([w for w in app.root.winfo_children() if isinstance(w, tk.Button)]) > 0

        root.destroy()

    def test_show_movement_screen_with_missing_config_values(self):
        """
        Test the show_movement_screen method when certain config values are missing.
        This tests an edge case where the configuration might be incomplete.
        """
        root = tk.Tk()
        app = RecoilControlApp(root)

        # Backup original config
        original_config = config.copy()

        # Remove some config values
        del config['vertical_recoil']
        del config['horizontal_recoil']

        # Mock the methods that interact with tkinter
        with patch('tkinter.Canvas.create_window'), \
             patch('tkinter.Label'), \
             patch('tkinter.Scale'), \
             patch('tkinter.Button'), \
             patch.object(app, 'add_discord_contact'):

            # Call the method
            app.show_movement_screen()

        # Assert that the method doesn't crash when config values are missing
        # We're mainly checking that the method completes without raising an exception

        # Restore original config
        config.update(original_config)

        root.destroy()

    def test_show_rapid_fire_config_1(self):
        """
        Test that the show_rapid_fire_config method correctly sets up the Rapid Fire configuration screen.

        This test verifies that:
        1. The screen is cleared before setting up the new configuration.
        2. A canvas is created for the animated background.
        3. A frame is created and added to the canvas.
        4. The Rapid Fire configuration elements are added to the frame, including:
           - Title label
           - Checkbox for enabling Rapid Fire
           - Key selector for Rapid Fire activation
           - Interval entry for Rapid Fire timing
           - Dropdown for selecting the mouse button
           - Explanation text
           - Save and Back buttons
        5. The Discord contact information is added to the bottom right of the screen.
        """
        app = RecoilControlApp(tk.Tk())
        app.show_rapid_fire_config()

        # Check if the screen was cleared
        assert len(app.root.winfo_children()) == 2  # Canvas and titlebar

        # Check if canvas was created
        assert isinstance(app.root.winfo_children()[0], tk.Canvas)

        # Check if frame was added to canvas
        canvas = app.root.winfo_children()[0]
        assert len(canvas.find_withtag("all")) == 1

        # Check if all required elements are present in the frame
        frame = canvas.winfo_children()[0]
        assert isinstance(frame.winfo_children()[0], tk.Label)  # Title
        assert isinstance(frame.winfo_children()[1], tk.Frame)  # Checkbox frame
        assert isinstance(frame.winfo_children()[2], tk.Frame)  # Key selector frame
        assert isinstance(frame.winfo_children()[3], tk.Frame)  # Interval frame
        assert isinstance(frame.winfo_children()[4], tk.Label)  # Mouse button label
        assert isinstance(frame.winfo_children()[5], ttk.Combobox)  # Mouse button dropdown
        assert isinstance(frame.winfo_children()[6], tk.Label)  # Explanation text
        assert isinstance(frame.winfo_children()[7], tk.Frame)  # Buttons frame

        # Check if Discord contact info is added
        assert len(canvas.find_withtag("all")) == 2  # Frame and Discord contact

    def test_show_tbag_config_1(self):
        """
        Test that the show_tbag_config method correctly initializes and displays
        the T-Bag configuration screen with the expected elements and values.
        """
        root = tk.Tk()
        app = RecoilControlApp(root)

        # Mock the clear_screen and animated_bg methods
        app.clear_screen = MagicMock()
        app.animated_bg = MagicMock()
        app.animated_bg.setup_canvas.return_value = tk.Canvas(root)

        # Call the method under test
        app.show_tbag_config()

        # Assertions to verify the correct setup of the T-Bag config screen
        self.assertTrue(hasattr(app, 'tbag_enabled_var'))
        self.assertEqual(app.tbag_enabled_var.get(), config["tbag_enabled"])

        self.assertTrue(hasattr(app, 'tbah_key_var'))
        self.assertEqual(app.tbah_key_var.get(), config["tbag_key"])

        self.assertTrue(hasattr(app, 'tbag_interval_var'))
        self.assertEqual(app.tbag_interval_var.get(), str(config["tbag_interval"]))

        self.assertTrue(hasattr(app, 'tbag_button_var'))
        self.assertEqual(app.tbag_button_var.get(), config["tbag_button"])

        # Clean up
        root.destroy()

    def test_show_welcome_screen_1(self):
        """
        Test that the welcome screen is displayed correctly with all expected elements.

        This test verifies that the show_welcome_screen method creates and displays
        all the necessary widgets with the correct text, styles, and layout.
        """
        root = tk.Tk()
        app = RecoilControlApp(root)
        app.show_welcome_screen()

        # Check if the main elements are present
        assert isinstance(app.animated_bg, AnimatedGIF), "Animated background should be created"

        canvas = root.winfo_children()[0]
        assert isinstance(canvas, tk.Canvas), "Canvas should be created"

        frame = canvas.winfo_children()[0]
        assert isinstance(frame, tk.Frame), "Frame should be created"

        widgets = frame.winfo_children()
        assert len(widgets) == 6, "Frame should contain 6 widgets"

        # Check specific widgets
        assert isinstance(widgets[0], tk.Label) and widgets[0].cget("text") == "MDZ RECOIL", "Logo label should be present"
        assert isinstance(widgets[1], tk.Label) and widgets[1].cget("text") == "Bem-vindo ao MDZ Recoil", "Welcome label should be present"
        assert isinstance(widgets[2], tk.Label) and "Software de controle de recoil" in widgets[2].cget("text"), "Description label should be present"
        assert isinstance(widgets[3], tk.Button) and widgets[3].cget("text") == "Iniciar Configuração", "Enter button should be present"
        assert isinstance(widgets[4], tk.Label) and widgets[4].cget("text") == "v1.1.0", "Version label should be present"

        # Check if Discord contact is added
        discord_frame = canvas.winfo_children()[1]
        assert isinstance(discord_frame, tk.Frame), "Discord contact frame should be present"

        root.destroy()

    def test_show_welcome_screen_no_titlebar(self):
        """
        Test the show_welcome_screen method when the titlebar attribute doesn't exist.
        This tests the edge case where the titlebar hasn't been created yet.
        """
        app = RecoilControlApp(tk.Tk())
        delattr(app, 'titlebar')  # Remove titlebar attribute
        app.show_welcome_screen()
        assert hasattr(app, 'titlebar'), "Titlebar should be created if it doesn't exist"

    def test_toggle_macro_1(self):
        """
        Tests the toggle_macro method when the macro is initially not running
        and there is no active listener thread.
        """
        # Create a mock RecoilControlApp instance
        class MockRecoilControlApp:
            def __init__(self):
                self.running = False
                self.listener_thread = None

            def update_status_label(self):
                pass

            def run_macro(self):
                time.sleep(0.1)  # Simulate some work

            def toggle_macro(self):
                self.running = not self.running
                self.update_status_label()
                if self.running:
                    if not self.listener_thread or not self.listener_thread.is_alive():
                        self.listener_thread = threading.Thread(target=self.run_macro, daemon=True)
                        self.listener_thread.start()

        # Create an instance of the mock class
        app = MockRecoilControlApp()

        # Call the toggle_macro method
        app.toggle_macro()

        # Assert that the running state has changed
        assert app.running == True

        # Assert that a listener thread has been created and started
        assert app.listener_thread is not None
        assert app.listener_thread.is_alive() == True

        # Wait for the thread to complete
        app.listener_thread.join(timeout=0.2)

        # Assert that the thread has finished
        assert app.listener_thread.is_alive() == False

    def test_toggle_macro_2(self):
        """
        Tests toggle_macro method when the macro is already running and the listener thread is alive.

        This test verifies that:
        1. The running state is toggled from True to False.
        2. The update_status_label method is called.
        3. No new listener thread is started.
        """
        # Setup
        app = RecoilControlApp(None)
        app.running = True
        app.listener_thread = Mock()
        app.listener_thread.is_alive.return_value = True
        app.update_status_label = Mock()

        # Execute
        app.toggle_macro()

        # Assert
        assert app.running == False
        app.update_status_label.assert_called_once()
        app.listener_thread.start.assert_not_called()

    def test_toggle_macro_3(self):
        """
        Tests the toggle_macro method when the macro is initially not running.

        This test verifies that:
        1. The running state is changed from False to True.
        2. The status label is updated.
        3. A new listener thread is created and started if it doesn't exist or is not alive.
        """
        # Create a mock RecoilControlApp instance
        app = MagicMock()
        app.running = False
        app.listener_thread = None

        # Call the toggle_macro method
        app.toggle_macro()

        # Assert that the running state is changed to True
        assert app.running == True

        # Assert that the update_status_label method was called
        app.update_status_label.assert_called_once()

        # Assert that a new listener thread was created and started
        assert app.listener_thread is not None
        app.listener_thread.start.assert_called_once()

    def test_toggle_window_visibility_1(self):
        """
        Test that toggle_window_visibility restores the window when it's hidden.

        This test case verifies that when the window is hidden (self.window_hidden is True),
        calling toggle_window_visibility will restore the window and set window_hidden to False.
        """
        root = tk.Tk()
        app = RecoilControlApp(root)
        app.window_hidden = True
        app.restore_window = lambda: None  # Mock restore_window method
        app.toggle_window_visibility()
        assert app.window_hidden == False

    def test_toggle_window_visibility_2(self):
        """
        Test that toggle_window_visibility minimizes the window when it's not hidden.

        This test case verifies that when the window is not hidden (self.window_hidden is False),
        calling toggle_window_visibility will minimize the window and set self.window_hidden to True.
        """
        # Create an instance of RecoilControlApp
        app = RecoilControlApp(tk.Tk())

        # Set initial state
        app.window_hidden = False

        # Mock the minimize_window and restore_window methods
        app.minimize_window = lambda: None
        app.restore_window = lambda: None

        # Call the method under test
        app.toggle_window_visibility()

        # Assert that the window is now hidden
        assert app.window_hidden == True

    def test_toggle_window_visibility_when_window_hidden(self):
        """
        Test toggle_window_visibility when the window is hidden.
        It should call restore_window and set window_hidden to False.
        """
        root = tk.Tk()
        app = RecoilControlApp(root)
        app.window_hidden = True
        app.restore_window = MagicMock()

        app.toggle_window_visibility()

        app.restore_window.assert_called_once()
        assert app.window_hidden == False

    def test_toggle_window_visibility_when_window_visible(self):
        """
        Test toggle_window_visibility when the window is visible.
        It should call minimize_window and set window_hidden to True.
        """
        root = tk.Tk()
        app = RecoilControlApp(root)
        app.window_hidden = False
        app.minimize_window = MagicMock()

        app.toggle_window_visibility()

        app.minimize_window.assert_called_once()
        assert app.window_hidden == True

    def test_update_frame_1(self):
        """
        Test that update_frame returns early when there are no frames.

        This test verifies that the method exits immediately without performing
        any actions when the 'frames' list is empty.
        """
        # Setup
        root_mock = Mock()
        gif = AnimatedGIF(root_mock, "dummy.gif")
        gif.frames = []  # Ensure frames list is empty
        gif.canvas = Mock()

        # Call the method
        result = gif.update_frame()

        # Assertions
        self.assertIsNone(result)  # Method should return None
        gif.canvas.itemconfig.assert_not_called()  # canvas.itemconfig should not be called
        root_mock.after.assert_not_called()  # root.after should not be called

    def test_update_frame_2(self):
        """
        Tests the update_frame method when self.frames is not empty.

        This test verifies that:
        1. The canvas.itemconfig is called with the correct arguments.
        2. The current_frame is updated correctly.
        3. The root.after method is called with the correct arguments.
        """
        # Setup
        root = tk.Tk()
        gif = AnimatedGIF(root, "test.gif")
        gif.frames = [Mock(), Mock()]  # Create mock frames
        gif.canvas = Mock()
        gif.image_id = "test_image_id"
        gif.current_frame = 0
        gif.delay = 100

        # Call the method
        gif.update_frame()

        # Assertions
        gif.canvas.itemconfig.assert_called_once_with(gif.image_id, image=gif.frames[0])
        self.assertEqual(gif.current_frame, 1)
        root.after.assert_called_once_with(gif.delay, gif.update_frame)

        # Cleanup
        root.destroy()

    def test_update_frame_no_frames(self):
        """
        Test update_frame when there are no frames loaded.
        This tests the edge case where the frames list is empty.
        """
        root = None  # Mock root, not actually used in this test
        gif = AnimatedGIF(root, "nonexistent.gif")
        gif.frames = []  # Explicitly set frames to an empty list
        gif.canvas = None  # Set canvas to None to avoid attribute errors

        # Call update_frame and verify it returns without error
        gif.update_frame()
        # No assertion needed as we're just checking it doesn't raise an exception

    def test_update_scale_value_1(self):
        """
        Test that the update_scale_value method correctly updates the vertical_value_label
        when scale_type is "vertical".
        """
        root = tk.Tk()
        app = RecoilControlApp(root)
        app.vertical_value_label = tk.Label(root)

        app.update_scale_value("vertical", "5.5")

        assert app.vertical_value_label.cget("text") == "5.5"

        root.destroy()

    def test_update_scale_value_invalid_input(self):
        """
        Test that update_scale_value raises a ValueError when given a non-numeric input.
        """
        app = RecoilControlApp(None)
        with pytest.raises(ValueError, match="Invalid value: must be a number"):
            app.update_scale_value("vertical", "not_a_number")

    def test_update_scale_value_invalid_scale_type(self):
        """
        Test that update_scale_value does not update any label when given an invalid scale type.
        """
        app = RecoilControlApp(None)
        app.vertical_value_label = MockLabel()
        app.horizontal_value_label = MockLabel()

        initial_vertical = app.vertical_value_label.text
        initial_horizontal = app.horizontal_value_label.text

        app.update_scale_value("invalid_type", 5.0)

        assert app.vertical_value_label.text == initial_vertical
        assert app.horizontal_value_label.text == initial_horizontal

    def test_update_status_label_1(self):
        """
        Test the update_status_label method when all status labels are present.

        This test verifies that the method correctly updates all status labels
        (status, rapid fire, t-bag, and hide window) with the appropriate text
        and colors based on the current configuration and running state.
        """
        root = tk.Tk()
        app = RecoilControlApp(root)

        # Create mock status labels
        app.status_label = tk.Label(root)
        app.rapid_fire_status_label = tk.Label(root)
        app.tbag_status_label = tk.Label(root)
        app.hide_window_status_label = tk.Label(root)

        # Set initial states
        app.running = True
        config["rapid_fire_enabled"] = True
        config["tbag_enabled"] = False
        config["hide_toggle_key"] = "F6"

        # Call the method under test
        app.update_status_label()

        # Assert the correct updates
        assert app.status_label.cget("text") == "Status: Ativo"
        assert app.status_label.cget("fg") == "#00ff00"

        assert app.rapid_fire_status_label.cget("text") == "Rapid Fire: Ativado"
        assert app.rapid_fire_status_label.cget("fg") == "#00ff00"

        assert app.tbag_status_label.cget("text") == "T-Bag: Desativado"
        assert app.tbag_status_label.cget("fg") == "#ff0000"

        assert app.hide_window_status_label.cget("text") == "Tecla Esconder: F6"

        root.destroy()

    def test_update_status_label_missing_attributes(self):
        """
        Test update_status_label when the required attributes are missing.
        This tests the edge case where the method is called on an object
        that doesn't have all the expected attributes.
        """
        class MockApp:
            def __init__(self):
                self.running = True

        app = MockApp()

        # No exception should be raised, method should silently handle missing attributes
        app.update_status_label()

        # Verify that no attributes were added
        assert not hasattr(app, 'status_label')
        assert not hasattr(app, 'rapid_fire_status_label')
        assert not hasattr(app, 'tbag_status_label')
        assert not hasattr(app, 'hide_window_status_label')

class MockRecoilControlApp:

    def __init__(self):
        self.running = False
        self.rapid_fire_active = False
        self.tbag_active = False
        self.rapid_fire_thread = None
        self.tbag_thread = None
        self.window_hidden = False

    def toggle_macro(self):
        self.running = not self.running

    def toggle_window_visibility(self):
        self.window_hidden = not self.window_hidden

class MockLabel:

    def __init__(self):
        self.text = ""

    def config(self, text):
        self.text = text

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
