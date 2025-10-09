#Importing songs from a folder from shell
#Script provided by chatGPT



#After modifying the model, run migrations:


#python manage.py makemigrations
#python manage.py migrate





#STEP 1:  Run following command in terminal
#python manage.py shell


#STEP 2: Copy and Paste following script


exec("""
import os
from django.contrib.auth.models import User
from songbook.models import Song
# Define the directory containing your ChordPro files
chordpro_dir = 'mychordpro'
# Fetch or create the User instance for "Gaulind"
contributor_user, created = User.objects.get_or_create(username="Gaulind")
# Counter to track imported files
imported_count = 0
# Loop through all .pro files in the directory
for filename in os.listdir(chordpro_dir):
    if filename.endswith('.pro'):
        # Construct the full path to the file
        file_path = os.path.join(chordpro_dir, filename)
        # Open and read the file content
        with open(file_path, 'r') as file:
            chordpro_text = file.read()
            # Assign a default title based on the filename if no title is extracted
            title = filename.rsplit('.', 1)[0]
            # Create a new Song instance with the file content and the User instance as contributor
            song = Song(songTitle=title, songChordPro=chordpro_text, contributor=contributor_user)
            song.save()
            # Increment the counter
            imported_count += 1
            print(f"Imported: {filename}")
# Print the total count of imported songs
print(f"Total songs imported: {imported_count}")
""")