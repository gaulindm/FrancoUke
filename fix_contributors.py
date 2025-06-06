import json

# 🔄 INPUT and OUTPUT filenames
INPUT_FILE = "songbook_backup.json"
OUTPUT_FILE = "songbook_mapped.json"

# 🧑 Use your actual user ID from CustomUser (check admin or shell)
VALID_USER_ID = 1

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

for obj in data:
    if obj["model"] == "songbook.song":
        if obj["fields"]["contributor"] is not None:
            print(f"Fixing song ID {obj['pk']} contributor from {obj['fields']['contributor']} to {VALID_USER_ID}")
            obj["fields"]["contributor"] = VALID_USER_ID

# Save modified JSON
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print(f"✅ Fixed file saved as {OUTPUT_FILE}")
