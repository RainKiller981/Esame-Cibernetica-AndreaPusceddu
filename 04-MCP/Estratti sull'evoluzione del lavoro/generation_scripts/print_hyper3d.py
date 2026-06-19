with open(r"C:\Users\andre\Desktop\blender-mcp\addon.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i in range(1125, min(1160, len(lines))):
    print(f"{i+1}: {lines[i]}", end="")
