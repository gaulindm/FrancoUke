from reportlab.platypus import Flowable
from reportlab.lib import colors

from reportlab.platypus import Flowable
from reportlab.lib import colors

GREY = "#CCCCCC"

class CubeFlowable(Flowable):
    """
    A simple 3x3 isometric cube for reference.
    - Front face: squares
    - Right face: diamonds (parallelograms) skewed upward
    - Top face: diamonds (parallelograms) skewed to the right
    """
    def __init__(self, size=40):
        Flowable.__init__(self)
        self.size = size
        self.width = size * 3 + size  # add space for skew
        self.height = size * 3 + size

    def draw(self):
        c = self.canv
        s = self.size          # sticker size
        skew = s / 2           # skew factor for diamonds

        # --------------------
        # FRONT FACE (squares)
        # --------------------
        for row in range(3):
            for col in range(3):
                x0 = col * s
                y0 = row * s
                c.setFillColor(colors.white)
                c.rect(x0, y0, s, s, fill=1, stroke=1)

        # --------------------
        # RIGHT FACE (parallelograms)
        # --------------------
        for col in range(3):  # left to right
            for row in range(3):
                # x0, y0 is bottom-left of parallelogram
                x0 = 3 * s + col * skew
                y0 = row * s + col * s * 0.5  # shift up per column

                points = [
                    (x0, y0),                     # bottom-left
                    (x0 + skew, y0 + skew),       # bottom-right
                    (x0 + skew, y0 + s + skew),   # top-right
                    (x0, y0 + s)                  # top-left
                ]
                c.setFillColor(GREY)
                path = c.beginPath()
                path.moveTo(*points[0])
                for p in points[1:]:
                    path.lineTo(*p)
                path.close()
                c.drawPath(path, fill=1, stroke=1)

        # --------------------
        # TOP FACE (parallelograms / diamonds)
        # --------------------
        for row in range(3):      # front to back
            for col in range(3):  # left to right
                x0 = col * s + row * skew
                y0 = 3 * s + row * skew  # bottom-left corner of top sticker

                points = [
                    (x0, y0),                       # bottom-left
                    (x0 + s, y0),            # bottom-right
                    (x0 + s + skew, y0 + s - skew), # top-right
                    (x0 + skew, y0 + s - skew)             # top-left
                ]
                c.setFillColor(colors.yellow)
                path = c.beginPath()
                path.moveTo(*points[0])
                for p in points[1:]:
                    path.lineTo(*p)
                path.close()
                c.drawPath(path, fill=1, stroke=1)

    # Helper to draw polygon
    def _draw_poly(self, points):
        c = self.canv
        path = c.beginPath()
        path.moveTo(*points[0])
        for p in points[1:]:
            path.lineTo(*p)
        path.close()
        c.drawPath(path, stroke=1, fill=1)
