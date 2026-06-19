import socket
import json
import sys

def receive_full_response(sock, buffer_size=8192):
    chunks = []
    sock.settimeout(180.0)
    while True:
        try:
            chunk = sock.recv(buffer_size)
            if not chunk:
                if not chunks:
                    raise Exception("Connection closed before receiving any data")
                break
            chunks.append(chunk)
            try:
                data = b''.join(chunks)
                json.loads(data.decode('utf-8'))
                return data
            except json.JSONDecodeError:
                continue
        except socket.timeout:
            print("Socket timeout during receive")
            break
        except Exception as e:
            print(f"Error during receive: {e}")
            raise
    if chunks:
        data = b''.join(chunks)
        try:
            json.loads(data.decode('utf-8'))
            return data
        except json.JSONDecodeError:
            raise Exception("Incomplete JSON response received")
    else:
        raise Exception("No data received")

def send_command(sock, command_type, params=None):
    command = {
        "type": command_type,
        "params": params or {}
    }
    sock.sendall(json.dumps(command).encode('utf-8'))
    response_data = receive_full_response(sock)
    response = json.loads(response_data.decode('utf-8'))
    if response.get("status") == "error":
        raise Exception(response.get("message", "Unknown error from Blender"))
    return response.get("result", {})

def main():
    host = "localhost"
    port = 9876
    print(f"Connecting to Blender...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
        print("Connected!")
    except Exception as e:
        print(f"Failed to connect to Blender: {e}")
        sys.exit(1)

    try:
        print("Debugging scene in Blender...")
        debug_code = """import bpy

print("--- ACTIVE CAMERA ---")
if bpy.context.scene.camera:
    cam = bpy.context.scene.camera
    print(f"Active Camera Name: {cam.name}")
    print(f"Camera Location: {cam.location}")
    print(f"Camera Rotation (Euler): {cam.rotation_euler}")
else:
    print("NO ACTIVE CAMERA!")

print("\\n--- ALL LIGHTS ---")
lights = [o for o in bpy.context.scene.objects if o.type == 'LIGHT']
if lights:
    for l in lights:
        print(f"Light: {l.name}, Type: {l.data.type}, Energy: {l.data.energy}, Color: {l.data.color[:]}, Location: {l.location}")
else:
    print("NO LIGHTS FOUND!")

print("\\n--- OBJECTS BETWEEN CAMERA AND XENOMORPH ---")
# Camera is around Y = -2.6, Xeno is around Y = 1.35
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        loc = obj.location
        if abs(loc.x) < 0.5 and -3.0 < loc.y < 3.0:
            print(f"Mesh: {obj.name}, Location: {loc}, Scale: {obj.scale}")

print("\\n--- ALL MESH OBJECTS ---")
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        print(f"Mesh: {obj.name}, Parent: {obj.parent.name if obj.parent else 'None'}, Location: {obj.location}, Scale: {obj.scale}, Hide Render: {obj.hide_render}")
"""
        res = send_command(sock, "execute_code", {"code": debug_code})
        print(f"Debug result: {res.get('result')}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
