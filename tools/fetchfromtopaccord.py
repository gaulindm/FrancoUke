from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import unicodedata
import time

def fetch_and_convert_chord_pro(url, login_url, username, password):
    try:
        # Set up the Selenium WebDriver
        driver = webdriver.Chrome()  # Ensure ChromeDriver is installed and in PATH
        wait = WebDriverWait(driver, 20)  # Increase timeout to 20 seconds

        # Navigate to the login page
        driver.get(login_url)

        # Debug: Save login page source
        with open("login_page_source.html", "w", encoding="utf-8") as file:
            file.write(driver.page_source)

        # Locate and fill the username and password fields
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))  # Adjust selector
        password_field = driver.find_element(By.NAME, "password")  # Adjust selector
        username_field.send_keys(username)
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)

        # Wait for login to complete
        wait.until(EC.url_changes(login_url))

        # Navigate to the target page
        driver.get(url)

        # Debug: Save target page source
        with open("target_page_source.html", "w", encoding="utf-8") as file:
            file.write(driver.page_source)

        # Locate the <textarea> containing the ChordPro content
        textarea = wait.until(EC.presence_of_element_located((By.NAME, "content")))
        chord_content = textarea.get_attribute("value")

        # Extract artist and song title from the URL
        path_segments = url.strip('/').split('/')
        artist = path_segments[2]
        song_title = path_segments[3]

        # Convert chord markers from `{{C}}` to `[C]`
        converted_content = re.sub(r"\{\{(.*?)\}\}", r"[\1]", chord_content)

        # Define metadata
        metadata = f"""
{{title: {song_title}}}
{{artist: {artist}}}
{{album: }}
{{capo: }}
{{composer: }}
{{lyricist: }}
{{key: }}
{{keymatch: }}
{{year: }}
{{1stnote: }}
{{tempo: }}
{{timeSignature: }}
"""

        # Combine metadata and content
        final_content = metadata.strip() + "\n\n" + converted_content

        # Create a safe filename
        def slugify(value, allow_unicode=False):
            value = str(value)
            if allow_unicode:
                value = unicodedata.normalize('NFKC', value)
            else:
                value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
            value = re.sub(r'[^\w\s-]', '', value.lower())
            return re.sub(r'[-\s]+', '-', value).strip('-_')

        safe_song_title = slugify(song_title)
        output_filename = f"{safe_song_title}.songchordpro"

        # Save the final content to a file
        with open(output_filename, 'w', encoding='utf-8') as file:
            file.write(final_content)

        print(f"File successfully converted and saved to {output_filename}.")

    finally:
        # Close the browser
        driver.quit()

# Example usage
if __name__ == "__main__":
    login_url = "https://www.topaccords.com/login"  # Replace with the actual login URL
    url = "https://www.topaccords.com/custom/jean-jacques-goldman/quand-la-musique-est-bonne/1/create"  # Replace with the actual URL
    username = "gaulindm@gmail.com"  # Replace with your username
    password = ",m582^7+*Gy86Ea"  # Replace with your password

    fetch_and_convert_chord_pro(url, login_url, username, password)
