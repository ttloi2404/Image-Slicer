from utils.settings import SLICE_TYPES


def calculate_cell_dimensions(current_image, processor):
    cell_width, cell_height = 0, 0
    if processor.variables.slice_type.get() == SLICE_TYPES[0]:
        if processor.variables.columns.get() > 1:
            cell_width = int(current_image.width / processor.variables.columns.get())
        if processor.variables.rows.get() > 1:
            cell_height = int(current_image.height / processor.variables.rows.get())
    else:
        if processor.variables.width.get() > 1:
            cell_width = processor.variables.width.get()
        if processor.variables.height.get() > 1:
            cell_height = processor.variables.height.get()
    return cell_width, cell_height
