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
        print("Creating three physical camera objects in Blender...")
        blender_code = """import bpy
import math

# 1. Delete all existing camera objects to start clean
bpy.ops.object.select_all(action='DESELECT')
for obj in list(bpy.context.scene.objects):
    if obj.type == 'CAMERA':
        bpy.data.objects.remove(obj, do_unlink=True)

# 2. Position the photorealistic Xenomorph in a perfect static pose for all shots
xeno = next((o for o in bpy.context.scene.objects if o.name.startswith("Sketchfab_model")), None)
if xeno:
    xeno.location = (0.12, 1.35, -0.65)
    xeno.rotation_euler = (0, 0, math.radians(165)) # Menacing angled pose

# 3. Create Camera 1: Claustrophobia (Fuga nel Corridoio)
cam1_data = bpy.data.cameras.new(name="Camera_Claustrophobia")
cam1_obj = bpy.data.objects.new(name="Camera_Claustrophobia", object_data=cam1_data)
bpy.context.collection.objects.link(cam1_obj)
cam1_obj.location = (0.0, -2.6, 0.4)
cam1_obj.rotation_euler = (math.radians(82), 0, math.radians(180))

# 4. Create Camera 2: Overhead (La Minaccia dall'Alto)
cam2_data = bpy.data.cameras.new(name="Camera_Overhead")
cam2_obj = bpy.data.objects.new(name="Camera_Overhead", object_data=cam2_data)
bpy.context.collection.objects.link(cam2_obj)
cam2_obj.location = (-0.95, -1.2, 1.55)
cam2_obj.rotation_euler = (math.radians(48), 0, math.radians(130))

# 5. Create Camera 3: Close Up (Le Fauci della Morte)
cam3_data = bpy.data.cameras.new(name="Camera_CloseUp")
cam3_obj = bpy.data.objects.new(name="Camera_CloseUp", object_data=cam3_data)
bpy.context.collection.objects.link(cam3_obj)
cam3_obj.location = (0.28, -0.22, 0.78) # Perfectly close to the head
cam3_obj.rotation_euler = (math.radians(72), 0, math.radians(150))

print("Physical cameras created successfully!")
"""
        res = send_command(sock, "execute_code", {"code": blender_code})
        print(f"Cameras creation result: {res}")

        # List of screenshots to take sequentially by setting the active camera
        shots = [
            {
                "camera_name": "Camera_Claustrophobia",
                "name": "Shot 1: Claustrophobia (Fuga nel Corridoio)",
                "filepath": r"C:\Users\andre\Desktop\nostromo_shot_1_claustrophobia.png"
            },
            {
                "camera_name": "Camera_Overhead",
                "name": "Shot 2: Overhead (La Minaccia dall'Alto)",
                "filepath": r"C:\Users\andre\Desktop\nostromo_shot_2_overhead.png"
            },
            {
                "camera_name": "Camera_CloseUp",
                "name": "Shot 3: Close Up (Le Fauci della Morte)",
                "filepath": r"C:\Users\andre\Desktop\nostromo_shot_3_close_up.png"
            }
        ]

        for shot in shots:
            print(f"\nSetting active camera to {shot['camera_name']}...")
            set_cam_code = f"""import bpy
cam = bpy.data.objects.get("{shot['camera_name']}")
if cam:
    bpy.context.scene.camera = cam
    print("Active camera set to: " + cam.name)
"""
            res_cam = send_command(sock, "execute_code", {"code": set_cam_code})
            print(f"Result: {res_cam}")
            
            # Wait for Blender to update the viewport
            time.sleep(0.8)
            
            print(f"Capturing screenshot to {shot['filepath']}...")
            res_ss = send_command(sock, "get_viewport_screenshot", {
                "max_size": 1024,
                "filepath": shot['filepath'],
                "format": "png"
            })
            print(f"Screenshot result: {res_ss}")

        # Set default active camera to Camera_Claustrophobia at the end
        print("\nSetting default viewport camera to Camera_Claustrophobia...")
        default_cam_code = """import bpy
cam = bpy.data.objects.get("Camera_Claustrophobia")
if cam:
    bpy.context.scene.camera = cam
"""
        send_command(sock, "execute_code", {"code": default_cam_code})
        print("Default camera restored.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()
        print("Socket closed.")

if __name__ == "__main__":
    main()
