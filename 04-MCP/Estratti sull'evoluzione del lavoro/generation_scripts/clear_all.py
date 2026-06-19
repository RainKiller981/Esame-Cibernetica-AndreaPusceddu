import socket
import json
import sys
import os

def receive_full_response(sock, buffer_size=8192):
    chunks = []
    sock.settimeout(10.0)
    while True:
        try:
            chunk = sock.recv(buffer_size)
            if not chunk:
                break
            chunks.append(chunk)
            try:
                data = b''.join(chunks)
                json.loads(data.decode('utf-8'))
                return data
            except json.JSONDecodeError:
                continue
        except Exception as e:
            break
    if chunks:
        return b''.join(chunks)
    return b''

def send_command(sock, command_type, params=None):
    command = {
        "type": command_type,
        "params": params or {}
    }
    sock.sendall(json.dumps(command).encode('utf-8'))
    response_data = receive_full_response(sock)
    try:
        response = json.loads(response_data.decode('utf-8'))
        return response.get("result", {})
    except Exception:
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
        clear_code = """import bpy

# Thorough cleanup of everything in Blender
for obj in list(bpy.data.objects): 
    bpy.data.objects.remove(obj, do_unlink=True)
for mesh in list(bpy.data.meshes): 
    bpy.data.meshes.remove(mesh, do_unlink=True)
for mat in list(bpy.data.materials): 
    bpy.data.materials.remove(mat, do_unlink=True)
for node_group in list(bpy.data.node_groups): 
    bpy.data.node_groups.remove(node_group, do_unlink=True)
for light in list(bpy.data.lights):
    bpy.data.lights.remove(light, do_unlink=True)
for cam in list(bpy.data.cameras):
    bpy.data.cameras.remove(cam, do_unlink=True)
for coll in list(bpy.data.collections):
    if coll.name != "Collection":
        bpy.data.collections.remove(coll)

print("All elements cleared successfully.")
"""
        res = send_command(sock, "execute_code", {"code": clear_code})
        print("Scene cleared.")
        
        # Take a screenshot of the empty viewport
        target_dir = r"C:\Users\andre\Desktop\Nuova cartella (5)"
        if not os.path.exists(target_dir):
            target_dir = r"C:\Users\andre\OneDrive\Desktop\Nuova cartella (5)"
            os.makedirs(target_dir, exist_ok=True)
            
        screenshot_path = os.path.join(target_dir, "geonodes_test.png")
        send_command(sock, "get_viewport_screenshot", {
            "max_size": 1024,
            "filepath": screenshot_path,
            "format": "png"
        })
        print("Empty screenshot taken.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
