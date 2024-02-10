import customtkinter as ctk
from interface.image_controls import OpenButton, CloseButton, AddButton, MergeButton, DeleteButton
from utils.image_processing import disable_alpha_channel, is_solid_color


class ViewerController:
    def __init__(self, parent, processor):
        self.parent = parent
        self.processor = processor
        self.current_viewer = ctk.CTkFrame(parent)
        self.processor.variables.current_tab.trace_add("write", lambda *args: self.switch_viewer(self.processor.variables.current_tab.get()))

    def switch_viewer(self, mode):
        self.processor.variables.merge_status.set("Merge: Off")
        self.processor.variables.delete_status.set("Delete: Off")
        self.processor.variables.add_status.set("Add: Off")
        self.current_viewer.grid_forget()
        if mode == "Open":
            self.processor.variables.slice_type.set("Open")
            self.open_image_button = OpenButton(self.parent, self.processor.load_image)
        elif mode == "Slice":
            self.current_viewer = ImageViewer(self.parent, self.processor.resize_image)
            self.close_button = CloseButton(self.current_viewer, self.processor.close_current_image)
            self.add_button = AddButton(self.current_viewer, self.processor)
            self.merge_button = MergeButton(self.current_viewer, self.processor)
            self.delete_button = DeleteButton(self.current_viewer, self.processor)
        elif mode == "Export":
            self.current_viewer = SlicedViewer(self.parent, self.processor)


class ImageViewer(ctk.CTkCanvas):
    def __init__(self, parent, resize_image_function):
        super().__init__(parent, background="black", bd=0, highlightthickness=0, relief="ridge")
        self.bind("<Configure>", resize_image_function)
        self.grid(row=0, column=1, sticky="nsew")


class SlicedViewer(ctk.CTkScrollableFrame):
    def __init__(self, parent, processor):
        super().__init__(parent, width=processor.canvas_width, height=processor.canvas_height, fg_color="black")
        self.grid(row=0, column=1, sticky="nsew")
        self.initialize_parameters(processor)
        self.display_sliced_images(processor)

    def initialize_parameters(self, processor):
        self.image_width = 128
        self.image_height = 128
        self.spacing = 24
        self.max_images_per_row = int(processor.canvas_width / (self.image_width + 2 * self.spacing))
        self.all_entity_names = [ctk.StringVar(value=f"{index}.png") for index in range(len(processor.all_sliced_images))]

    def display_sliced_images(self, processor):
        count = 0
        while count < len(processor.all_sliced_images):
            frame = ctk.CTkFrame(self, fg_color="transparent")
            frame.pack(side="top", fill="x", pady=self.spacing / 6)

            number_current_image_on_line = 0
            while number_current_image_on_line < self.max_images_per_row and count < len(processor.all_sliced_images):
                if is_solid_color(processor.all_sliced_images[count]):
                    count += 1
                    continue
                image = disable_alpha_channel(processor.all_sliced_images[count])
                image.thumbnail((self.image_width, self.image_height))
                ctk_image = ctk.CTkImage(image, size=image.size)

                label_image = ctk.CTkLabel(
                    frame,
                    image=ctk_image,
                    textvariable=self.all_entity_names[count],
                    compound="top",
                    width=self.image_width,
                    height=self.image_height,
                    fg_color="transparent",
                    wraplength=self.image_width,
                )
                label_image.pack(side="left", padx=self.spacing / 4)
                count += 1
                number_current_image_on_line += 1
