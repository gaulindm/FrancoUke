def vertical_arrow(x, y, direction=1):
    if direction == 1:
        pts = f"{x},{y-2} {x-6},{y+8} {x+6},{y+8}"
    else:
        pts = f"{x},{y+12} {x-6},{y+2} {x+6},{y+2}"
    return f'<polygon points="{pts}" fill="black" />'


def horizontal_arrow(x, y, direction=1):
    if direction == 1:
        pts = f"{x+24},{y} {x+14},{y-6} {x+14},{y+6}"
    else:
        pts = f"{x-24},{y} {x-14},{y-6} {x-14},{y+6}"
    return f'<polygon points="{pts}" fill="black" />'

def circular_arc(cx, cy, r, start_deg, end_deg, direction=1):
    import math

    s = math.radians(start_deg)
    e = math.radians(end_deg)

    x1 = cx + r * math.cos(s)
    y1 = cy + r * math.sin(s)
    x2 = cx + r * math.cos(e)
    y2 = cy + r * math.sin(e)

    # Always force large arc for 270° sweeps
    large_arc = 1

    # sweep flag: 1=CW, 0=CCW
    sweep = 1 if direction == 1 else 0

    return f'''
        <path d="M {x1} {y1}
                 A {r} {r} 0 {large_arc} {sweep} {x2} {y2}"
              stroke="black" stroke-width="3" fill="none" />
    '''


def svg_icon(move, box_width=64, box_height=64, radius=5):

    move = move.strip()
    axis = move[0]
    modifier = move[1:]
    is_prime = modifier == "'"
    is_double = modifier == "2"

    label_height = 22
    total_height = label_height + box_height

    Lx = box_width * 0.1875
    Mx = box_width * 0.50
    Rx = box_width * 0.8125

    Uy = label_height + box_height * 0.1875
    My = label_height + box_height * 0.50
    Dy = label_height + box_height * 0.8125

    arrows = []

    # ----------------------------------------------------------
    # R / L MOVES
    # ----------------------------------------------------------
    if axis in ("R", "L"):

        slice_x = Rx if axis == "R" else Lx
        direction = 1 if (axis == "R" and not is_prime) or (axis == "L" and is_prime) else -1

        top_line_y = label_height + 10
        bottom_line_y = label_height + box_height - 20

        if is_double:
            arrows.append(vertical_arrow(slice_x, top_line_y - 2, 1))
            arrows.append(vertical_arrow(slice_x, top_line_y + 6, 1))
        else:
            if direction == 1:
                arrows.append(vertical_arrow(slice_x, top_line_y - 2, 1))
            else:
                arrows.append(vertical_arrow(slice_x, bottom_line_y, -1))

# ----------------------------------------------------------
    # U / D MOVES
    # ----------------------------------------------------------
    if axis in ("U", "D"):

        slice_y = Uy if axis == "U" else Dy

        if axis == "U":
            direction = -1 if not is_prime else 1
            double_direction = -1
        else:
            direction = 1 if not is_prime else -1
            double_direction = 1

        arrow_x = box_width / 2

        if is_double:
            arrows.append(horizontal_arrow(arrow_x, slice_y, double_direction))
            arrows.append(horizontal_arrow(arrow_x + 8, slice_y, double_direction))
        else:
            arrows.append(horizontal_arrow(arrow_x, slice_y, direction))
    # ----------------------------------------------------------
    # F / F' / F2 MOVES
        # ----------------------------------------------------------
    if axis == "F":

        cx = Mx
        cy = My
        r = box_width * 0.28

        # rotation direction
        direction = 1 if not is_prime else -1

        # Always start at 90°
        start = 90
        end = 0 if direction == 1 else 180

        if is_double:
            # Always draw CW 90→0 arc for double moves
            arrows.append(circular_arc(cx, cy, r, 90, 0, 1))

            # Two vertical upward arrows, same style as R2/L2 arrows
            # Middle slice, slightly offset for display
            arrow_x = cx+17
            arrow_y = cy-2
            arrows.append(vertical_arrow(arrow_x, arrow_y-6, direction=-1))
            arrows.append(vertical_arrow(arrow_x, arrow_y, direction=-1))
        else:
            # Normal single arc: CW (F) or CCW (F')
            arrows.append(circular_arc(cx, cy, r, start, end, direction))

            # Arrowhead at arc endpoint (same arrow shape as R')
            if direction == 1:
                # F ends at right side (0°)
                arrow_x = cx+17
                arrow_y = cy-2
            else:
                # F' ends at left side (180°)
                arrow_x = cx-17
                arrow_y = cy-2

            # Use downward arrowhead like R' (direction = -1)
            arrows.append(vertical_arrow(arrow_x, arrow_y, direction=-1))


    # ----------------------------------------------------------
    # Slice lines
    # ----------------------------------------------------------

    vertical_lines = ""
    horizontal_lines = ""

    if axis in ("R", "L"):
        vertical_lines = f"""
            <line x1="{Lx}" y1="{label_height+10.5}" x2="{Lx}" y2="{label_height+box_height-10.5}" stroke="black" stroke-width="3" />
            <line x1="{Mx}" y1="{label_height+10.5}" x2="{Mx}" y2="{label_height+box_height-10.5}" stroke="black" stroke-width="3" />
            <line x1="{Rx}" y1="{label_height+10.5}" x2="{Rx}" y2="{label_height+box_height-10.5}" stroke="black" stroke-width="3" />
        """

    if axis in ("U", "D"):
        horizontal_lines = f"""
            <line x1="10.5" y1="{Uy}" x2="{box_width-10.5}" y2="{Uy}" stroke="black" stroke-width="3" />
            <line x1="10.5" y1="{My}" x2="{box_width-10.5}" y2="{My}" stroke="black" stroke-width="3" />
            <line x1="10.5" y1="{Dy}" x2="{box_width-10.5}" y2="{Dy}" stroke="black" stroke-width="3" />
        """

    # ----------------------------------------------------------
    arrows_svg = "\n".join(arrows)

    return f"""
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 {box_width} {total_height}"
     preserveAspectRatio="xMidYMid meet">

    <text x="{box_width/2}" y="{label_height/2}"
          font-size="14" text-anchor="middle" dominant-baseline="middle">
        {move}
    </text>

    <rect x="1" y="{label_height}" width="{box_width-2}" height="{box_height-2}"
          rx="{radius}" ry="{radius}"
          fill="white" stroke="black" stroke-width="2"/>

    <!-- Grid -->
    <line x1="{box_width/3}" y1="{label_height+1}" x2="{box_width/3}" y2="{label_height+box_height-1}" stroke="lightgray" stroke-width=".1" />
    <line x1="{2*box_width/3}" y1="{label_height+1}" x2="{2*box_width/3}" y2="{label_height+box_height-1}" stroke="lightgray" stroke-width=".1" />
    <line x1="2" y1="{label_height+box_height/3}" x2="{box_width-2}" y2="{label_height+box_height/3}" stroke="lightgray" stroke-width=".1" />
    <line x1="2" y1="{label_height+2*box_height/3}" x2="{box_width-2}" y2="{label_height+2*box_height/3}" stroke="lightgray" stroke-width=".1" />

    {vertical_lines}
    {horizontal_lines}

    {arrows_svg}
</svg>
"""
