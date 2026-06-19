with open(r"C:\Users\andre\Desktop\blender-mcp\addon.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

print("Searching for create_hunyuan_job in addon.py:")
for i, line in enumerate(lines):
    if "def create_hunyuan_job" in line:
        print(f"Line {i+1}: {line.strip()}")
        # print the next 100 lines
        for j in range(i, min(i+100, len(lines))):
            print(f"  {j+1}: {lines[j]}", end="")
        print("\n" + "="*40 + "\n")
