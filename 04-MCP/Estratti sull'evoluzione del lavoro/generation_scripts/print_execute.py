with open(r"C:\Users\andre\Desktop\blender-mcp\addon.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i in range(188, min(300, len(lines))):
    print(f"{i+1}: {lines[i]}", end="")
