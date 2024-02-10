from PIL import Image
import numpy


def disable_alpha_channel(original_image):
    converted_image = Image.new("RGB", original_image.size, (0, 0, 0))
    converted_image.paste(original_image, mask=original_image.split()[-1])
    return converted_image


def is_solid_color(current_image):
    image_array = numpy.array(current_image)
    return (image_array == image_array[0, 0]).all()


def set_background_to_transparent(current_image, background_color):
    image_array = numpy.array(current_image)
    mask = numpy.all(image_array == background_color, axis=-1)
    image_array[mask] = (0, 0, 0, 0)
    return Image.fromarray(image_array)
