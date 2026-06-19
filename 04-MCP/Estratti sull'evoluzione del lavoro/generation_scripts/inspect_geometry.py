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
    if obj.name.startswith("Xenomorph_"):
        mesh = obj.data
        info[obj.name] = {
            "vertices": len(mesh.vertices),
            "polygons": len(mesh.polygons),
            "dimensions": list(obj.dimensions),
        }
import json
print("GEOM_START")
print(json.dumps(info, indent=2))
print("GEOM_END")
"""

res = send_command("execute_code", {"code": code})
print(res.get("result", {}).get("stdout", ""))
