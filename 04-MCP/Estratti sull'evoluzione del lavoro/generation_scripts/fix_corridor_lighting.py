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
        print("Fixing lights and rendering photorealistic shots...")
        blender_code = """import bpy
import math

print("Rebuilding lights with high-contrast dual-row layout...")

# 1. Delete all existing lights to avoid duplicates
bpy.ops.object.select_all(action='DESELECT')
for obj in list(bpy.context.scene.objects):
    if obj.type == 'LIGHT':
        bpy.data.objects.remove(obj, do_unlink=True)

# 2. Add Left Row of Ceiling Lights (Industrial warm yellow/orange)
# Placed at X=-0.9 (outside the ceiling duct) and Z=1.35 (below the bulkheads)
left_positions = [-1.0, 1.0, 3.0]
for idx, y in enumerate(left_positions):
    light_data = bpy.data.lights.new(name=f"Nostromo_Light_L_{idx}", type='POINT')
    light_data.energy = 1500
    light_data.color = (1.0, 0.55, 0.15) # Warm halogen amber
    light_obj = bpy.data.objects.new(name=f"Nostromo_Light_L_{idx}", object_data=light_data)
    bpy.context.collection.objects.link(light_obj)
    light_obj.location = (-0.95, y, 1.35)

# 3. Add Right Row of Ceiling Lights (Industrial sci-fi cyan/blue)
# Placed at X=0.9 and Z=1.35
right_positions = [-1.0, 1.0, 3.0]
for idx, y in enumerate(right_positions):
    light_data = bpy.data.lights.new(name=f"Nostromo_Light_R_{idx}", type='POINT')
    light_data.energy = 1500
    light_data.color = (0.1, 0.45, 1.0) # Cool neon cyan/blue
    light_obj = bpy.data.objects.new(name=f"Nostromo_Light_R_{idx}", object_data=light_data)
    bpy.context.collection.objects.link(light_obj)
    light_obj.location = (0.95, y, 1.35)

# 4. Add Emergency Red Beacon Light at the far end of the corridor
light_emerg_data = bpy.data.lights.new(name="Nostromo_EmergencyBeacon", type='POINT')
light_emerg_data.energy = 2500
light_emerg_data.color = (1.0, 0.05, 0.0) # Intense emergency red
light_emerg_obj = bpy.data.objects.new(name="Nostromo_EmergencyBeacon", object_data=light_emerg_data)
bpy.context.collection.objects.link(light_emerg_obj)
light_emerg_obj.location = (0.0, 4.2, 1.2)

# 5. Add Floor Up-Light (soft magenta) right near the Xenomorph to highlight it
light_up_data = bpy.data.lights.new(name="Nostromo_Xeno_Highlight", type='POINT')
light_up_data.energy = 800
light_up_data.color = (0.7, 0.1, 0.9) # Deep sci-fi purple
light_up_obj = bpy.data.objects.new(name="Nostromo_Xeno_Highlight", object_data=light_up_data)
bpy.context.collection.objects.link(light_up_obj)
light_up_obj.location = (0.12, 1.35, -0.6)

# 6. Configure World lighting (set background strength to 0.02 for high contrast)
if bpy.context.scene.world:
    bpy.context.scene.world.use_nodes = True
    nodes = bpy.context.scene.world.node_tree.nodes
    bg_node = nodes.get("Background")
    if bg_node:
        bg_node.inputs['Strength'].default_value = 0.02
        bg_node.inputs['Color'].default_value = (0.05, 0.05, 0.06, 1.0)

print("Lighting rebuild complete! Starting professional render...")

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100

# Perform render for the 3 shots
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
        print(f"Rendering {shot['camera_name']} to {shot['filepath']}...")
        bpy.ops.render.render(write_still=True)
        print("Render complete!")
    else:
        print(f"Error: Camera {shot['camera_name']} not found!")

# Restore Camera_Claustrophobia
default_cam = bpy.data.objects.get("Camera_Claustrophobia")
if default_cam:
    scene.camera = default_cam
"""
        res = send_command(sock, "execute_code", {"code": blender_code})
        print(f"Render script result: {res.get('result')}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
