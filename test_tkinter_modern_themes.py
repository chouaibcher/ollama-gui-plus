import TKinterModernThemes as TKMT
import tkinter as tk

class TestApp(TKMT.ThemedTKinterFrame):
    def __init__(self):
        super().__init__("Test App", "park", "dark")
        self.Button("Test Button", lambda: print("Button clicked!"))
        self.run()

if __name__ == "__main__":
    TestApp()
