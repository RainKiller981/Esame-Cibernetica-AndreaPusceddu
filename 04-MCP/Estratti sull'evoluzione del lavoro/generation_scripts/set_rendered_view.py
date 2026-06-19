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

# Change viewport shading to RENDERED to see materials and lighting
changed = False
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'RENDERED'
                # Also hide overlays for a clean high-quality shot!
                space.show_overlays = False
                changed = True
                print("Viewport shading set to RENDERED, overlays hidden.")

if not changed:
    print("Could not find VIEW_3D space.")
"""

res = send_command("execute_code", {"code": code})
print(res.get("result", {}).get("stdout", ""))
