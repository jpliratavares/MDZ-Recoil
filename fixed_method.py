def run_rapid_fire(self):
        from pynput import mouse
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