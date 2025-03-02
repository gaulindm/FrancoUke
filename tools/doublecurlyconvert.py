import re
import os

def convert_chord_pro_format(file_path):
    """
    Converts chord pro format from `{{C}}` to `[C]` in a given file,
    adds metadata tags at the beginning, extracts artist and title from the first two lines,
    and saves the output to a file named after the song title.

    Args:
        file_path (str): Path to the input file.
    """
    try:
        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read the content of the file
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        if len(lines) < 2:
            raise ValueError("Input file must have at least two lines for artist and title.")
        
        # Extract artist and title from the first two lines
        artist = lines[0].strip()
        title = lines[1].strip()
        
        # Remaining content after artist and title
        content = "".join(lines[2:])
        
        # Use regular expression to find and replace patterns
        converted_content = re.sub(r"\{\{(.*?)\}\}", r"[\1]", content)
        
        # Define the metadata tags with extracted artist and title
        metadata = f"""
{{title: {title}}}
{{artist: {artist}}}
{{album: }}
{{capo: }}
{{composer: }}
{{lyricist: }}
{{key: }}
{{capo: }}
{{year: }}
{{1stnote: }}
{{tempo: }}
{{timeSignature: }}
"""

        # Combine metadata and converted content
        final_content = metadata.strip() + "\n\n" + converted_content
        
        # Define output file path based on the song title
        output_path = f"{title}.songchordpro"
        
        # Save the final content to the output file
        with open(output_path, 'w') as file:
            file.write(final_content)
        
        print(f"File successfully converted and saved to {output_path}.")
    
    except FileNotFoundError as e:
        print(f"An error occurred: {e}")
    except ValueError as e:
        print(f"An error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Example usage
if __name__ == "__main__":
    input_file = "example.txt"  # Replace with the full path if necessary
    convert_chord_pro_format(input_file)

