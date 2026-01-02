# cubing_users/constants.py
"""
Constantes pour les identités de cubeurs en français.
"""

# Les 6 couleurs du Rubik's Cube
COLORS = [
    ('Rouge', '🟥 Rouge'),
    ('Bleu', '🟦 Bleu'),
    ('Vert', '🟩 Vert'),
    ('Jaune', '🟨 Jaune'),
    ('Orange', '🟧 Orange'),
    ('Blanc', '⬜ Blanc'),
]

# Juste les noms pour les choix internes
COLOR_CHOICES = [color[0] for color in COLORS]

# Adjectifs (mots de pouvoir)
ADJECTIVES = [
    ('Rapide', 'Rapide'),
    ('Éclair', 'Éclair'),
    ('Turbo', 'Turbo'),
    ('Puissant', 'Puissant'),
    ('Génial', 'Génial'),
    ('Brillant', 'Brillant'),
    ('Habile', 'Habile'),
    ('Malin', 'Malin'),
    ('Vif', 'Vif'),
    ('Super', 'Super'),
    ('Méga', 'Méga'),
    ('Costaud', 'Costaud'),
    ('Doué', 'Doué'),
    ('Véloce', 'Véloce'),
    ('Ultime', 'Ultime'),
    ('Fulgurant', 'Fulgurant'),
    ('Rusé', 'Rusé'),
    ('Adroit', 'Adroit'),
    ('Solide', 'Solide'),
    ('Fort', 'Fort'),
]

ADJECTIVE_CHOICES = [adj[0] for adj in ADJECTIVES]

# Titres de super-héros
SUPERHEROES = [
    ('Solveur', 'Solveur'),
    ('Maître', 'Maître'),
    ('Champion', 'Champion'),
    ('Cubeur', 'Cubeur'),
    ('Ninja', 'Ninja'),
    ('Pro', 'Pro'),
    ('As', 'As'),
    ('Légende', 'Légende'),
    ('Twisteur', 'Twisteur'),
    ('Magicien', 'Magicien'),
    ('Prodige', 'Prodige'),
    ('Virtuose', 'Virtuose'),
    ('Tourneur', 'Tourneur'),
    ('Mélangeur', 'Mélangeur'),
    ('Démêleur', 'Démêleur'),
]

SUPERHERO_CHOICES = [hero[0] for hero in SUPERHEROES]

# Rôles pour les leaders
LEADER_ROLES = [
    ('teacher', 'Enseignant(e)'),
    ('coach', 'Entraîneur/Entraîneuse'),
    ('club_leader', 'Animateur/Animatrice de Club'),
    ('parent', 'Parent Responsable'),
]

# Types de groupes
GROUP_TYPES = [
    ('class', 'Classe'),
    ('club', 'Club'),
    ('team', 'Équipe'),
    ('practice', 'Groupe de Pratique'),
]

# Variantes d'avatars (expressions)
AVATAR_VARIANTS = [
    ('cool', '😎 Cool'),
    ('determined', '😤 Déterminé'),
    ('happy', '😊 Heureux'),
    ('focused', '🤓 Concentré'),
    ('excited', '🤩 Excité'),
    ('confident', '😏 Confiant'),
]

# Emojis pour les couleurs (pour affichage)
COLOR_EMOJIS = {
    'Rouge': '🟥',
    'Bleu': '🟦',
    'Vert': '🟩',
    'Jaune': '🟨',
    'Orange': '🟧',
    'Blanc': '⬜',
}

# Fonction helper pour obtenir le nom complet avec emoji
def get_color_display(color):
    """Retourne 'Rouge' -> '🟥 Rouge'"""
    emoji = COLOR_EMOJIS.get(color, '')
    return f"{emoji} {color}" if emoji else color