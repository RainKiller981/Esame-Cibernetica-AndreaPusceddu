with open(r"C:\Users\andre\Desktop\blender-mcp\addon.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

print("Searching for API Key or settings properties:")
for i, line in enumerate(lines):
    if "blendermcp_" in line or "api_key" in line.lower() or "rodin" in line.lower() or "hyper3d" in line.lower() or "secret" in line.lower():
        if "def " in line or "=" in line:
            print(f"Line {i+1}: {line.strip()}")
