import os

user_dir = r"C:\Users\andre"
filename_to_search = "nostromo_shot_1_claustrophobia.png"

print(f"Searching for {filename_to_search} in {user_dir}...")
found_paths = []
for root, dirs, files in os.walk(user_dir):
    # Skip AppData, .gemini, and hidden folders to be fast
    if "AppData" in root or ".gemini" in root or ".git" in root or ".DS_Store" in root:
        continue
    if filename_to_search in files:
        full_path = os.path.join(root, filename_to_search)
        print(f"Found: {full_path}")
        found_paths.append(full_path)

if not found_paths:
    print("Not found anywhere in user directory!")
