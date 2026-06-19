with open(r"C:\Users\andre\Desktop\blender-mcp\addon.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

print("Searching for get_viewport_screenshot in addon.py:")
for i, line in enumerate(lines):
    if "def get_viewport_screenshot" in line:
        print(f"Line {i+1}: {line.strip()}")
        for j in range(i, min(i+100, len(lines))):
            print(f"  {j+1}: {lines[j]}", end="")
        print("\n" + "="*40 + "\n")
