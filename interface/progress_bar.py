import customtkinter as ctk
import threading
from utils.settings import PROGRESS_COLOR


class ProgressBarManager(ctk.CTkToplevel):
    def __init__(self, task, *args, **kwargs):
        super().__init__()
        self.title("Task in Progress")

        self.run_task(task, *args, **kwargs)
        self.display_progress_bar()

    def make_window_at_center(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int(((screen_width - width) / 2) * self._get_window_scaling())
        y = int(((screen_height - height) / 2) * self._get_window_scaling())
        self.geometry(f"{width}x{height}+{x}+{y}")

    def display_progress_bar(self):
        self.make_window_at_center(width=480, height=90)
        self.progress_bar = ctk.CTkProgressBar(self, mode="indeterminate", progress_color=PROGRESS_COLOR, width=240)
        self.progress_bar.pack(pady=10)
        message_label = ctk.CTkLabel(self, text="Please wait while processing. This may take a few minutes for large datasets....")
        message_label.pack(pady=5)
        self.progress_bar.set(0)
        self.progress_bar.start()
        self.after(100, self.lift)
        self.trace_progress()

    def run_task(self, task, *args, **kwargs):
        self.thread = threading.Thread(target=task, args=args, kwargs=kwargs)
        self.thread.daemon = True
        self.thread.start()

    def trace_progress(self):
        if self.thread.is_alive():
            self.after(100, self.trace_progress)
        else:
            self.progress_bar.stop()
            self.destroy()


def run_task_with_progress_bar(function):
    def wrapper(*args, **kwargs):
        ProgressBarManager(function, *args, **kwargs)

    return wrapper
