from PIL import Image, ImageDraw
from collections import deque
from concurrent.futures import ProcessPoolExecutor
import os, math, numpy
from backend.bounding_box import BoundingBox


class EntityDetector:
    """
    This class performs entity detection on an image using pixel connectivity and multi-processing.

    Attributes:
        original_image (Image): The original image object.
        formatted_image (Image): The preprocessed image used for detection (e.g., alpha transparency removed).
        bounding_boxes (set): A set of BoundingBox objects representing detected entities.
        merge_boxes (set): A set of merged BoundingBox objects after post-processing.
    """
    def __init__(self, image):
        self.original_image = image
        self.formatted_image = image

    def set_alpha_to_zero(self, threshold):
        """Removes pixels with alpha channel below a certain threshold, making them transparent."""
        data = numpy.array(self.original_image)
        alpha_channel = data[:, :, -1]
        data[alpha_channel < threshold, -1] = 0
        self.formatted_image = Image.fromarray(data, "RGBA")

    def load_containing_bounding_box(self, boxes, point):
        """Checks if a point is contained within any existing bounding box and returns it."""
        for bbox in boxes:
            if bbox.contains_point(point):
                return bbox
        return None

    def explore_bounded_box(self, start_point):
        """
        Uses breadth-first search to explore a connected region and create a BoundingBox.

        Args:
            start_point (tuple): The starting point for the exploration.

        Returns:
            BoundingBox: The bounding box encompassing the connected region.
        """
        queue = deque([start_point])
        result = BoundingBox()
        marked_points = set()
        while queue:
            current_point = queue.popleft()
            result.expand(current_point)
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    new_point = (current_point[0] + dx, current_point[1] + dy)
                    if 0 <= new_point[0] < self.formatted_image.width and 0 <= new_point[1] < self.formatted_image.height:
                        if new_point not in marked_points and self.formatted_image.getpixel(new_point)[-1] > 0:
                            marked_points.add(new_point)
                            queue.append(new_point)
        return result

    def single_process_image(self, execution_area):
        """
        Detects entities within a specific area of the image using single-core processing.

        Args:
            execution_area (tuple): A tuple representing the top-left and bottom-right coordinates of the area.

        Returns:
            set: A set of BoundingBox objects representing detected entities in the area.
        """
        result = set()
        start_x, start_y, end_x, end_y = execution_area
        for y in range(int(start_y), int(end_y)):
            for x in range(int(start_x), int(end_x)):
                if self.formatted_image.getpixel((x, y))[-1] > 0:
                    bbox = self.load_containing_bounding_box(result, (x, y))
                    if bbox is not None:
                        x = bbox.end_x
                    else:
                        bbox = self.explore_bounded_box((x, y))
                        result.add(bbox)
        return result

    def divide_image(self, part_number):
        """
        Divides the image into a grid of equal-sized parts.

        Args:
            part_number (int): The number of parts to divide the image into.

        Returns:
            list: A list of tuples representing the top-left and bottom-right coordinates of each part.
        """
        width, height = self.original_image.size
        parts = []

        part_width = int(width / math.sqrt(part_number))
        part_height = int(height / math.sqrt(part_number))

        for i in range(int(math.sqrt(part_number))):
            for j in range(int(math.sqrt(part_number))):
                left = i * part_width
                upper = j * part_height
                right = left + part_width
                lower = upper + part_height
                parts.append((left, upper, right, lower))

        return parts

    def distance_point_to_bounding_box(self, point, bounding_box):
        """Calculates the minimum distance between a point and any edge of a bounding box."""
        return min(
            math.dist(point, (bounding_box.start_x, bounding_box.start_y)),
            math.dist(point, (bounding_box.end_x, bounding_box.start_y)),
            math.dist(point, (bounding_box.start_x, bounding_box.end_y)),
            math.dist(point, (bounding_box.end_x, bounding_box.end_y)),
        )

    def distance_between_bounding_boxes(self, bounding_box1, bounding_box2):
        """Calculates the minimum distance between any corner of one bounding box and any corner of another."""
        return min(
            self.distance_point_to_bounding_box((bounding_box1.start_x, bounding_box1.start_y), bounding_box2),
            self.distance_point_to_bounding_box((bounding_box1.end_x, bounding_box1.start_y), bounding_box2),
            self.distance_point_to_bounding_box((bounding_box1.start_x, bounding_box1.end_y), bounding_box2),
            self.distance_point_to_bounding_box((bounding_box1.end_x, bounding_box1.end_y), bounding_box2),
        )

    def find_first_small_bounding_box(self, minimum_box_size):
        """Finds the first bounding box in the set that has a size smaller than the given minimum size."""
        for bbox in self.bounding_boxes:
            if bbox.size()[0] < minimum_box_size[0] or bbox.size()[1] < minimum_box_size[1]:
                return bbox
        return None

    def merge_bounding_boxes(self, bbox1, bbox2):
        """Merges two bounding boxes into one that encompasses both."""
        return bbox1.merge(bbox2)

    def find_next_bounding_box(self, pivot):
        """Finds the bounding box in the set that is closest to the given pivot bounding box."""
        return min(
            (bbox for bbox in self.bounding_boxes if bbox != pivot),
            key=lambda b: self.distance_between_bounding_boxes(pivot, b),
            default=None,
        )

    def fix_merged_bounding_boxes(self, minimum_box_size):
        """
        Merges small bounding boxes by iteratively finding the closest pair and merging them.

        Args:
            minimum_box_size (tuple): A tuple representing the minimum width and height for a bounding box.

        Returns:
            set: The updated set of bounding boxes after merging small ones.
        """
        pivot_small_bbox = self.find_first_small_bounding_box(minimum_box_size)
        while pivot_small_bbox:
            next_bbox = self.find_next_bounding_box(pivot_small_bbox)
            if next_bbox is None:
                break
            merged_bbox = self.merge_bounding_boxes(pivot_small_bbox, next_bbox)
            self.bounding_boxes.remove(next_bbox)
            self.bounding_boxes.remove(pivot_small_bbox)
            self.bounding_boxes.add(merged_bbox)
            pivot_small_bbox = self.find_first_small_bounding_box(minimum_box_size)
        return self.bounding_boxes

    def multiprocess_image(self, minimum_box_size, number_of_cores):
        """
        Divides the image into parts and uses multi-processing to detect entities in each part.

        Args:
            minimum_box_size (tuple): A tuple representing the minimum width and height for a bounding box.
            number_of_cores (int): The number of cores to use for parallel processing.

        Returns:
            None: Stores the results in the object attributes.
        """
        part_numbers = self.divide_image(part_number=number_of_cores)
        with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
            self.result = list(executor.map(self.single_process_image, part_numbers))
        self.bounding_boxes = set()
        for box in self.result:
            self.bounding_boxes.update(box)

        self.merge_boxes = self.fix_merged_bounding_boxes(minimum_box_size)