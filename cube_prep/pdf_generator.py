# cube_prep/pdf_generator.py

from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors as rl_colors
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.platypus.flowables import Flowable
from reportlab.lib.enums import TA_CENTER

# ============================
# Helper to render a Cube face
# ============================

COLOR_MAP = {
    "R": rl_colors.red,
    "B": rl_colors.blue,
    "Y": rl_colors.yellow,
    "G": rl_colors.green,
    "O": rl_colors.orange,
    "W": rl_colors.white,
}

def draw_cube_face(cube, size=48):
    """
    Returns a Flowable (Drawing) that represents a 3x3 cube face
    Size: 48pt to ensure 5x5 grid fits on one page
    """
    drawing = Drawing(size, size)
    sticker_size = size / 3

    for i, row in enumerate(cube.colors):
        for j, color in enumerate(row):
            drawing.add(
                Rect(
                    j * sticker_size,
                    size - (i + 1) * sticker_size,
                    sticker_size,
                    sticker_size,
                    fillColor=COLOR_MAP.get(color, rl_colors.grey),
                    strokeColor=rl_colors.black,
                    strokeWidth=0.5,
                )
            )

    return drawing

# ============================
# Main PDF generator function
# ============================

def generate_teacher_pdf(mosaic, cols=5, rows=5):
    """
    Generates a PDF for a given Mosaic instance.
    Cubes are numbered sequentially based on their grid position.
    Each cube shows: Mosaic Name, Cube Number, Row/Col position
    
    Page calculations:
    - Letter: 612 x 792 points
    - Margins: 20pt each side
    - Usable: 572 x 752 points
    - Cell (5x5): 114.4 x 140.4 points (with -10 adjustment)
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20,
    )

    elements = []
    styles = getSampleStyleSheet()
    
    # Style for mosaic name (small, subtle)
    mosaic_name_style = ParagraphStyle(
        'MosaicName',
        parent=styles['Normal'],
        fontSize=7,         # Small
        alignment=TA_CENTER,
        spaceAfter=2,       # Minimal space after
        spaceBefore=1,
        leading=8,
        textColor=rl_colors.HexColor('#999999'),  # Light gray
        fontName='Helvetica-Oblique',  # Italic for distinction
    )
    
    # Style for cube number (larger, bold)
    cube_number_style = ParagraphStyle(
        'CubeNumber',
        parent=styles['Normal'],
        fontSize=10,        # Larger for visibility
        alignment=TA_CENTER,
        spaceAfter=3,       # Space after
        spaceBefore=0,
        leading=12,
        fontName='Helvetica-Bold',
    )
    
    # Style for position info
    position_style = ParagraphStyle(
        'Position',
        parent=styles['Normal'],
        fontSize=8,         # Readable size
        alignment=TA_CENTER,
        spaceAfter=3,
        spaceBefore=0,
        leading=10,
        textColor=rl_colors.HexColor('#666666'),
    )

    cubes_grid = mosaic.cubes_grid()
    cubes_list = []
    for r_idx, row in enumerate(cubes_grid):
        for c_idx, cube in enumerate(row):
            if cube:
                cubes_list.append((r_idx, c_idx, cube))

    cubes_per_page = cols * rows
    
    # Get total columns from mosaic to calculate cube numbers correctly
    total_cols = mosaic.cube_cols
    
    # Get mosaic name (truncate if too long)
    mosaic_name = mosaic.name
    if len(mosaic_name) > 20:
        mosaic_name = mosaic_name[:17] + "..."
    
    # Calculate exact dimensions
    usable_width = letter[0] - 40   # 612 - 40 = 572
    usable_height = letter[1] - 40  # 792 - 40 = 752
    cell_width = usable_width / cols   # 572 / 5 = 114.4
    cell_height = usable_height / rows - 10  # 752 / 5 - 10 = 140.4
    
    print(f"\n{'='*60}")
    print(f"PDF Generation - Layout Calculations")
    print(f"{'='*60}")
    print(f"Mosaic name: {mosaic.name}")
    print(f"Page size: {letter[0]} x {letter[1]} points")
    print(f"Usable area: {usable_width} x {usable_height} points")
    print(f"Grid: {cols} x {rows} ({cubes_per_page} cubes per page)")
    print(f"Cell size: {cell_width:.1f} x {cell_height:.1f} points")
    print(f"Total cubes: {len(cubes_list)}")
    print(f"Mosaic grid: {mosaic.cube_rows} x {total_cols}")
    print(f"Pages needed: {(len(cubes_list) + cubes_per_page - 1) // cubes_per_page}")
    print(f"{'='*60}\n")

    for page_start in range(0, len(cubes_list), cubes_per_page):
        page_cubes = cubes_list[page_start: page_start + cubes_per_page]
        page_num = (page_start // cubes_per_page) + 1
        print(f"Building page {page_num}: cubes {page_start + 1} to {page_start + len(page_cubes)}")
        
        table_data = []

        for r in range(rows):
            row_data = []
            for c in range(cols):
                index = r * cols + c
                if index < len(page_cubes):
                    real_row, real_col, cube = page_cubes[index]
                    
                    # Calculate cube number based on position in original mosaic grid
                    # Cube number = (row * total_columns) + column + 1
                    cube_number = (real_row * total_cols) + real_col + 1

                    # Cube drawing (48pt)
                    cube_drawing = draw_cube_face(cube, size=48)

                    # Inner table with mosaic name, cube number, and position
                    inner_table = Table(
                        [
                            [Paragraph(f"<i>{mosaic_name}</i>", mosaic_name_style)],
                            [Paragraph(f"<b>Cube {cube_number}</b>", cube_number_style)],
                            [Paragraph(f"Row {real_row + 1} : Col {real_col + 1}", position_style)],
                            [cube_drawing],
                        ],
                        colWidths=cell_width - 6,
                    )
                    inner_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('TOPPADDING', (0, 0), (-1, -1), 1),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                        ('LEFTPADDING', (0, 0), (-1, -1), 2),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                    ]))

                    row_data.append(inner_table)
                else:
                    row_data.append("")

            table_data.append(row_data)

        # Create main table with exact dimensions
        table = Table(
            table_data,
            colWidths=[cell_width] * cols,
            rowHeights=[cell_height] * rows,
        )
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, rl_colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ]))

        elements.append(table)
        if page_start + cubes_per_page < len(cubes_list):
            elements.append(PageBreak())

    print(f"Building PDF document...")
    doc.build(elements)
    buffer.seek(0)
    print(f"✅ PDF generated: {len(buffer.getvalue())} bytes\n")
    return buffer