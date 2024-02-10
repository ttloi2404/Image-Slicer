import customtkinter as ctk


class Variables:
    def __init__(self, processor):
        self.current_tab = ctk.StringVar(value="Slice")
        self.slice_type = ctk.StringVar(value="Open")

        self.rows = ctk.IntVar(value=0)
        self.columns = ctk.IntVar(value=0)

        self.width = ctk.IntVar(value=0)
        self.height = ctk.IntVar(value=0)

        self.min_width = ctk.IntVar(value=0)
        self.min_height = ctk.IntVar(value=0)
        self.alpha_threshold = ctk.IntVar(value=32)
        self.number_of_cores = ctk.IntVar(value=9)

        self.prefix = ctk.StringVar()
        self.start_index = ctk.IntVar(value=0)
        self.postfix = ctk.StringVar()
        self.separator = ctk.StringVar(value="_")
        self.format = ctk.StringVar(value="png")
        self.background_color = ctk.StringVar(value="(0, 0, 0, 0)")

        self.merge_status = ctk.StringVar(value="Merge: Off")
        self.delete_status = ctk.StringVar(value="Delete: Off")
        self.add_status = ctk.StringVar(value="Add: Off")
        self.processing_queue = set()
        self.start_x, self.end_x, self.start_y, self.end_y = None, None, None, None

        self.trace_grid(processor.draw_grid)
        self.trace_boxes(processor.draw_boxes)
        self.slice_type.trace_add("write", processor.refresh_image)

    def trace_grid(self, callback=None):
        vars_to_trace = [self.slice_type, self.rows, self.columns, self.width, self.height]
        for var in vars_to_trace:
            var.trace_add("write", callback)

    def trace_boxes(self, callback=None):
        vars_to_trace = [self.merge_status, self.delete_status, self.add_status]
        for var in vars_to_trace:
            var.trace_add("write", callback)
