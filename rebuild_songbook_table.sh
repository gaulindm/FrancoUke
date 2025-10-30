#!/bin/bash
set -e  # stop if anything fails

echo "🎵 Backing up current songbook and user data..."
python manage.py dumpdata songbook --indent 2 > songbook_backup.json
python manage.py dumpdata users.CustomUser --indent 2 > users_backup.json
echo "✅ Backup complete."

echo "🔧 Rebuilding 'songbook_song' table without youtube_embeddable..."
python manage.py dbshell <<'EOF'
CREATE TABLE songbook_song_new AS 
SELECT 
    id,
    songTitle,
    songChordPro,
    lyrics_with_chords,
    metadata,
    date_posted,
    acknowledgement,
    site_name,
    contributor_id,
    scroll_speed,
    revised_on
FROM songbook_song;

DROP TABLE songbook_song;
ALTER TABLE songbook_song_new RENAME TO songbook_song;
.exit
EOF

echo "✅ Table successfully rebuilt."

echo "🧠 Resetting migrations to match current model state..."
python manage.py migrate --fake songbook zero
python manage.py migrate --fake
echo "✅ Migrations faked successfully."

echo "📦 Restoring backed-up data..."
python manage.py loaddata users_backup.json
python manage.py loaddata songbook_backup.json
echo "✅ Data restored."

echo "🔍 Verifying final schema..."
python manage.py dbshell <<'EOF'
PRAGMA table_info(songbook_song);
.exit
EOF

echo "🎉 All done! Your songbook_song table is now clean and synchronized with your Django model."
