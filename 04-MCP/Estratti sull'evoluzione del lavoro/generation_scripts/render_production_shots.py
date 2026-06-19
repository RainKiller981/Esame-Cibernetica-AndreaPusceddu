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
        print("Executing professional production render script...")
        render_code = """import bpy

scene = bpy.context.scene

# Set resolution (Full HD 1920x1080)
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100

# Try to enable Ambient Occlusion, Bloom, and Screen Space Reflections safely
try:
    if hasattr(scene, "eevee"):
        # Blender 3.x - 4.1 Eevee properties
        if hasattr(scene.eevee, "use_gtao"): scene.eevee.use_gtao = True
        if hasattr(scene.eevee, "use_bloom"): scene.eevee.use_bloom = True
        if hasattr(scene.eevee, "use_ssr"): scene.eevee.use_ssr = True
        if hasattr(scene.eevee, "use_ssr_refraction"): scene.eevee.use_ssr_refraction = True
except Exception as e:
    print(f"Skipping advanced Eevee setup: {e}")

shots = [
    {
        "camera_name": "Camera_Claustrophobia",
        "filepath": r"C:\\Users\\andre\\Desktop\\nostromo_shot_1_claustrophobia.png"
    },
    {
        "camera_name": "Camera_Overhead",
        "filepath": r"C:\\Users\\andre\\Desktop\\nostromo_shot_2_overhead.png"
    },
    {
        "camera_name": "Camera_CloseUp",
        "filepath": r"C:\\Users\\andre\\Desktop\\nostromo_shot_3_close_up.png"
    }
]

for shot in shots:
    cam = bpy.data.objects.get(shot["camera_name"])
    if cam:
        scene.camera = cam
        scene.render.filepath = shot["filepath"]
        print(f"Rendering {shot['camera_name']}...")
        bpy.ops.render.render(write_still=True)
        print("Render complete!")
    else:
        print(f"Error: Camera {shot['camera_name']} not found!")

# Restore default active camera
default_cam = bpy.data.objects.get("Camera_Claustrophobia")
if default_cam:
    scene.camera = default_cam
"""
        res = send_command(sock, "execute_code", {"code": render_code})
        print(f"Render script execution result: {res}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()
        print("Socket closed.")

if __name__ == "__main__":
    main()
