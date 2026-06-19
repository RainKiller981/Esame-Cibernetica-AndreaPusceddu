with open(r"C:\Users\andre\Desktop\blender-mcp\addon.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

print("Searching for command handling:")
for i, line in enumerate(lines):
    if "def execute" in line or "handle_command" in line or 'type == "' in line or 'type" == ' in line or "command_type" in line:
        print(f"Line {i+1}: {line.strip()}")
