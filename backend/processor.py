from interface.image_viewer import ViewerController
from backend.variables import Variables
from PIL import Image, ImageTk, ImageDraw
from utils.image_processing import disable_alpha_channel
from interface.main_menu import MainMenu
from utils.cell_dimension_calculation import calculate_cell_dimensions
from utils.settings import SLICE_TYPES, BOX_COLOR, GRID_COLOR


class Processor:
    """This class represents the main image processing logic, handling image loading, display, and entity management."""
    def __init__(self, parent):
        self.parent = parent
        self.all_entities = set()
        self.all_sliced_images = set()
        self.variables = Variables(self)
        self.viewer_controller = ViewerController(parent=parent, processor=self)

    def load_image(self, image_path):
        """Load an image from the specified path and perform initial processing."""
        self.image_path = image_path
        self.original_image = Image.open(image_path).convert("RGBA")
        self.non_alpha_image = disable_alpha_channel(Image.open(image_path).convert("RGBA"))
        self.current_image = self.non_alpha_image
        self.display_image()

    def display_image(self):
        """Calculate image aspect ratio, create main menu, and switch to slice viewer in the viewer controller."""
        self.image_ratio = self.current_image.width / self.current_image.height
        self.main_menu = MainMenu(parent=self.parent, processor=self)
        self.viewer_controller.switch_viewer("Slice")

    def resize_image(self, event):
        """Resize the image based on the available canvas dimensions while maintaining aspect ratio."""
        self.canvas_ratio = event.width / event.height
        self.canvas_width = event.width
        self.canvas_height = event.height

        if self.canvas_ratio > self.image_ratio:
            self.image_height = event.height
            self.image_width = self.image_height * self.image_ratio
        else:
            self.image_width = event.width
            self.image_height = self.image_width / self.image_ratio
        self.place_image()

    def place_image(self):
        """Clear the viewer, resize and convert the image to PhotoImage, and display it on the canvas."""
        self.viewer_controller.current_viewer.delete("all")
        resized_image = self.current_image.resize((int(self.image_width), int(self.image_height)))
        self.image_tk = ImageTk.PhotoImage(resized_image)
        self.viewer_controller.current_viewer.create_image(self.canvas_width / 2, self.canvas_height / 2, image=self.image_tk)

    def close_current_image(self):
        """Clear the viewer, reset entities and sliced images, and switch to the open image viewer."""
        self.viewer_controller.current_viewer.delete("all")
        self.all_entities.clear()
        self.all_sliced_images.clear()
        self.viewer_controller.switch_viewer("Open")

    def draw_boxes(self, *args):
        """Draws rectangles around all detected entities on the image."""
        self.variables.processing_queue.clear()
        self.current_image = self.non_alpha_image.copy()
        drawer = ImageDraw.Draw(self.current_image)
        for bounding_box in self.all_entities:
            drawer.rectangle((bounding_box.start_x, bounding_box.start_y, bounding_box.end_x + 1, bounding_box.end_y + 1), outline=BOX_COLOR)
        self.place_image()

    def draw_grid(self, *args):
        """Draws a grid overlay on the image, dividing it into cells based on slice type."""
        self.current_image = self.non_alpha_image.copy()
        if self.variables.slice_type.get() != SLICE_TYPES[2]:
            cell_width, cell_height = calculate_cell_dimensions(self.current_image, processor=self)
            drawer = ImageDraw.Draw(self.current_image)
            if cell_width > 0:
                for x in range(cell_width, int(self.current_image.width), cell_width):
                    drawer.line((x, 0, x, self.current_image.height), fill=GRID_COLOR)
            if cell_height > 0:
                for y in range(cell_height, int(self.current_image.height), cell_height):
                    drawer.line((0, y, self.current_image.width, y), fill=GRID_COLOR)
        self.place_image()

    def refresh_image(self, *args):
        """Reverts the displayed image to the original non-alpha version, removing any drawn elements."""
        self.current_image = self.non_alpha_image.copy()
