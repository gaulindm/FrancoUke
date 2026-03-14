# cube/management/commands/rotate_y.py
#
# Applies a y rotation to every CubeState json_state.
# y = clockwise horizontal rotation (like a U move on the whole cube):
#
#   F ← R   (Green comes to front)
#   R ← B   (Red comes to right)
#   B ← L   (Blue goes to back)
#   L ← F   (Orange goes to left)
#   U stays U  (rotates clockwise internally)
#   D stays D  (rotates counter-clockwise internally)
#
# Result: White top, Green front, Red right, Yellow bottom, Blue back, Orange left
#         = standard WCA / Franco-Ontarien orientation ✅
#
# Usage:
#   python manage.py rotate_y --dry-run      ← preview, touches nothing
#   python manage.py rotate_y                ← actually updates the DB

import copy
from django.core.management.base import BaseCommand
from cube.models import CubeState


def rotate_face_cw(face):
    """Rotate a 3x3 face 90° clockwise."""
    return [
        [face[2][0], face[1][0], face[0][0]],
        [face[2][1], face[1][1], face[0][1]],
        [face[2][2], face[1][2], face[0][2]],
    ]


def rotate_face_ccw(face):
    """Rotate a 3x3 face 90° counter-clockwise."""
    return [
        [face[0][2], face[1][2], face[2][2]],
        [face[0][1], face[1][1], face[2][1]],
        [face[0][0], face[1][0], face[2][0]],
    ]


def rotate_y(json_state):
    """
    Return a NEW json_state dict with y rotation applied.
    Original is never mutated.
    """
    state = copy.deepcopy(json_state)
    cube  = state['cube']

    old_F = cube['F']
    old_R = cube['R']
    old_B = cube['B']
    old_L = cube['L']
    old_U = cube['U']
    old_D = cube['D']

    # Horizontal faces just swap
    cube['F'] = old_R
    cube['R'] = old_B
    cube['B'] = old_L
    cube['L'] = old_F

    # U rotates clockwise, D rotates counter-clockwise
    cube['U'] = rotate_face_cw(old_U)
    cube['D'] = rotate_face_ccw(old_D)

    return state


def centre_colour(face):
    """Return the centre sticker of a face — always [1][1]."""
    return face[1][1]


class Command(BaseCommand):
    help = (
        'Rotate all CubeState json_state records by y '
        '(Green to front, Red to right — standard WCA orientation)'
    )

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

        total   = qs.count()
        updated = 0
        skipped = 0
        errors  = 0

        self.stdout.write(
            f"\n{'DRY RUN — ' if dry_run else ''}Rotating {total} records (y)\n"
        )
        self.stdout.write("─" * 60)

        for cs in qs:
            if not cs.json_state or 'cube' not in cs.json_state:
                self.stdout.write(
                    self.style.WARNING(
                        f"  SKIP  {cs.slug:30s} — no valid json_state"
                    )
                )
                skipped += 1
                continue

            current_F_centre = centre_colour(cs.json_state['cube']['F'])
            current_R_centre = centre_colour(cs.json_state['cube']['R'])

            # Already green in front and red on right? Skip.
            if current_F_centre == 'G' and current_R_centre == 'R':
                self.stdout.write(
                    f"  OK    {cs.slug:30s} — already green front / red right, skipping"
                )
                skipped += 1
                continue

            try:
                new_state    = rotate_y(cs.json_state)
                new_F_centre = centre_colour(new_state['cube']['F'])
                new_R_centre = centre_colour(new_state['cube']['R'])

                self.stdout.write(
                    self.style.SUCCESS(
                        f"  {'WOULD UPDATE' if dry_run else 'UPDATED':12s} "
                        f"{cs.slug:30s} — "
                        f"F: {current_F_centre}→{new_F_centre}  "
                        f"R: {current_R_centre}→{new_R_centre}"
                    )
                )

                if not dry_run:
                    cs.json_state = new_state
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