from django.db import models
from django.utils.text import slugify
from django.utils.safestring import mark_safe
import re


class CubeState(models.Model):
    METHOD_CHOICES = [
        ("cubienewbie", "CubieNewbie"),
        ("beginner", "Beginner"),
        ("cfop", "CFOP"),
        ("roux", "Roux"),
        ("zz", "ZZ"),
    ]

    DIFFICULTY_CHOICES = [
        ('facile', 'Facile'),
        ('moyen', 'Moyen'),
        ('difficile', 'Difficile'),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    json_state = models.JSONField()
    json_highlight = models.JSONField(blank=True, null=True)
    algorithm = models.TextField(blank=True)
    description = models.TextField(blank=True)
    step_number = models.PositiveIntegerField(default=1)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default="beginner")
    hand_orientation = models.CharField(
        max_length=10,
        choices=[('right', 'Main Droite'), ('left', 'Main Gauche')],
        default='right',
    )
    category = models.CharField(max_length=50, blank=True)
    difficulty = models.CharField(max_length=20, blank=True, choices=DIFFICULTY_CHOICES)
    roofpig_setup = models.TextField(blank=True)
    roofpig_colored = models.TextField(blank=True)
    roofpig_flags = models.CharField(max_length=200, blank=True, default='showalg')
    camera_longitude = models.FloatField(
        default=-25.0,
        help_text="cubing.js camera horizontal angle. Negative = more front face visible."
    )
    camera_latitude = models.FloatField(
        default=22.0,
        help_text="cubing.js camera vertical angle. Higher = more top-down view."
    )
    stickering = models.CharField(
        max_length=30,
        blank=True,
        default='full',
        help_text="cubing.js stickering: full | OLL | PLL | F2L | LL | Cross"
    )
 

    # ── Left-hand substitution ─────────────────────────────────────────────
    # Students hold the cube in their right hand and move with their left.
    # The ANIMATION stays as F/F' (correct face shown in Roofpig).
    # The SVG ICONS show L/L' (what the student's left hand actually does).
    LEFT_HAND_MAP = {
        'F':  'L',
        "F'": "L'",
        'F2': 'L2',
    }

    def _apply_hand_substitution(self, moves):
        """
        Swap F-family moves to L-family for left-hand students.
        Only applied to SVG icon display — NOT to Roofpig.
        """
        if self.hand_orientation != 'left':
            return moves
        return [self.LEFT_HAND_MAP.get(m, m) for m in moves]

    def get_clean_algorithm(self):
        """
        Return the algorithm as a plain list of moves with grouping notation
        stripped, WITHOUT hand substitution.

        Used by get_roofpig_config() so the animation always shows the
        original F/F' moves animating the correct face.

        "(R U' R') [F' U F]"  ->  ['R', "U'", "R'", "F'", 'U', 'F']
        """
        return re.sub(r'[(){}\[\]]', '', self.algorithm).split()

    def get_algorithm_svg(self):
        """
        Generate SVG icons from algorithm string.
          - ( ) groups  -> Rubik's blue  (#0051A8)
          - [ ] groups  -> Rubik's red   (#C41E3A)
          - Left-hand substitution IS applied here so icons show what
            the student's hand actually does (L/L' instead of F/F').
        """
        if not self.algorithm or self.algorithm.strip() == '':
            return ''

        def move_to_svg(move, extra_class=''):
            # Substitute for display only
            display_move = self._apply_hand_substitution([move])[0]
            svg_id = display_move.replace("'", "-prime")
            css = f'move-icon {extra_class}'.strip()
            return (f'<svg class="{css}" aria-label="{display_move}" '
                f'width="82" height="82" style="width:82px;height:82px;min-width:0">'
                f'<use href="#{svg_id}"/></svg>')

        alg = self.algorithm.strip()
        tokens = []
        i = 0
        while i < len(alg):
            ch = alg[i]
            if ch == '(':
                depth, j = 1, i + 1
                while j < len(alg) and depth:
                    if alg[j] == '(':   depth += 1
                    elif alg[j] == ')': depth -= 1
                    j += 1
                inner = alg[i+1:j-1].strip()
                tokens.append({'type': 'group-paren',
                               'moves': [m for m in inner.split() if m]})
                i = j
            elif ch == '[':
                depth, j = 1, i + 1
                while j < len(alg) and depth:
                    if alg[j] == '[':   depth += 1
                    elif alg[j] == ']': depth -= 1
                    j += 1
                inner = alg[i+1:j-1].strip()
                tokens.append({'type': 'group-bracket',
                               'moves': [m for m in inner.split() if m]})
                i = j
            elif ch == ' ':
                i += 1
            else:
                j = i
                while j < len(alg) and alg[j] not in (' ', '(', ')', '[', ']'):
                    j += 1
                move = alg[i:j].strip()
                if move:
                    tokens.append({'type': 'move', 'moves': [move]})
                i = j

        parts = []
        for token in tokens:
            ttype = token['type']
            moves = token['moves']
            if ttype == 'group-paren':
                icons = ''.join(move_to_svg(m, 'group-paren') for m in moves)
                parts.append(
                    f'<span class="move-group move-group--paren">'
                    f'<span class="move-bracket">(</span>{icons}'
                    f'<span class="move-bracket">)</span></span>'
                )
            elif ttype == 'group-bracket':
                icons = ''.join(move_to_svg(m, 'group-bracket') for m in moves)
                parts.append(
                    f'<span class="move-group move-group--bracket">'
                    f'<span class="move-bracket">[</span>{icons}'
                    f'<span class="move-bracket">]</span></span>'
                )
            else:
                parts.append(move_to_svg(moves[0]))

        return mark_safe('\n'.join(parts))

    def get_roofpig_config(self):
        """
        Generate Roofpig configuration string.
          - Brackets stripped (Roofpig cannot parse them)
          - NO hand substitution — Roofpig receives the original F/F' moves
            so the animation shows the correct face moving.
        """
        config_parts = []

        clean_moves = self.get_clean_algorithm()   # brackets only, no F->L swap
        if clean_moves:
            config_parts.append(f"alg={' '.join(clean_moves)}")

        if self.roofpig_setup:
            config_parts.append(f"setup={self.roofpig_setup}")
        if self.roofpig_colored:
            config_parts.append(f"colored={self.roofpig_colored}")

        flags = self.roofpig_flags or 'showalg'
        config_parts.append(f"flags={flags}")
        config_parts.append("hover=2")

        return " | ".join(config_parts)
    
    @staticmethod
    def invert_alg(alg):
        """
        Compute the inverse of an algorithm string.
 
        Used to auto-generate the setup position for cubing.js.
        Strips grouping brackets before inverting.
 
        "R U R'"  →  "R U' R'"  (inverse)
        """
        if not alg or not alg.strip():
            return ''
        # Strip grouping notation so brackets don't confuse the parser
        clean = re.sub(r'[(){}\[\]]', '', alg).strip()
        moves = clean.split()
        inverted = []
        for m in reversed(moves):
            if not m:
                continue
            if m.endswith("'"):
                inverted.append(m[:-1])       # R'  → R
            elif m.endswith('2'):
                inverted.append(m)             # R2  → R2  (self-inverse)
            else:
                inverted.append(m + "'")       # R   → R'
        return ' '.join(inverted)
 
    def get_setup_alg(self):
        """
        Return the cubing.js setup algorithm.
 
        Priority:
          1. Use roofpig_setup if it was manually set (backward compat)
          2. Otherwise auto-invert the main algorithm
 
        This means you never NEED to fill roofpig_setup again —
        it just works automatically.
        """
        if self.roofpig_setup and self.roofpig_setup.strip():
            return self.roofpig_setup
        return self.invert_alg(self.algorithm)



    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name