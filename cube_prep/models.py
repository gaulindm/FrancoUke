from django.db import models


class Cube(models.Model):
    """
    Represents a single cube face (3x3) used in a mosaic.
    """
    name = models.CharField(max_length=50, blank=True)

    # 3x3 list, row-major, e.g. [["R","R","R"], ["R","B","B"], ...]
    colors = models.JSONField(help_text="3x3 face colors")

    def __str__(self):
        return self.name or f"Cube {self.id}"


class Mosaic(models.Model):
    """
    Represents a mosaic made up of positioned cube faces.
    """
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def cube_rows(self):
        return max((mc.row for mc in self.mosaiccubes.all()), default=-1) + 1

    @property
    def cube_cols(self):
        return max((mc.col for mc in self.mosaiccubes.all()), default=-1) + 1

    def cubes_grid(self):
        """
        Returns a 2D grid [row][col] of Cube or None.
        """
        rows = self.cube_rows
        cols = self.cube_cols

        grid = [[None for _ in range(cols)] for _ in range(rows)]
        for mc in self.mosaiccubes.all():
            grid[mc.row][mc.col] = mc.cube
        return grid


class MosaicCube(models.Model):
    """
    Positions a Cube at a specific row/col inside a Mosaic.
    """
    mosaic = models.ForeignKey(
        Mosaic,
        on_delete=models.CASCADE,
        related_name="mosaiccubes"
    )
    row = models.PositiveSmallIntegerField()  # 0-indexed
    col = models.PositiveSmallIntegerField()  # 0-indexed
    cube = models.ForeignKey(Cube, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("mosaic", "row", "col")

    def __str__(self):
        return f"Cube ({self.row},{self.col}) in {self.mosaic.name}"
