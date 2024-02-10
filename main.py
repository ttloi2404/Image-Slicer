import customtkinter as ctk
from backend.processor import Processor
from multiprocessing import freeze_support


class Main(ctk.CTk):
    """Main application window for Image Slicer."""

    def __init__(self):
        """Initializes the main window and sets up the GUI elements."""
        super().__init__()
        self.initialize_interface()
        self.processor = Processor(self)  # Create a Processor object to handle backend tasks

    def initialize_interface(self):
        """Sets up the visual appearance and layout of the application window."""
        self.title("Image Slicer")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue") 
        self.iconbitmap("resources/icon.ico") 
        self.configure_layout() 
        self.make_window_at_center(width=960, height=540)  # Position the window at the center

    def make_window_at_center(self, width, height):
        """Centers the application window on the user's screen."""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int(((screen_width - width) / 2) * self._get_window_scaling())
        y = int(((screen_height - height) / 2) * self._get_window_scaling())
        self.geometry(f"{width}x{height}+{x}+{y}")

    def configure_layout(self):
        """Configures the grid layout of the main window."""
        self.rowconfigure(0, weight=1)  # Make the first row fill all available height
        self.columnconfigure(0, weight=2, uniform="a")  # Make the first column 2/10 width and stretch equally
        self.columnconfigure(1, weight=8, uniform="a")  # Make the second column 8/10 width and stretch equally

    def run_editor(self):
        """Starts the image slicing process and enters the main event loop."""
        self.processor.viewer_controller.switch_viewer("Open")  # Open the image selection interface
        self.mainloop()  # Start the main event loop and listen for user interactions

if __name__ == "__main__":
    freeze_support()  # Allow multi-processing for quicker image processing
    main = Main()
    main.after(0, lambda: main.wm_state("zoomed"))  # Maximize the window after initialization
    main.run_editor()
