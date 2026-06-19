import socket
import json

def send_command(command_type, params=None):
    if params is None:
        params = {}
    host = '127.0.0.1'
    port = 9876
    payload = {"type": command_type, "params": params}
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.sendall(json.dumps(payload).encode('utf-8'))
    response = b""
    while True:
        chunk = s.recv(4096)
        if not chunk:
            break
        response += chunk
    s.close()
    return json.loads(response.decode('utf-8'))

code = """
import bpy
info = {}
for obj in bpy.data.objects:
    if obj.name.startswith("Xenomorph_") or obj.name == "Floor":
        info[obj.name] = {
            "type": obj.type,
            "location": list(obj.location),
            "rotation": list(obj.rotation_euler),
            "scale": list(obj.scale),
            "parent": obj.parent.name if obj.parent else None,
            "modifiers": [m.name for m in obj.modifiers],
            "materials": [m.name for m in obj.material_slots if m.material]
        }
import json
print("INSPECT_START")
print(json.dumps(info, indent=2))
print("INSPECT_END")
"""

res = send_command("execute_code", {"code": code})
print(res.get("result", {}).get("stdout", ""))
