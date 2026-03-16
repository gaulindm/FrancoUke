# cube/management/commands/fix_sticker_colors.py
#
# For any CubeState where U centre is still Yellow (Y):
#   - Swaps Y ↔ W  (yellow and white)
#   - Swaps R ↔ O  (red and orange)
#
# Usage:
#   python manage.py fix_sticker_colors --dry-run
#   python manage.py fix_sticker_colors
#   python manage.py fix_sticker_colors --method cfop --dry-run

import copy
from django.core.management.base import BaseCommand
from cube.models import CubeState

SWAP_MAP = {
    'Y': 'W',
    'W': 'Y',
    'R': 'O',
    'O': 'R',
}


def swap_colours(json_state):
    """
    Return a NEW json_state with Y↔W and R↔O swapped throughout.
    X (greyed) and G/B are left completely untouched.
    Original dict is never mutated.
    """
    state = copy.deepcopy(json_state)
    cube  = state['cube']

    for face_key, face in cube.items():
        for r, row in enumerate(face):
            for c, sticker in enumerate(row):
                cube[face_key][r][c] = SWAP_MAP.get(sticker, sticker)

    return state


def centre_colour(json_state, face):
    return json_state['cube'][face][1][1]


class Command(BaseCommand):
    help = (
        'Swap Y↔W and R↔O sticker colours in CubeState records '
        'where U centre is still Yellow'
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
            help='Only fix records with this method (e.g. cfop, beginner)',
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
            f"\n{'DRY RUN — ' if dry_run else ''}"
            f"Checking {total} records for yellow-top stickers\n"
        )
        self.stdout.write("─" * 60)

        for cs in qs:
            if not cs.json_state or 'cube' not in cs.json_state:
                self.stdout.write(
                    self.style.WARNING(
                        f"  SKIP  {cs.slug:35s} — no valid json_state"
                    )
                )
                skipped += 1
                continue

            u_centre = centre_colour(cs.json_state, 'U')

            # Already white on top? Nothing to do.
            if u_centre != 'Y':
                self.stdout.write(
                    f"  OK    {cs.slug:35s} — U centre is {u_centre}, skipping"
                )
                skipped += 1
                continue

            try:
                new_state  = swap_colours(cs.json_state)
                new_u      = centre_colour(new_state, 'U')
                new_f      = centre_colour(new_state, 'F')
                new_r      = centre_colour(new_state, 'R')

                self.stdout.write(
                    self.style.SUCCESS(
                        f"  {'WOULD FIX' if dry_run else 'FIXED':12s} "
                        f"{cs.slug:35s} — "
                        f"U:{u_centre}→{new_u}  "
                        f"F:{centre_colour(cs.json_state,'F')}→{new_f}  "
                        f"R:{centre_colour(cs.json_state,'R')}→{new_r}"
                    )
                )

                if not dry_run:
                    cs.json_state = new_state
                    cs.save()

                updated += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  ERROR {cs.slug:35s} — {e}")
                )
                errors += 1

        self.stdout.write("─" * 60)
        self.stdout.write(
            f"\n{'Would fix' if dry_run else 'Fixed'}: {updated}"
            f"  |  Already correct: {skipped}"
            f"  |  Errors: {errors}"
            f"  |  Total: {total}\n"
        )

        if dry_run and updated > 0:
            self.stdout.write(
                self.style.WARNING(
                    "  → Run without --dry-run to apply these changes.\n"
                )
            )