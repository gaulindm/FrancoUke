# cube/management/commands/rotate_y_prime.py
#
# Applies a y' rotation — the REVERSE of rotate_y.
# Undoes: Green front / Red right → back to Orange front / Green right
#
#   F ← L   (Orange comes to front)
#   L ← B   (Blue comes to left)
#   B ← R   (Green goes to back)
#   R ← F   (Orange... wait no)
#
# y' mapping:
#   F ← L
#   L ← B
#   B ← R
#   R ← F
#   U rotates counter-clockwise
#   D rotates clockwise
#
# Usage:
#   python manage.py rotate_y_prime --dry-run
#   python manage.py rotate_y_prime

import copy
from django.core.management.base import BaseCommand
from cube.models import CubeState


def rotate_face_cw(face):
    return [
        [face[2][0], face[1][0], face[0][0]],
        [face[2][1], face[1][1], face[0][1]],
        [face[2][2], face[1][2], face[0][2]],
    ]


def rotate_face_ccw(face):
    return [
        [face[0][2], face[1][2], face[2][2]],
        [face[0][1], face[1][1], face[2][1]],
        [face[0][0], face[1][0], face[2][0]],
    ]


def rotate_y_prime(json_state):
    state = copy.deepcopy(json_state)
    cube  = state['cube']

    old_F = cube['F']
    old_R = cube['R']
    old_B = cube['B']
    old_L = cube['L']
    old_U = cube['U']
    old_D = cube['D']

    # y' is opposite of y
    cube['F'] = old_L
    cube['L'] = old_B
    cube['B'] = old_R
    cube['R'] = old_F

    # U rotates counter-clockwise, D rotates clockwise
    cube['U'] = rotate_face_ccw(old_U)
    cube['D'] = rotate_face_cw(old_D)

    return state


def centre_colour(face):
    return face[1][1]


class Command(BaseCommand):
    help = 'Reverse of rotate_y — restores orientation before rotate_y was run'

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
            f"\n{'DRY RUN — ' if dry_run else ''}Rotating {total} records (y')\n"
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

            current_F = centre_colour(cs.json_state['cube']['F'])
            current_R = centre_colour(cs.json_state['cube']['R'])

            # Already orange front / green right? Skip — already undone.
            if current_F == 'O' and current_R == 'G':
                self.stdout.write(
                    f"  OK    {cs.slug:30s} — already orange front, skipping"
                )
                skipped += 1
                continue

            try:
                new_state = rotate_y_prime(cs.json_state)
                new_F = centre_colour(new_state['cube']['F'])
                new_R = centre_colour(new_state['cube']['R'])

                self.stdout.write(
                    self.style.SUCCESS(
                        f"  {'WOULD UPDATE' if dry_run else 'UPDATED':12s} "
                        f"{cs.slug:30s} — "
                        f"F: {current_F}→{new_F}  R: {current_R}→{new_R}"
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