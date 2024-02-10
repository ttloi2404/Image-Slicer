from interface.progress_bar import run_task_with_progress_bar
from utils.cell_dimension_calculation import calculate_cell_dimensions
from utils.image_processing import set_background_to_transparent
import ast
from CTkMessagebox import CTkMessagebox
from utils.settings import SLICE_TYPES


def start_slicing(processor, main_menu):
    processor.all_sliced_images.clear()
    message = CTkMessagebox(master=processor.parent, title="Remove Background", message="Do you want to remove the background?", icon="question", option_1="Cancel", option_2="No", option_3="Yes", option_focus=3)
    response = message.get()
    if response == "Cancel":
        return
    processing_image = processor.original_image
    if response == "Yes":
        processing_image = set_background_to_transparent(current_image=processor.original_image, background_color=ast.literal_eval(processor.variables.background_color.get()))
    continue_slicing(processor, processing_image, main_menu)


@run_task_with_progress_bar
def continue_slicing(processor, processing_image, main_menu):
    if processor.variables.slice_type.get() not in (SLICE_TYPES[2], "Open"):
        cell_width, cell_height = calculate_cell_dimensions(processing_image, processor)
        cell_width = cell_width if cell_width != 0 else processing_image.width
        cell_height = cell_height if cell_height != 0 else processing_image.height
        processor.all_sliced_images = [processing_image.crop((x, y, x + cell_width, y + cell_height)) for y in range(0, int(processing_image.height), cell_height) for x in range(0, int(processing_image.width), cell_width)]
    else:
        if processor.all_entities:
            processor.all_sliced_images = [processing_image.crop((bounding_box.start_x, bounding_box.start_y, bounding_box.end_x + 1, bounding_box.end_y + 1)) for bounding_box in sorted(processor.all_entities, key=lambda box: (box.start_y, box.start_x))]
    main_menu.set("Export")
    if not processor.all_sliced_images:
        processor.all_sliced_images = [processing_image]
    processor.viewer_controller.switch_viewer("Export")
