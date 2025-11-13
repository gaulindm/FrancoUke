from django.shortcuts import render
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Flowable, Image, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from io import BytesIO
import random, os

from .cube_flowable import CubeFlowable

# --- Sample move icons folder ---
MOVE_ICONS_DIR = os.path.join("cube_prep", "static", "cube_prep", "moves")

# --- Sample scrambles ---
PATTERNS = {
    "Face Solved": ["R U R' U'"],
    "Checkerboard": ["M2 E2 S2"],
    "Simple Scramble": ["R U R' U'", "L' U2 L", "U R U' R'"]
}

# --- View: Home page ---
def generator_home(request):
    return render(request, "cube_prep/generator.html")


# --- View: Generate single card PDF ---
def generate_single_card(request):
    pattern = request.GET.get("pattern", "Face Solved")
    scramble_seq = random.choice(PATTERNS[pattern])

    # --- Create PDF buffer ---
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []

    styles = getSampleStyleSheet()
    story.append(Paragraph(f"Rubik's Cube Card – Pattern: {pattern}", styles['Heading1']))
    story.append(Spacer(1, 20))

    # --- Cube on the left ---
    cube_size = 40  # shrink as desired
    cube = CubeFlowable(size=cube_size)
    story.append(cube)

    story.append(Spacer(1, 20))

    # --- Scramble moves (icons) on the right ---
    icon_size = 40  # pixels
    icons = []
    for move in scramble_seq.split():
        # Convert prime moves to filenames, e.g., R' -> R_prime.png
        filename = move.replace("'", "_prime") + ".png"
        filepath = os.path.join(MOVE_ICONS_DIR, filename)

        if os.path.exists(filepath):
            img = Image(filepath, width=icon_size, height=icon_size)
            icons.append(img)

    # Arrange moves horizontally
    if icons:
        table = Table([icons], hAlign='LEFT', colWidths=icon_size)
        table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ]))
        story.append(table)

    doc.build(story)

    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')


# --- View: Generate 2 cards PDF ---
def generate_two_cards_view(request):
    pattern = request.GET.get("pattern", "Face Solved")

    # --- Create PDF buffer ---
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []

    styles = getSampleStyleSheet()
    story.append(Paragraph(f"Rubik's Cube – Pattern: {pattern}", styles['Heading1']))
    story.append(Spacer(1, 20))

    # --- Loop to generate 2 cards vertically ---
    for card_index in range(2):
        scramble_seq = random.choice(PATTERNS[pattern])

        # Cube
        cube_size = 40
        cube = CubeFlowable(size=cube_size)

        # Scramble icons
        icon_size = 40
        icons = []
        for move in scramble_seq.split():
            filename = move.replace("'", "_prime") + ".png"
            filepath = os.path.join(MOVE_ICONS_DIR, filename)
            if os.path.exists(filepath):
                img = Image(filepath, width=icon_size, height=icon_size)
                icons.append(img)

        # Arrange cube left, icons right
        data = [[cube, icons if icons else Paragraph("No icons", styles['Normal'])]]
        table = Table(data, colWidths=[cube.width + 10, 300], hAlign='LEFT')
        table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ]))
        story.append(table)
        story.append(Spacer(1, 50))  # space between cards

    doc.build(story)
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')
