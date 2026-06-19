import socket
import json
import sys
import os
import shutil

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
    target_dir = r"C:\Users\andre\Desktop\Nuova cartella (5)"
    if not os.path.exists(target_dir):
        # Fallback to OneDrive
        target_dir = r"C:\Users\andre\OneDrive\Desktop\Nuova cartella (5)"
        os.makedirs(target_dir, exist_ok=True)
        
    output_path = os.path.join(target_dir, "nostromo_hyperrealistic_cycles.png")

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
        print("Executing hyperrealistic Cycles ray-tracing script...")
        cycles_code = f"""import bpy
import math

scene = bpy.context.scene

# 1. Create a special Camera for the Hyperrealistic Shot
cam_name = "Camera_Hyperrealism"
cam = bpy.data.objects.get(cam_name)
if cam:
    bpy.data.objects.remove(cam, do_unlink=True)

cam_data = bpy.data.cameras.new(name=cam_name)
# Set focal length to 45mm for dramatic cinematic depth
cam_data.lens = 45
cam_obj = bpy.data.objects.new(name=cam_name, object_data=cam_data)
bpy.context.collection.objects.link(cam_obj)
# Close-up positioning on the Xenomorph head
cam_obj.location = (0.32, -0.15, 0.72)
cam_obj.rotation_euler = (math.radians(70), 0, math.radians(145))

# 2. Switch Render Engine to Cycles for ray-traced photorealism
scene.render.engine = 'CYCLES'

# Configure GPU rendering if available
try:
    preferences = bpy.context.preferences
    addons = preferences.addons
    cycles_addon = addons.get('cycles')
    if cycles_addon:
        cycles_preferences = cycles_addon.preferences
        cycles_preferences.compute_device_type = 'CUDA' # Try CUDA
        bpy.context.scene.cycles.device = 'GPU'
        # Refresh devices
        cycles_preferences.get_devices()
        print("Cycles configured to use GPU (CUDA)")
except Exception as e:
    print(f"GPU config skipped (falling back to CPU): {{e}}")

# Optimize Cycles samples for fast and clean rendering (64 samples with Denoise is perfect!)
scene.cycles.samples = 64
if hasattr(scene.cycles, "use_denoising"):
    scene.cycles.use_denoising = True

# Resolution (1920x1080 Full HD)
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100

# Set active camera and render path
scene.camera = cam_obj
scene.render.filepath = r"{output_path}"

print("Starting Cycles Ray-Traced Render...")
bpy.ops.render.render(write_still=True)
print("Cycles Render Complete!")

# 3. Restore interactive settings for user convenience
scene.render.engine = 'BLENDER_EEVEE'
default_cam = bpy.data.objects.get("Camera_Claustrophobia")
if default_cam:
    scene.camera = default_cam
"""
        res = send_command(sock, "execute_code", {"code": cycles_code})
        print(f"Cycles script execution result: {res.get('result')}")
        
        # 4. Copy the rendered file to the conversation's main artifact folder
        artifact_dir = r"C:\Users\andre\.gemini\antigravity-cli\brain\bf0fdf96-df65-451f-a3dd-ee395072dc69"
        dest_path = os.path.join(artifact_dir, "nostromo_hyperrealistic_cycles.png")
        if os.path.exists(output_path):
            print(f"Copying {output_path} -> {dest_path}...")
            shutil.copy(output_path, dest_path)
            print("Successfully copied!")
        else:
            print("Rendered file not found!")
            
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        sock.close()
        print("Socket closed.")

if __name__ == "__main__":
    main()
