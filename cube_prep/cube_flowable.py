from reportlab.platypus import Flowable
from reportlab.lib import colors

from reportlab.platypus import Flowable
from reportlab.lib import colors

GREY = "#CCCCCC"

COLOR_MAP = {
    "W": colors.white,
    "R": colors.red,
    "B": colors.blue,
    "G": colors.green,
    "Y": colors.yellow,
    "O": colors.orange,
    None: colors.HexColor(GREY)  # default
}

class CubeFlowable(Flowable):
    def __init__(self, size=40, front_color=colors.white, top_color=colors.red, right_color="#CCCCCC"):
        Flowable.__init__(self)
        self.size = size
        self.width = size * 3 + size
        self.height = size * 3 + size

        # Sanitize input colors
        def sanitize(cvalue):
            # letter-based colors ("R", "G", "W"…)
            if cvalue in COLOR_MAP:
                return COLOR_MAP[cvalue]

            # hex color or already valid
            try:
                return colors.toColor(cvalue)
            except:
                return colors.HexColor(GREY)

        self.front_color = sanitize(front_color)
        self.top_color = sanitize(top_color)
        self.right_color = sanitize(right_color)


    def draw(self):
        c = self.canv
        s = self.size
        skew = s / 2

        # --------------------
        # FRONT FACE
        # --------------------
        for row in range(3):
            for col in range(3):
                x0 = col * s
                y0 = row * s
                c.setFillColor(self.front_color)
                c.rect(x0, y0, s, s, fill=1, stroke=1)

        # --------------------
        # RIGHT FACE
        # --------------------
        for col in range(3):
            for row in range(3):
                x0 = 3 * s + col * skew
                y0 = row * s + col * s * 0.5
                points = [
                    (x0, y0),
                    (x0 + skew, y0 + skew),
                    (x0 + skew, y0 + s + skew),
                    (x0, y0 + s)
                ]
                c.setFillColor(self.right_color)
                path = c.beginPath()
                path.moveTo(*points[0])
                for p in points[1:]:
                    path.lineTo(*p)
                path.close()
                c.drawPath(path, fill=1, stroke=1)

        # --------------------
        # TOP FACE
        # --------------------
        for row in range(3):
            for col in range(3):
                x0 = col * s + row * skew
                y0 = 3 * s + row * skew
                points = [
                    (x0, y0),
                    (x0 + s, y0),
                    (x0 + s + skew, y0 + s - skew),
                    (x0 + skew, y0 + s - skew)
                ]
                c.setFillColor(self.top_color)
                path = c.beginPath()
                path.moveTo(*points[0])
                for p in points[1:]:
                    path.lineTo(*p)
                path.close()
                c.drawPath(path, fill=1, stroke=1)

    def _draw_poly(self, points):
        c = self.canv
        path = c.beginPath()
        path.moveTo(*points[0])
        for p in points[1:]:
            path.lineTo(*p)
        path.close()
        c.drawPath(path, stroke=1, fill=1)
