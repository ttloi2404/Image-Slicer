import ast
from backend.entity_detection import EntityDetector
from interface.progress_bar import run_task_with_progress_bar
from utils.image_processing import set_background_to_transparent
from utils.settings import SLICE_TYPES


@run_task_with_progress_bar
def start_detecting(processor):
    processor.variables.slice_type.set(SLICE_TYPES[2])
    detector = EntityDetector(set_background_to_transparent(current_image=processor.original_image, background_color=ast.literal_eval(processor.variables.background_color.get())))
    detector.set_alpha_to_zero(processor.variables.alpha_threshold.get())
    detector.multiprocess_image((processor.variables.min_width.get(), processor.variables.min_height.get()), processor.variables.number_of_cores.get())
    processor.all_entities = detector.merge_boxes
    processor.draw_boxes()
