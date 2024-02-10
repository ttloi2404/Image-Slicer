class BoundingBox:
    """Represents a rectangular bounding box with four coordinates: start_x, start_y, end_x, end_y."""
    def __init__(self, start_x=None, start_y=None, end_x=None, end_y=None):
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y

    def expand(self, point):
        """Updates the bounding box to include the given point."""
        if self.start_x is None and self.start_y is None and self.end_x is None and self.end_y is None:
            self.start_x, self.start_y, self.end_x, self.end_y = point[0], point[1], point[0], point[1]
        else:
            self.start_x = min(self.start_x, point[0])
            self.start_y = min(self.start_y, point[1])
            self.end_x = max(self.end_x, point[0])
            self.end_y = max(self.end_y, point[1])

    def contains_point(self, point):
        """Checks if the given point is contained within the bounding box."""
        return self.start_x <= point[0] <= self.end_x and self.start_y <= point[1] <= self.end_y

    def merge(self, other_bbox):
        """Merges this bounding box with another bounding box, returning a new BoundingBox."""
        if other_bbox is not None:
            return BoundingBox(
                start_x=min(self.start_x, other_bbox.start_x),
                start_y=min(self.start_y, other_bbox.start_y),
                end_x=max(self.end_x, other_bbox.end_x),
                end_y=max(self.end_y, other_bbox.end_y),
            )
        return None

    def size(self):
        """Calculates the size (width and height) of the bounding box."""
        return (self.end_x - self.start_x + 1, self.end_y - self.start_y + 1)

    def area(self):
        width, height = self.size()
        return width * height

    def __eq__(self, other):
        if isinstance(other, BoundingBox):
            return self.start_x == other.start_x and self.start_y == other.start_y and self.end_x == other.end_x and self.end_y == other.end_y
        return False

    def __hash__(self):
        return hash((self.start_x, self.start_y, self.end_x, self.end_y))

    def __str__(self):
        return f"({self.start_x}, {self.start_y}, {self.end_x}, {self.end_y})"
