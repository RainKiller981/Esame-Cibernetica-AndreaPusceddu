with open(r"C:\Users\andre\Desktop\blender-mcp\addon.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

print("Searching for render functions in addon.py:")
for i, line in enumerate(lines):
    if "def " in line and "render" in line.lower():
        print(f"Line {i+1}: {line.strip()}")
        for j in range(i, min(i+40, len(lines))):
            print(f"  {j+1}: {lines[j]}", end="")
        print("\n" + "="*40 + "\n")
