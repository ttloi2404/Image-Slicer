from utils.convert_coordinates import convert_coordinates


def color_update_on_click(parent, processor, event):
    x, y = convert_coordinates(processor, (event.x, event.y))
    if x < 0 or x >= processor.original_image.width or y < 0 or y >= processor.original_image.height:
        return None

    parent.choose_color.configure(state="normal")
    processor.viewer_controller.current_viewer.unbind("<Button-1>")
    pixel_color = processor.original_image.getpixel((x, y))
    processor.variables.background_color.set(str(pixel_color))
