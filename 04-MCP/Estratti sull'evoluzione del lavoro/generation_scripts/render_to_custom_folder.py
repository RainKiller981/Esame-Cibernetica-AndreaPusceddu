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
    # 1. Resolve and create the destination directory
    target_dir = r"C:\Users\andre\Desktop\Nuova cartella (5)"
    
    # Check if target_dir actually exists or if it's a OneDrive path
    onedrive_dir = r"C:\Users\andre\OneDrive\Desktop\Nuova cartella (5)"
    
    if not os.path.exists(target_dir):
        if os.path.exists(r"C:\Users\andre\OneDrive\Desktop"):
            target_dir = onedrive_dir
            print(f"Target directory resolved to OneDrive: {target_dir}")
        else:
            print(f"Creating directory: {target_dir}")
            try:
                os.makedirs(target_dir, exist_ok=True)
            except Exception as e:
                print(f"Failed to create desktop directory: {e}")
                # Fallback to OneDrive
                target_dir = onedrive_dir
                os.makedirs(target_dir, exist_ok=True)
    else:
        print(f"Target directory exists: {target_dir}")

    # Set up render paths
    shot_paths = {
        "Camera_Claustrophobia": os.path.join(target_dir, "nostromo_shot_1_claustrophobia.png"),
        "Camera_Overhead": os.path.join(target_dir, "nostromo_shot_2_overhead.png"),
        "Camera_CloseUp": os.path.join(target_dir, "nostromo_shot_3_close_up.png")
    }

    # 2. Connect to Blender
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
        print("Starting Eevee Renders in Blender...")
        
        # We pass double backslashes for the windows paths in Blender Python
        render_code = f"""import bpy

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100

# Safely enable Eevee features
try:
    if hasattr(scene, "eevee"):
        if hasattr(scene.eevee, "use_gtao"): scene.eevee.use_gtao = True
        if hasattr(scene.eevee, "use_bloom"): scene.eevee.use_bloom = True
        if hasattr(scene.eevee, "use_ssr"): scene.eevee.use_ssr = True
        if hasattr(scene.eevee, "use_ssr_refraction"): scene.eevee.use_ssr_refraction = True
except Exception as e:
    print(f"Eevee features warning: {{e}}")

# Render each camera
cams = {{
    "Camera_Claustrophobia": r"{shot_paths['Camera_Claustrophobia']}",
    "Camera_Overhead": r"{shot_paths['Camera_Overhead']}",
    "Camera_CloseUp": r"{shot_paths['Camera_CloseUp']}"
}}

for cam_name, path in cams.items():
    cam = bpy.data.objects.get(cam_name)
    if cam:
        scene.camera = cam
        scene.render.filepath = path
        print(f"Rendering {{cam_name}} to {{path}}...")
        bpy.ops.render.render(write_still=True)
        print("Render finished!")
    else:
        print(f"Error: Camera {{cam_name}} not found!")

# Reset active camera
default_cam = bpy.data.objects.get("Camera_Claustrophobia")
if default_cam:
    scene.camera = default_cam
"""
        res = send_command(sock, "execute_code", {"code": render_code})
        print(f"Render script execution result: {res.get('result')}")
        
        # 3. Copy rendered files to our main conversation's artifact folder
        artifact_dir = r"C:\Users\andre\.gemini\antigravity-cli\brain\bf0fdf96-df65-451f-a3dd-ee395072dc69"
        os.makedirs(artifact_dir, exist_ok=True)
        
        for cam_name, path in shot_paths.items():
            if os.path.exists(path):
                dest_name = os.path.basename(path)
                dest_path = os.path.join(artifact_dir, dest_name)
                print(f"Copying {path} -> {dest_path}...")
                shutil.copy(path, dest_path)
            else:
                # If target was OneDrive, check if it's there
                print(f"Rendered file not found at {path}!")
                
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        sock.close()
        print("Socket closed.")

if __name__ == "__main__":
    main()
