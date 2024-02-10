import customtkinter as ctk
from interface.slicing_panel import SliceFrame
from interface.export_panel import ExportFrame


class MainMenu(ctk.CTkTabview):
    def __init__(self, parent, processor):
        super().__init__(parent, command=lambda: processor.variables.current_tab.set(self.get()))
        self.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.add("Slice")
        self.add("Export")
        self.slice_frame = SliceFrame(parent=self.tab("Slice"), processor=processor, main_menu=self)
        self.export_frame = ExportFrame(parent=self.tab("Export"), processor=processor)
