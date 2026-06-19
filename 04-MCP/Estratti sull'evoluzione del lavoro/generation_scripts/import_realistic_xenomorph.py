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
        # Construct the complete procedural code
        blender_code = """import bpy
import math

print("Starting realistic Xenomorph import...")

# 1. Clear previous procedurally generated Xenomorph objects
xeno_prefixes = ["Xeno_Head", "Xeno_Jaw", "Xeno_Torso", "Xeno_Rib", "Xeno_Tube", "Xeno_Tail", "Xeno_Thigh", "Xeno_Calf", "Xeno_Foot", "Xeno_UArm", "Xeno_FArm", "Xeno_Hand", "thigh_l", "calf_l", "foot_l", "thigh_r", "calf_r", "foot_r", "uarm_l", "farm_l", "hand_l", "uarm_r", "farm_r", "hand_r"]

for obj in list(bpy.context.scene.objects):
    should_delete = False
    # Check if object name matches any of our procedurally created mesh parts
    for prefix in xeno_prefixes:
        if obj.name.startswith(prefix):
            should_delete = True
            break
    if should_delete:
        bpy.data.objects.remove(obj, do_unlink=True)

# 2. Deselect all before import
bpy.ops.object.select_all(action='DESELECT')

# 3. Import the photorealistic xenomorph.glb from Downloads
glb_path = r"C:\\Users\\andre\\Downloads\\xenomorph.glb"
bpy.ops.import_scene.gltf(filepath=glb_path)

# 4. Process imported objects
imported_objs = list(bpy.context.selected_objects)
print(f"Imported {len(imported_objs)} objects.")

# Find root object or meshes to scale and place
root_obj = None
for obj in imported_objs:
    if obj.parent is None:
        root_obj = obj
        break

if root_obj is None and imported_objs:
    root_obj = imported_objs[0]

if root_obj:
    print(f"Setting position and scale for root object: {root_obj.name}")
    # Place it at the origin, but slightly lowered so it stands on the ground (-0.65)
    root_obj.location = (0, 0, -0.65)
    
    # Check current scale. Let's make sure it fits a reasonable scale.
    # If the model is huge or tiny, let's normalize it.
    # First, calculate bounding box of all meshes
    meshes = [o for o in imported_objs if o.type == 'MESH']
    if meshes:
        min_z = min((o.matrix_world @ v.co).z for o in meshes for v in o.data.vertices)
        max_z = max((o.matrix_world @ v.co).z for o in meshes for v in o.data.vertices)
        height = max_z - min_z
        print(f"Current height of model: {height:.2f} meters")
        
        # We want the Xenomorph height to be around 2.2 meters
        target_height = 2.2
        if height > 0:
            scale_factor = target_height / height
            root_obj.scale = root_obj.scale * scale_factor
            print(f"Rescaled model by factor {scale_factor:.4f} to reach height of 2.2m")
            
            # Recalculate and place base exactly on ground (Z = -0.65)
            # Z location adjust
            min_z = min((o.matrix_world @ v.co).z for o in meshes for v in o.data.vertices)
            root_obj.location.z = root_obj.location.z + (-0.65 - min_z)
            print(f"Adjusted Z base to -0.65")
            
    # Rotate the Xenomorph so it faces towards the egg
    # Egg is at (-0.8, -0.3, -0.6), Xenomorph is around (0, 0, -0.65)
    # We want it to rotate on Z axis to look at the egg.
    dx = -0.8 - root_obj.location.x
    dy = -0.3 - root_obj.location.y
    angle_z = math.atan2(dy, dx)
    
    # We rotate by angle_z. Depending on the model's default orientation, we might need a 90 deg offset.
    # Typically GLTF models face -Y or +Y, let's rotate it to look towards the egg.
    root_obj.rotation_euler = (0, 0, angle_z - math.radians(90))

# 5. Make sure the materials are glossy and biomechanical
# Let's inspect materials of imported meshes and enhance them for high photorealism.
for obj in imported_objs:
    if obj.type == 'MESH':
        for slot in obj.material_slots:
            if slot.material:
                mat = slot.material
                mat.use_nodes = True
                nodes = mat.node_tree.nodes
                principled = nodes.get("Principled BSDF")
                if principled:
                    # Give it a wet, slimy sheen
                    principled.inputs['Roughness'].default_value = 0.12
                    principled.inputs['Metallic'].default_value = 0.8
                    if 'Specular' in principled.inputs:
                        principled.inputs['Specular'].default_value = 0.9
                    print(f"Refined material '{mat.name}' roughness to 0.12 and metallic to 0.8")

# 6. Re-track camera to focus on the midpoint between Xenomorph and Egg
camera = bpy.data.objects.get("Xeno_Camera")
if camera:
    # Update camera location to frame the photorealistic model beautifully
    camera.location = (2.2, 3.8, 1.4)
    print("Camera positioned for optimal photorealistic framing.")

print("Realistic Xenomorph import and shading complete!")
"""
        
        print("Executing realistic Xenomorph importer...")
        res = send_command(sock, "execute_code", {"code": blender_code})
        print(f"Execute result: {res}")
        
        # 11. Capture viewport screenshot
        print("Capturing viewport screenshot...")
        screenshot_path = r"C:\Users\andre\Desktop\xenomorph_and_egg.png"
        screenshot_result = send_command(sock, "get_viewport_screenshot", {
            "max_size": 1024,
            "filepath": screenshot_path,
            "format": "png"
        })
        print(f"Screenshot complete! Saved to {screenshot_path}.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()
        print("Socket closed.")

if __name__ == "__main__":
    main()
