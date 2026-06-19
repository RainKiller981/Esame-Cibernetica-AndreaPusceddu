import socket
import json
import sys
import time

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
        # Step 1: Clean up Egg and Sack
        print("Cleaning up unnecessary assets (Alien Egg)...")
        cleanup_code = """import bpy
print("Deleting egg assets...")
# Remove Alien Egg and Egg Inner Sack
for obj_name in ["Alien_Egg", "Egg_Inner_Sack"]:
    obj = bpy.data.objects.get(obj_name)
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)
"""
        res = send_command(sock, "execute_code", {"code": cleanup_code})
        print(f"Cleanup result: {res}")

        # Define the three shots
        shots = [
            {
                "name": "Shot 1: Claustrophobia (Fuga nel Corridoio)",
                "filepath": r"C:\Users\andre\Desktop\nostromo_shot_1_claustrophobia.png",
                "code": """import bpy
import math

xeno = next((o for o in bpy.context.scene.objects if o.name.startswith("Sketchfab_model")), None)
if xeno:
    xeno.location = (0.05, 2.0, -0.65)
    xeno.rotation_euler = (0, 0, math.radians(180)) # Facing camera

camera = bpy.data.objects.get("Xeno_Camera")
if camera:
    camera.location = (0.0, -2.6, 0.4)
    camera.rotation_euler = (math.radians(82), 0, math.radians(180))
"""
            },
            {
                "name": "Shot 2: Overhead (La Minaccia dall'Alto)",
                "filepath": r"C:\Users\andre\Desktop\nostromo_shot_2_overhead.png",
                "code": """import bpy
import math

xeno = next((o for o in bpy.context.scene.objects if o.name.startswith("Sketchfab_model")), None)
if xeno:
    xeno.location = (0.35, 1.2, -0.65)
    xeno.rotation_euler = (0, 0, math.radians(135))

camera = bpy.data.objects.get("Xeno_Camera")
if camera:
    camera.location = (-0.95, -1.2, 1.55)
    camera.rotation_euler = (math.radians(48), 0, math.radians(130))
"""
            },
            {
                "name": "Shot 3: Close Up (Le Fauci della Morte)",
                "filepath": r"C:\Users\andre\Desktop\nostromo_shot_3_close_up.png",
                "code": """import bpy
import math

xeno = next((o for o in bpy.context.scene.objects if o.name.startswith("Sketchfab_model")), None)
if xeno:
    xeno.location = (0.0, 0.52, -0.65)
    xeno.rotation_euler = (0, 0, math.radians(180))

camera = bpy.data.objects.get("Xeno_Camera")
if camera:
    camera.location = (0.13, -0.58, 0.86)
    camera.rotation_euler = (math.radians(75), 0, math.radians(165))
"""
            }
        ]

        for i, shot in enumerate(shots):
            print(f"\nSetting up {shot['name']}...")
            res_code = send_command(sock, "execute_code", {"code": shot['code']})
            print(f"Setup result: {res_code}")
            
            # Wait a split second for viewport updates
            time.sleep(0.5)
            
            print(f"Capturing screenshot to {shot['filepath']}...")
            res_ss = send_command(sock, "get_viewport_screenshot", {
                "max_size": 1024,
                "filepath": shot['filepath'],
                "format": "png"
            })
            print(f"Screenshot result: {res_ss}")

        # Revert camera to Shot 1 framing for convenience
        print("\nReverting viewport to primary shot...")
        send_command(sock, "execute_code", {"code": shots[0]['code']})

    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()
        print("Socket closed.")

if __name__ == "__main__":
    main()
