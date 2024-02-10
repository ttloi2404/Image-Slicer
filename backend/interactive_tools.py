from PIL import ImageDraw
from utils.convert_coordinates import convert_coordinates
from utils.settings import MERGE_OUTLINE_COLOR, DELETE_OUTLINE_COLOR, ADD_OUTLINE_COLOR, SLICE_TYPES, BOX_COLOR
from backend.entity_detection import EntityDetector
from utils.image_processing import set_background_to_transparent
import ast # Used to parse background color string into a tuple


def start_operating(processor, operation_type):
    """Initiates an entity operation (add, delete, or merge) and sets up event bindings."""
    processor.variables.slice_type.set(SLICE_TYPES[2])
    current_viewer = processor.viewer_controller.current_viewer
    merge_status, delete_status, add_status = processor.variables.merge_status, processor.variables.delete_status, processor.variables.add_status

    # Determine the relevant status variable and its "other" counterparts based on the operation type
    if operation_type == "delete":
        status_variable, other_status_variable = delete_status, (merge_status, add_status)
    elif operation_type == "merge":
        status_variable, other_status_variable = merge_status, (delete_status, add_status)
    else:
        status_variable, other_status_variable = add_status, (delete_status, merge_status)

    if status_variable.get() == f"{operation_type.capitalize()}: Off":
        # If not active, turn off other operations and activate the current one
        other_status_variable[0].set(f"{other_status_variable[0].get().split(':')[0].capitalize()}: Off")
        other_status_variable[1].set(f"{other_status_variable[1].get().split(':')[0].capitalize()}: Off")
        status_variable.set(f"{operation_type.capitalize()}: On")

        # Set focus to the viewer and bind event handlers for user interaction
        current_viewer.focus_set()
        current_viewer.bind("<Button-1>", lambda event: on_click_start(processor, event))
        current_viewer.bind("<B1-Motion>", lambda event: on_dragging(processor, event, operation_type))
        current_viewer.bind("<ButtonRelease-1>", lambda event: on_release_button(processor, event, operation_type))
        current_viewer.bind("<Return>", lambda event: finalize_operation(processor, operation_type))
    else:
        status_variable.set(f"{operation_type.capitalize()}: Off")
        current_viewer.unbind("<Button-1>")
        current_viewer.unbind("<B1-Motion>")
        current_viewer.unbind("<ButtonRelease-1>")
        current_viewer.unbind("<Return>")


def on_click_start(processor, event):
    """Records the starting coordinates of a mouse drag for selecting an area."""
    processor.variables.start_x = processor.viewer_controller.current_viewer.canvasx(event.x)
    processor.variables.start_y = processor.viewer_controller.current_viewer.canvasy(event.y)


def on_dragging(processor, event, operation_type):
    """Draws a temporary rectangle on the viewer to indicate the selection area while dragging."""
    processor.viewer_controller.current_viewer.delete("rectangle")
    if operation_type == "delete":
        outline_color = DELETE_OUTLINE_COLOR
    elif operation_type == "merge":
        outline_color = MERGE_OUTLINE_COLOR
    else:
        outline_color = ADD_OUTLINE_COLOR
    processor.viewer_controller.current_viewer.create_rectangle(processor.variables.start_x, processor.variables.start_y, event.x, event.y, outline=outline_color, tags="rectangle")


def on_release_button(processor, event, operation_type):
    """Handle the release of the mouse button after a drag operation."""
    processor.viewer_controller.current_viewer.delete("rectangle")
    start_x, start_y = convert_coordinates(processor, (processor.variables.start_x, processor.variables.start_y))
    end_x, end_y = convert_coordinates(processor, (event.x, event.y))

    # Get the final coordinates of the selected area, ensuring they stay within image bounds
    if start_x > end_x:
        start_x, end_x = end_x, start_x
    if start_y > end_y:
        start_y, end_y = end_y, start_y
    start_x = max(0, min(start_x, processor.original_image.width - 1))
    start_y = max(0, min(start_y, processor.original_image.height - 1))
    end_x = max(0, min(end_x, processor.original_image.width - 1))
    end_y = max(0, min(end_y, processor.original_image.height - 1))

    # Reset the starting coordinates for future drags
    processor.variables.start_x = None
    processor.variables.start_y = None

    # Process the selected area based on the operation type
    adjust_selection(processor, start_x, start_y, end_x, end_y, operation_type)


def finalize_operation(processor, operation_type):
    """Finalize the current operation (add, delete, or merge) and update the image display."""
    if processor.variables.processing_queue:
        if operation_type == "add":
            processor.all_entities.update(processor.variables.processing_queue)
        else:
            processor.all_entities = processor.all_entities - processor.variables.processing_queue
            if operation_type == "merge":
                merged_entity = processor.variables.processing_queue.pop()
                for entity in processor.variables.processing_queue:
                    merged_entity = merged_entity.merge(entity)
                processor.all_entities.add(merged_entity)

        # Re-draw bounding boxes and clear the processing queue
        processor.draw_boxes()
        processor.variables.processing_queue.clear()


def adjust_selection(processor, start_x, start_y, end_x, end_y, operation_type):
    """Adjust the selection based on the operation type and handle entity processing."""
    drawer = ImageDraw.Draw(processor.current_image)
    if operation_type == "add":
        detector = EntityDetector(set_background_to_transparent(current_image=processor.original_image, background_color=ast.literal_eval(processor.variables.background_color.get())))
        detector.set_alpha_to_zero(processor.variables.alpha_threshold.get())
        entities = expand_by_click(detector, start_x, start_y) if start_x == end_x and start_y == end_y else detector.single_process_image((start_x, start_y, end_x, end_y))
        
        # Process each detected entity
        for entity in sorted(entities, key=lambda entity: entity.area()):
            if entity not in processor.variables.processing_queue:
                if entity not in processor.all_entities:
                    processor.variables.processing_queue.add(entity)
                    drawer.rectangle((entity.start_x, entity.start_y, entity.end_x + 1, entity.end_y + 1), outline=ADD_OUTLINE_COLOR)
            else:
                processor.variables.processing_queue.remove(entity)
                drawer.rectangle((entity.start_x, entity.start_y, entity.end_x + 1, entity.end_y + 1), outline=ast.literal_eval(processor.variables.background_color.get())[:-1])

    else:
        for entity in sorted(processor.all_entities, key=lambda entity: entity.area()):
            if entity.end_x >= start_x and entity.start_x <= end_x and entity.end_y >= start_y and entity.start_y <= end_y:
                color = DELETE_OUTLINE_COLOR if operation_type == "delete" else MERGE_OUTLINE_COLOR
                if entity not in processor.variables.processing_queue:
                    processor.variables.processing_queue.add(entity)
                else:
                    processor.variables.processing_queue.remove(entity)
                    color = BOX_COLOR
                drawer.rectangle((entity.start_x, entity.start_y, entity.end_x + 1, entity.end_y + 1), outline=color)

    # Update the image display with the drawn selections
    processor.place_image()


def expand_by_click(detector, x, y):
    """This function performs entity detection around a clicked point and expands the selection if the pixel is non-transparent."""
    result = set()
    if detector.formatted_image.getpixel((x, y))[-1] > 0:
        bbox = detector.load_containing_bounding_box(result, (x, y))
        if bbox is not None:
            x = bbox.end_x
        else:
            bbox = detector.explore_bounded_box((x, y))
            result.add(bbox)
    return result
