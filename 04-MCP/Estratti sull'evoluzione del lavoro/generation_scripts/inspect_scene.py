import socket
import json
import sys

def send_command(sock, command_type, params=None):
    command = {
        "type": command_type,
        "params": params or {}
    }
    sock.sendall(json.dumps(command).encode('utf-8'))
    
    # Receive response
    chunks = []
    sock.settimeout(10.0)
    while True:
        try:
            chunk = sock.recv(8192)
            if not chunk:
                break
            chunks.append(chunk)
            try:
                data = b''.join(chunks)
                json.loads(data.decode('utf-8'))
                return json.loads(data.decode('utf-8'))
            except json.JSONDecodeError:
                continue
        except Exception as e:
            break
    return {}

def main():
    host = "localhost"
    port = 9876
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
    except Exception as e:
        print(f"Failed to connect to Blender: {e}")
        sys.exit(1)

    try:
        inspect_code = """import bpy
import os

filepath = r"C:\\Users\\andre\\.gemini\\antigravity-cli\\brain\\bf0fdf96-df65-451f-a3dd-ee395072dc69\\scratch\\inspection_results.txt"
with open(filepath, "w") as f:
    f.write("--- SCENE INSPECTION ---\\n")
    f.write(f"Active scene: {bpy.context.scene.name}\\n")
    f.write(f"Render Engine: {bpy.context.scene.render.engine}\\n")
    f.write("Objects in scene:\\n")
    for obj in bpy.data.objects:
        f.write(f" - {obj.name} (Type: {obj.type}, Location: {obj.location})\\n")
    
    f.write("Cameras:\\n")
    for cam in bpy.data.cameras:
        f.write(f" - {cam.name}\\n")
    f.write(f"Active camera: {bpy.context.scene.camera.name if bpy.context.scene.camera else 'None'}\\n")
    
    # Check 3D viewports shading
    f.write("Viewports:\\n")
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        f.write(f" - Viewport Shading: {space.shading.type}, Clip Start: {space.clip_start}, Clip End: {space.clip_end}\\n")
"""
        res = send_command(sock, "execute_code", {"code": inspect_code})
        print(f"Command executed, status: {res.get('status')}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
