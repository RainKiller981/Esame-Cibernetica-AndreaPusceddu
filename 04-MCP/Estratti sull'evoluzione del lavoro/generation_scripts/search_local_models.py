import os

user_dir = r"C:\Users\andre"
paths_to_check = [
    os.path.join(user_dir, "Desktop"),
    os.path.join(user_dir, "Downloads"),
    user_dir
]

extensions = (".glb", ".gltf", ".obj", ".fbx", ".zip")

print("Searching for 3D model files:")
for path in paths_to_check:
    if not os.path.exists(path):
        continue
    print(f"\nChecking directory: {path}")
    try:
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            if os.path.isfile(full_path) and item.lower().endswith(extensions):
                print(f"File found: {item} ({os.path.getsize(full_path)} bytes)")
            elif os.path.isdir(full_path):
                # check one level deep
                try:
                    for subitem in os.listdir(full_path):
                        sub_full_path = os.path.join(full_path, subitem)
                        if os.path.isfile(sub_full_path) and subitem.lower().endswith(extensions):
                            print(f"Sub-file found: {item}/{subitem} ({os.path.getsize(sub_full_path)} bytes)")
                except Exception:
                    pass
    except Exception as e:
        print(f"Error reading {path}: {e}")
