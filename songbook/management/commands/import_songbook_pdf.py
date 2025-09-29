import re
from pathlib import Path
import pdfplumber
from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from songbook.models import Song  # adjust app name!


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

    # Prepend metadata block (can expand later)
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
        r"(?i)intro:": "{soi}",
        r"(?i)verse:": "{sov}",
        r"(?i)chorus:": "{soc}",
        r"(?i)bridge:": "{sob}",
        r"(?i)outro:": "{soo}",
    }
    for pattern, repl in replacements.items():
        text = re.sub(pattern, repl, text)

    lines.extend(text.splitlines())
    return "\n".join(lines)


class Command(BaseCommand):
    help = "Convert one or more PDFs into ChordPro format and save to DB or .cho files"

    def add_arguments(self, parser):
        parser.add_argument("input_path", type=str, help="Path to PDF file or directory")
        parser.add_argument(
            "--to-db", action="store_true", help="Save output directly into Song model"
        )
        parser.add_argument(
            "--contributor-id",
            type=int,
            help="Contributor user ID (required if saving to DB)",
        )

    def handle(self, *args, **options):
        input_path = Path(options["input_path"])

        if not input_path.exists():
            raise CommandError(f"Path does not exist: {input_path}")

        pdf_files = []
        if input_path.is_file() and input_path.suffix.lower() == ".pdf":
            pdf_files = [input_path]
        elif input_path.is_dir():
            pdf_files = list(input_path.glob("*.pdf"))
        else:
            raise CommandError("Input must be a PDF file or a directory containing PDFs")

        if not pdf_files:
            raise CommandError("No PDF files found.")

        for pdf_file in pdf_files:
            try:
                chordpro_text = pdf_to_chordpro_text(pdf_file)

                if options["to_db"]:
                    contributor_id = options.get("contributor_id")
                    if not contributor_id:
                        raise CommandError("--contributor-id is required with --to-db")

                    song = Song.objects.create(
                        songTitle=pdf_file.stem,  # fallback: filename
                        songChordPro=chordpro_text,
                        metadata={"source": str(pdf_file)},
                        date_posted=timezone.now(),
                        contributor_id=contributor_id,
                        site_name="StrumSphere",  # ✅ Default applied
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
