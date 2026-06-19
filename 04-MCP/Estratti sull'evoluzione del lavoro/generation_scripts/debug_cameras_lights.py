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
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
    except Exception as e:
        print(f"Failed: {e}")
        sys.exit(1)

    try:
        debug_code = """import bpy
print("--- ACTIVE CAMERA ---")
cam = bpy.context.scene.camera
if cam:
    print(f"Name: {cam.name}, Location: {cam.location}, Rotation: {cam.rotation_euler}")
else:
    print("NO ACTIVE CAMERA!")

print("--- ALL CAMERAS ---")
for c in [o for o in bpy.context.scene.objects if o.type == 'CAMERA']:
    print(f"Cam: {c.name}, Location: {c.location}")

print("--- ALL LIGHTS ---")
for l in [o for o in bpy.context.scene.objects if o.type == 'LIGHT']:
    print(f"Light: {l.name}, Type: {l.data.type}, Energy: {l.data.energy}, Color: {l.data.color[:]}")
"""
        res = send_command(sock, "execute_code", {"code": debug_code})
        print(res.get('result'))
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
