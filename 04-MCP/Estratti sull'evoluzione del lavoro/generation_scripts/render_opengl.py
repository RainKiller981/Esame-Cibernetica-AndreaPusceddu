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

# Make sure the camera is active
camera = bpy.data.objects.get("Camera")
if camera:
    bpy.context.scene.camera = camera

# Go through all windows and spaces to configure 3D view
for window in bpy.context.window_manager.windows:
    screen = window.screen
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.region_3d.view_perspective = 'CAMERA'
                    space.shading.type = 'RENDERED'
                    space.show_overlays = False
                    
# Set render settings for viewport OpenGL render
bpy.context.scene.render.filepath = r"C:\\Users\\andre\\Desktop\\xenomorph_and_egg.png"
bpy.context.scene.render.image_settings.file_format = 'PNG'

# Force update
bpy.context.view_layer.update()

# Redraw windows
bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=2)

# Perform the OpenGL render (view render)
# setting view_context=True will render the active viewport context exactly as shown!
bpy.ops.render.opengl(write_still=True, view_context=True)
print("OpenGL viewport render completed and saved to Desktop!")
"""

if __name__ == "__main__":
    print("Performing high-quality viewport render...")
    res = send_command("execute_code", {"code": code})
    print(res.get("result", {}).get("stdout", ""))
    print(res.get("result", {}).get("stderr", ""))
