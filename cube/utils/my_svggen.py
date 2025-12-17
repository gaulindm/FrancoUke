# cube/utils/svggen.py

def svg_border(width=20, height=20, radius=3, stroke="#000", stroke_width=1.2):
    return f"""
    <rect x="1" y="1" width="{width-2}" height="{height-2}"
          rx="{radius}"
          fill="white"
          stroke="{stroke}"
          stroke-width="{stroke_width}" />
    """

def svg_arrow_right(x1=4, x2=16, y=10, stroke="#000", stroke_width=1.2):
    return f"""
    <defs>
      <marker id="arrowhead" markerWidth="6" markerHeight="6"
              refX="0" refY="3" orient="auto">
        <polygon points="0 0, 6 3, 0 6" fill="{stroke}" />
      </marker>
    </defs>
    <line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}"
          stroke="{stroke}" stroke-width="{stroke_width}"
          marker-end="url(#arrowhead)" />
    """
def svg_label(text, x=10, y=16):
    return f"""
    <text x="{x}" y="{y}" font-family="sans-serif"
          font-size="7" text-anchor="middle"
          stroke="none" fill="#000">{text}</text>
    """

def my_svg_icon(label, box_width=64, box_height=64, radius=5):
    label_height = 22
    total_height = box_height + label_height

    return f"""
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 {box_width} {total_height}"
     preserveAspectRatio="xMidYMid meet">

    <!-- Label text -->
    <text x="{box_width/2}"
          y="{label_height/2}"
          font-size="14"
          text-anchor="middle"
          dominant-baseline="middle">
        {label}
    </text>

    <!-- Rounded box -->
    <rect x="1" y="{label_height}"
          width="{box_width-2}" height="{box_height-2}"
          rx="{radius}" ry="{radius}"
          fill="white"
          stroke="black"
          stroke-width="1"/>
    <!-- Grid lines to simulate cube facelets -->

    <line x1="21.3" y1="23" 
          x2="21.3" y2="83" 
          style="stroke:lightgray;
          stroke-width:.1" />
    <line x1="42.6" y1="23" 
          x2="42.6" y2="83" 
          style="stroke:lightgray;
          stroke-width:.1" />
    <line x1="2" y1="43" 
          x2="62" y2="43" 
          style="stroke:lightgray;
          stroke-width:.1" />
    <line x1="2" y1="64" 
          x2="62" y2="64" 
          style="stroke:lightgray;
          stroke-width:.1" />

    <line x1="54" y1="43" 
          x2="54" y2="74" 
          style="stroke:lightgray;
          stroke-width:3" />


</svg>
"""
