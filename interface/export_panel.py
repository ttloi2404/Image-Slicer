import customtkinter as ctk
from backend.export_function import start_exporting


class ExportFrame(ctk.CTkFrame):
    def __init__(self, parent, processor):
        super().__init__(parent, fg_color="transparent")
        self.pack(expand=True, fill="both")
        self.file_name_editor = FileNameEditor(parent=self, processor=processor)
        self.export_button = ExportButton(parent=self, processor=processor)


class FileNameEditor(ctk.CTkFrame):
    def __init__(self, parent, processor):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="x", pady=4)

        label_texts = ["Prefix", "Start Index", "Postfix", "Separator", "Format"]
        entry_vars = [processor.variables.prefix, processor.variables.start_index, processor.variables.postfix, processor.variables.separator, processor.variables.format]

        self.rowconfigure(tuple(range(len(label_texts))), weight=1, uniform="a")
        self.columnconfigure((0, 1), weight=1, uniform="a")

        self.entry_widgets = {}
        for i, label_text in enumerate(label_texts):
            ctk.CTkLabel(self, text=label_text).grid(row=i, column=0, sticky="w", pady=1)
            entry = ctk.CTkEntry(self, textvariable=entry_vars[i])
            entry.grid(row=i, column=1, sticky="e", pady=1)
            self.entry_widgets[i] = entry
            entry_vars[i].trace_add("write", lambda *args: self.update_text(processor))

    def update_text(self, processor, *args):
        prefix, start_index, postfix, separator, file_format = (value.get() for value in [processor.variables.prefix, processor.variables.start_index, processor.variables.postfix, processor.variables.separator, processor.variables.format])
        for index, entity_name in enumerate(processor.viewer_controller.current_viewer.all_entity_names, start=start_index):
            name_parts = [prefix + separator + str(index) if prefix else str(index), separator + postfix if postfix else ""]
            if file_format:
                name_parts.append("." + file_format)
            entity_name.set("".join(filter(None, name_parts)))


class ExportButton(ctk.CTkButton):
    def __init__(self, parent, processor):
        super().__init__(parent, text="Export", command=lambda: start_exporting(processor))
        self.pack(side="bottom")
