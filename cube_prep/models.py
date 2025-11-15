from django.db import models

class Cube(models.Model):
    """
    Represents a single 3x3 cube with colors on its front face.
    """
    name = models.CharField(max_length=50, blank=True)
    moves = models.JSONField(blank=True, null=True)  # store moves to recreate face

    colors = models.JSONField()  # 3x3 list, e.g. [["R","R","R"], ["R","B","B"], ...]

    def __str__(self):
        return self.name or f"Cube {self.id}"


class Mosaic(models.Model):
    """
    Represents a mosaic made up of up to 6x6 cubes.
    """
    
    name = models.CharField(max_length=100)
    cubes = models.ManyToManyField(Cube, related_name="mosaics", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def cubes_grid(self):
        """
        Returns the cubes arranged as a 2D list [row][col] for easy rendering.
        """
        grid = [[None for _ in range(6)] for _ in range(6)]
        for mc in self.mosaiccubes.all():
            grid[mc.row][mc.col] = mc.cube
        return grid

    def cube_rows(self):
        """Return the number of rows with cubes."""
        return max((mc.row for mc in self.mosaiccubes.all()), default=-1) + 1

    def cube_cols(self):
        """Return the number of columns with cubes."""
        return max((mc.col for mc in self.mosaiccubes.all()), default=-1) + 1



class MosaicCube(models.Model):
    mosaic = models.ForeignKey(Mosaic, on_delete=models.CASCADE, related_name="mosaiccubes")
    row = models.PositiveSmallIntegerField()  # 0-indexed
    col = models.PositiveSmallIntegerField()  # 0-indexed
    cube = models.ForeignKey(Cube, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("mosaic", "row", "col")

    def __str__(self):
        return f"Cube ({self.row},{self.col}) in {self.mosaic.name}"


