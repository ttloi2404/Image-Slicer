def convert_coordinates(processor, event):
    if event[0] is None or event[1] is None:
        return -1, -1
    offset_x = (processor.canvas_width - processor.image_width) / 2
    offset_y = (processor.canvas_height - processor.image_height) / 2
    scaled_factor_x = processor.original_image.width / processor.image_width
    scaled_factor_y = processor.original_image.height / processor.image_height
    return int((event[0] - offset_x) * scaled_factor_x), int((event[1] - offset_y) * scaled_factor_y)
