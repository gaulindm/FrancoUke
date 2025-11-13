from django.db import models

class Mosaic(models.Model):
    """
    Represents the overall mosaic picture.
    """
    name = models.CharField(max_length=100)
    cube_rows = models.PositiveSmallIntegerField(default=6)  # 6 cubes high
    cube_cols = models.PositiveSmallIntegerField(default=6)  # 6 cubes wide
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class MosaicCube(models.Model):
    """
    Represents a single cube in the mosaic.
    Each cube has a position (cube_row, cube_col) in the mosaic.
    """
    mosaic = models.ForeignKey(Mosaic, on_delete=models.CASCADE, related_name="cubes")
    cube_row = models.PositiveSmallIntegerField()  # 0-indexed
    cube_col = models.PositiveSmallIntegerField()  # 0-indexed

    class Meta:
        unique_together = ("mosaic", "cube_row", "cube_col")

    def __str__(self):
        return f"Cube ({self.cube_row},{self.cube_col}) in {self.mosaic.name}"


class CubeSquare(models.Model):
    """
    Represents a single square on the front face of a cube.
    Each cube has 9 squares (3x3).
    """
    cube = models.ForeignKey(MosaicCube, on_delete=models.CASCADE, related_name="squares")
    square_index = models.PositiveSmallIntegerField()  # 0-8 for 3x3 cube
    color = models.CharField(max_length=20)  # e.g., "Red", "White"

    class Meta:
        unique_together = ("cube", "square_index")

    def __str__(self):
        return f"{self.color} square {self.square_index} in {self.cube}"
