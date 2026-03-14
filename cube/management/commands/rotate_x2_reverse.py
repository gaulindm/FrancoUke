# cube/management/commands/rotate_x2_reverse.py
#
# Reverses rotate_x2 — identical transformation (x2 is self-inverse)
# but skip logic looks for WHITE on top (original had YELLOW on top).
#
# Run AFTER rotate_y_prime to fully restore original orientation:
#   Yellow top, Orange front, Green right
#
# Usage:
#   python manage.py rotate_x2_reverse --dry-run
#   python manage.py rotate_x2_reverse

import copy
from django.core.management.base import BaseCommand
from cube.models import CubeState


def reverse_rows(face):
    return list(reversed(face))


def rotate_x2(json_state):
    state = copy.deepcopy(json_state)
    cube  = state['cube']

    old_U = cube['U']
    old_D = cube['D']
    old_F = cube['F']
    old_B = cube['B']
    old_R = cube['R']
    old_L = cube['L']

    cube['U'] = reverse_rows(old_D)
    cube['D'] = reverse_rows(old_U)
    cube['F'] = reverse_rows(old_B)
    cube['B'] = reverse_rows(old_F)
    cube['R'] = reverse_rows(old_R)
    cube['L'] = reverse_rows(old_L)

    return state


def centre_colour(face):
    return face[1][1]


class Command(BaseCommand):
    help = 'Reverse of rotate_x2 — restores Yellow on top / White on bottom'

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
            f"\n{'DRY RUN — ' if dry_run else ''}Rotating {total} records (x2 reverse)\n"
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

            current_U = centre_colour(cs.json_state['cube']['U'])

            # Already yellow on top? Already restored — skip.
            if current_U == 'Y':
                self.stdout.write(
                    f"  OK    {cs.slug:30s} — already yellow on top, skipping"
                )
                skipped += 1
                continue

            try:
                new_state = rotate_x2(cs.json_state)
                new_U = centre_colour(new_state['cube']['U'])

                self.stdout.write(
                    self.style.SUCCESS(
                        f"  {'WOULD UPDATE' if dry_run else 'UPDATED':12s} "
                        f"{cs.slug:30s} — "
                        f"U: {current_U}→{new_U}"
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