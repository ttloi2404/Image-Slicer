import customtkinter as ctk
from backend.detection_function import start_detecting
from backend.slicing_function import start_slicing
from backend.color_update_on_click import color_update_on_click
from utils.settings import RADIO_SELECT_COLOR, SLICE_TYPES


class SliceFrame(ctk.CTkFrame):
    def __init__(self, parent, processor, main_menu):
        super().__init__(parent, fg_color="transparent")
        self.pack(expand=True, fill="both")

        self.row_column = RowColumn(self, processor)
        self.fixed_size = FixedSize(self, processor)
        self.auto_detection = AutoDetection(self, processor)
        self.slice_button = SliceButton(self, processor, main_menu)

        self.all_entry_widgets = {
            SLICE_TYPES[0]: self.row_column.entry_widgets,
            SLICE_TYPES[1]: self.fixed_size.entry_widgets,
            SLICE_TYPES[2]: self.auto_detection.entry_widgets,
        }


class BaseFrame(ctk.CTkFrame):
    def __init__(self, parent, processor, label_texts, entry_vars):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="x", pady=4)
        self.rowconfigure(tuple(range(len(label_texts["labels"]))), weight=1, uniform="a")
        self.columnconfigure((0, 1), weight=1, uniform="a")

        ctk.CTkRadioButton(self, text=label_texts["radio"], variable=processor.variables.slice_type, value=label_texts["value"], fg_color=RADIO_SELECT_COLOR).grid(row=0, column=0, columnspan=2, sticky="w")

        self.entry_widgets = {}
        for i, label_text in enumerate(label_texts["labels"]):
            ctk.CTkLabel(self, text=label_text).grid(row=i + 1, column=0, sticky="w", pady=1)
            entry = ctk.CTkEntry(self, textvariable=entry_vars[i])
            entry.grid(row=i + 1, column=1, sticky="e", pady=1)
            self.entry_widgets[i] = entry


class RowColumn(BaseFrame):
    def __init__(self, parent, processor):
        label_texts = {"radio": SLICE_TYPES[0], "value": SLICE_TYPES[0], "labels": ["Rows", "Columns"]}
        entry_vars = [processor.variables.rows, processor.variables.columns]
        super().__init__(parent, processor, label_texts, entry_vars)


class FixedSize(BaseFrame):
    def __init__(self, parent, processor):
        label_texts = {"radio": SLICE_TYPES[1], "value": SLICE_TYPES[1], "labels": ["Width", "Height"]}
        entry_vars = [processor.variables.width, processor.variables.height]
        super().__init__(parent, processor, label_texts, entry_vars)


class AutoDetection(BaseFrame):
    def __init__(self, parent, processor):
        label_texts = {"radio": SLICE_TYPES[2], "value": SLICE_TYPES[2], "labels": ["Min Width", "Min Height", "Alpha Threshold", "Number of Cores", "Background Color"]}
        entry_vars = [processor.variables.min_width, processor.variables.min_height, processor.variables.alpha_threshold, processor.variables.number_of_cores, processor.variables.background_color]
        super().__init__(parent, processor, label_texts, entry_vars)
        self.rowconfigure(tuple(range(len(label_texts["labels"]) + 1)), weight=1, uniform="a")

        self.choose_color = ctk.CTkButton(self, text="Choose Color", command=lambda: self.start_choosing(processor))
        self.choose_color.grid(row=6, column=0, sticky="w", padx=2)

        self.detect = ctk.CTkButton(self, text="Detect", command=lambda: start_detecting(processor))
        self.detect.grid(row=6, column=1, sticky="e", padx=2)

    def start_choosing(self, processor):
        self.choose_color.configure(state="disabled")
        processor.viewer_controller.current_viewer.bind("<Button-1>", lambda event: color_update_on_click(self, processor, event))


class SliceButton(ctk.CTkButton):
    def __init__(self, parent, processor, main_menu):
        super().__init__(parent, text="Slice", command=lambda: start_slicing(processor, main_menu))
        self.pack(side="bottom")
