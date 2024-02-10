import customtkinter as ctk
from tkinter import filedialog
from backend.interactive_tools import start_operating


class OpenButton(ctk.CTkFrame):
    def __init__(self, parent, open_image_function):
        super().__init__(parent)
        self.grid(column=0, columnspan=2, row=0, sticky="nsew")
        self.open_image_function = open_image_function
        ctk.CTkButton(self, text="Open Image", border_width=2, fg_color="transparent", command=self.open_dialog).pack(expand=True)

    def open_dialog(self):
        file_path = filedialog.askopenfile(filetypes=[("Image files", "*.jpg;*.png")]).name
        self.open_image_function(file_path)


class CloseButton(ctk.CTkButton):
    def __init__(self, parent, close_function):
        super().__init__(parent, width=0, height=0, command=close_function, text="Close", fg_color="black", bg_color="black")
        self.place(relx=1, rely=0, anchor="ne")


class AddButton(ctk.CTkButton):
    def __init__(self, parent, processor):
        super().__init__(parent, width=0, height=0, command=lambda: start_operating(processor, "add"), textvariable=processor.variables.add_status, fg_color="black", bg_color="black")
        self.place(relx=1, rely=1, anchor="se")


class MergeButton(ctk.CTkButton):
    def __init__(self, parent, processor):
        super().__init__(parent, width=0, height=0, command=lambda: start_operating(processor, "merge"), textvariable=processor.variables.merge_status, fg_color="black", bg_color="black")
        self.place(relx=0, rely=1, anchor="sw")


class DeleteButton(ctk.CTkButton):
    def __init__(self, parent, processor):
        super().__init__(parent, width=0, height=0, command=lambda: start_operating(processor, "delete"), textvariable=processor.variables.delete_status, fg_color="black", bg_color="black")
        self.place(relx=0, rely=0, anchor="nw")
