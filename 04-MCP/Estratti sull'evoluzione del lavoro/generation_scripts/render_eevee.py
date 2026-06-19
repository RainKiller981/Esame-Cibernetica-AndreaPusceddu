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

# Set active camera
camera = bpy.data.objects.get("Camera")
if camera:
    bpy.context.scene.camera = camera

# Use Eevee engine for fast, beautiful rendering
bpy.context.scene.render.engine = 'BLENDER_EEVEE'

# Set resolution and output path
bpy.context.scene.render.resolution_x = 1200
bpy.context.scene.render.resolution_y = 800
bpy.context.scene.render.resolution_percentage = 100
bpy.context.scene.render.filepath = r"C:\\Users\\andre\\Desktop\\xenomorph_and_egg.png"
bpy.context.scene.render.image_settings.file_format = 'PNG'

# Render still image
print("Rendering with Eevee...")
bpy.ops.render.render(write_still=True)
print("Render completed and saved!")
"""

if __name__ == "__main__":
    print("Executing Eevee render...")
    res = send_command("execute_code", {"code": code})
    print(res.get("result", {}).get("stdout", ""))
    print(res.get("result", {}).get("stderr", ""))
