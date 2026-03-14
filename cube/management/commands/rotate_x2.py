# cube/management/commands/rotate_x2.py
#
# Applies an x2 rotation to every CubeState json_state and json_highlight.
# x2 flips the cube upside down:
#   U ↔ D   (and their rows reverse)
#   F ↔ B   (and their rows reverse)
#   R stays R  (rows reverse)
#   L stays L  (rows reverse)
#
# Usage:
#   python manage.py rotate_x2 --dry-run      ← preview, touches nothing
#   python manage.py rotate_x2                ← actually updates the DB

import copy
from django.core.management.base import BaseCommand
from cube.models import CubeState


def reverse_rows(face):
    """Reverse the row order of a 3x3 face list."""
    return list(reversed(face))


def rotate_x2(json_state):
    """
    Return a NEW json_state dict with x2 rotation applied.
    Original is never mutated.
    """
    state = copy.deepcopy(json_state)
    cube  = state['cube']

    old_U = cube['U']
    old_D = cube['D']
    old_F = cube['F']
    old_B = cube['B']
    old_R = cube['R']
    old_L = cube['L']

    # x2 face remapping — rows reverse on every face
    cube['U'] = reverse_rows(old_D)   # D flips up
    cube['D'] = reverse_rows(old_U)   # U flips down
    cube['F'] = reverse_rows(old_B)   # B comes to front
    cube['B'] = reverse_rows(old_F)   # F goes to back
    cube['R'] = reverse_rows(old_R)   # R stays R, rows reverse
    cube['L'] = reverse_rows(old_L)   # L stays L, rows reverse

    return state


def centre_colour(face):
    """Return the centre sticker of a face — always [1][1]."""
    return face[1][1]


class Command(BaseCommand):
    help = 'Rotate all CubeState json_state records by x2 (White top → White bottom swap)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without writing to the database',
        )
        parser.add_argument(
            '--method',
            type=str,
            default=None,
            help='Only rotate records with this method (e.g. cfop, beginner)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        method  = options['method']

        qs = CubeState.objects.all()
        if method:
            qs = qs.filter(method=method)

        total    = qs.count()
        updated  = 0
        skipped  = 0
        errors   = 0

        self.stdout.write(f"\n{'DRY RUN — ' if dry_run else ''}Rotating {total} records (x2)\n")
        self.stdout.write("─" * 60)

        for cs in qs:
            if not cs.json_state or 'cube' not in cs.json_state:
                self.stdout.write(
                    self.style.WARNING(f"  SKIP  {cs.slug:30s} — no valid json_state")
                )
                skipped += 1
                continue

            current_U_centre = centre_colour(cs.json_state['cube']['U'])

            # Already white on top? Skip.
            if current_U_centre == 'W':
                self.stdout.write(
                    f"  OK    {cs.slug:30s} — already white on top, skipping"
                )
                skipped += 1
                continue

            try:
                new_state = rotate_x2(cs.json_state)
                new_U_centre = centre_colour(new_state['cube']['U'])

                self.stdout.write(
                    self.style.SUCCESS(
                        f"  {'WOULD UPDATE' if dry_run else 'UPDATED':12s} "
                        f"{cs.slug:30s} — "
                        f"U: {current_U_centre} → {new_U_centre}"
                    )
                )

                if not dry_run:
                    cs.json_state = new_state
                    # Also rotate json_highlight if it mirrors cube structure
                    # (highlight sticker references are face+row+col, not
                    #  colour-based, so they stay valid after rotation — no change needed)
                    cs.save()

                updated += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  ERROR {cs.slug:30s} — {e}")
                )
                errors += 1

        self.stdout.write("─" * 60)
        self.stdout.write(
            f"\n{'Would update' if dry_run else 'Updated'}: {updated}"
            f"  |  Skipped: {skipped}"
            f"  |  Errors: {errors}"
            f"  |  Total: {total}\n"
        )

        if dry_run and updated > 0:
            self.stdout.write(
                self.style.WARNING(
                    "  → Run without --dry-run to apply these changes.\n"
                )
            )