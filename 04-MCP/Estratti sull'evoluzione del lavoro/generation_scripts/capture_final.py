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

changed = False
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                # Switch viewport to the active Camera view
                space.region_3d.view_perspective = 'CAMERA'
                space.shading.type = 'RENDERED'
                space.show_overlays = False
                changed = True
                print("Viewport switched to CAMERA view, shading set to RENDERED, overlays hidden.")

if not changed:
    print("Could not find VIEW_3D space.")
"""

if __name__ == "__main__":
    print("Setting viewport to Camera view...")
    res_view = send_command("execute_code", {"code": code})
    print(res_view.get("result", {}).get("stdout", ""))
    
    filepath = r"C:\Users\andre\Desktop\xenomorph_and_egg.png"
    print(f"Capturing viewport screenshot to {filepath}...")
    res_snap = send_command("get_viewport_screenshot", {
        "max_size": 1200,
        "filepath": filepath,
        "format": "png"
    })
    print(json.dumps(res_snap, indent=2))
