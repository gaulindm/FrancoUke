import re
from pathlib import Path
from datetime import datetime
import pdfplumber
from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from songbook.models import Song  # adjust app name


def pdf_to_chordpro_text(pdf_path: Path) -> str:
    """Extract text from PDF and convert into ChordPro string."""
    texts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            content = page.extract_text()
            if content:
                texts.append(content)

    if not texts:
        raise ValueError("No extractable text found in PDF.")

    text = "\n".join(texts)

    # Prepend empty metadata block
    lines = [
        "{title:}",
        "{artist:}",
        "{youtube:}",
        "{songwriter:}",
        "{capo:}",
        "{year:}",
        "{1stnote:}",
        "{timeSignature:}",
        "",
    ]

    # Replace (C) style chords with [C]
    text = re.sub(r"\(([^)]+)\)", r"[\1]", text)

    # Replace common section headers with ChordPro markers
    replacements = {
        r"(?i)intro[\s:\-]*": "{soi}",
        r"(?i)verse[\s:\-]*": "{sov}",
        r"(?i)chorus[\s:\-]*": "{soc}",
        r"(?i)bridge[\s:\-]*": "{sob}",
        r"(?i)outro[\s:\-]*": "{soo}",
    }
    for pattern, repl in replacements.items():
        text = re.sub(pattern, repl, text)

    lines.extend(text.splitlines())
    return "\n".join(lines)


def extract_revision_date_from_filename(pdf_path: Path):
    """
    Extract revision date from file name in format:
    Song Title (Month Day, Year).pdf
    Returns a date object or None.
    """
    match = re.search(r'\(([^)]+)\)\.pdf$', pdf_path.name)
    if match:
        date_str = match.group(1)
        try:
            return datetime.strptime(date_str, "%B %d, %Y").date()
        except ValueError:
            return None
    return None


class Command(BaseCommand):
    help = "Convert PDFs to ChordPro format and optionally save to DB with revision date from file name"

    def add_arguments(self, parser):
        parser.add_argument("input_path", type=str, help="Path to PDF file or directory")
        parser.add_argument(
            "--to-db",
            action="store_true",
            help="Save output directly into Song model",
        )
        parser.add_argument(
            "--contributor-id",
            type=int,
            help="Contributor user ID (required if saving to DB)",
        )
        parser.add_argument(
            "--site-name",
            choices=["StrumSphere", "FrancoUke"],
            default=None,  # Leave empty to hide the song
            help="Site name for imported songs (optional, leave empty to hide)",
        )

    def handle(self, *args, **options):
        input_path = Path(options["input_path"])

        if not input_path.exists():
            raise CommandError(f"Path does not exist: {input_path}")

        # Collect PDF files
        pdf_files = []
        if input_path.is_file() and input_path.suffix.lower() == ".pdf":
            pdf_files = [input_path]
        elif input_path.is_dir():
            pdf_files = list(input_path.glob("*.pdf"))
        else:
            raise CommandError(
                "Input must be a PDF file or a directory containing PDFs"
            )

        if not pdf_files:
            raise CommandError("No PDF files found.")

        for i, pdf_file in enumerate(pdf_files, 1):
            self.stdout.write(f"[{i}/{len(pdf_files)}] Processing {pdf_file.name}...")
            try:
                chordpro_text = pdf_to_chordpro_text(pdf_file)
                revision_date = extract_revision_date_from_filename(pdf_file)

                if options["to_db"]:
                    contributor_id = options.get("contributor_id")
                    if not contributor_id:
                        raise CommandError(
                            "--contributor-id is required with --to-db"
                        )

                    song = Song.objects.create(
                        songTitle=pdf_file.stem,  # fallback filename
                        songChordPro=chordpro_text,
                        revised_on=revision_date,
                        metadata={"source": str(pdf_file)},
                        date_posted=timezone.now(),
                        contributor_id=contributor_id,
                        site_name=options["site_name"],  # can be None
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f"Saved to DB: {song.songTitle}")
                    )
                else:
                    # Write to .cho file
                    output_path = pdf_file.with_suffix(".cho")
                    output_path.write_text(chordpro_text, encoding="utf-8")
                    self.stdout.write(self.style.SUCCESS(f"Saved file: {output_path}"))

            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Failed for {pdf_file}: {e}"))



"""
🚀 Import Songbook PDFs Command - Usage Instructions

This command converts PDF files into ChordPro format and optionally saves them to the database. 
It also automatically detects the revision date from the file name if it is in the format:
    Song Title (Month Day, Year).pdf
and stores it in the `revised_on` field.

------------------------------------------------------------
1️⃣ Convert a single PDF to a .cho file (does NOT touch the database):

python manage.py import_songbook_pdf path/to/song.pdf

- Creates `song.cho` in the same folder as the PDF
- Leaves database untouched

------------------------------------------------------------
2️⃣ Convert a folder of PDFs to .cho files (no database changes):

python manage.py import_songbook_pdf path/to/folder/

- Loops through all `.pdf` files in the folder
- Creates a `.cho` file for each PDF in the same folder

------------------------------------------------------------
3️⃣ Convert a single PDF and save to the database:

python manage.py import_songbook_pdf path/to/song.pdf --to-db --contributor-id=1

- Extracts text from the PDF
- Converts it to ChordPro
- Saves a new Song object in the database with:
    - songTitle = filename by default (including revision date)
    - songChordPro = full ChordPro text
    - revised_on = extracted from file name if present (e.g., "(September 3, 2025)")
    - site_name = None (hidden) unless specified with --site-name
    - contributor = user with ID 1

------------------------------------------------------------
4️⃣ Convert a folder of PDFs and save all to the database:

python manage.py import_songbook_pdf path/to/folder/ --to-db --contributor-id=1

- Processes all `.pdf` files in the folder
- Creates one Song DB entry per PDF
- revision date is extracted from the file name if present
- site_name remains hidden by default

------------------------------------------------------------
5️⃣ Make songs visible on a specific site:

python manage.py import_songbook_pdf path/to/folder/ --to-db --contributor-id=1 --site-name=StrumSphere

- Use `--site-name=StrumSphere` or `--site-name=FrancoUke`
- If omitted, the song will remain hidden (site_name = None)

------------------------------------------------------------
📌 Notes:

- File name format for automatic revision date detection:
    Song Title (Month Day, Year).pdf
    Example: Be My Baby (September 3, 2025).pdf

- If the revision date is not in the file name, `revised_on` remains blank.

- Works for both **single PDF files** and **entire folders**.

"""
