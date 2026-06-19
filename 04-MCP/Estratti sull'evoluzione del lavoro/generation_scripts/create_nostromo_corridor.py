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
        blender_code = """import bpy
import math

print("Generating Nostromo spaceship corridor...")

# 1. Materials for the spaceship
# Dark steel panel
mat_steel = bpy.data.materials.new(name="Nostromo_Steel")
mat_steel.use_nodes = True
nodes_steel = mat_steel.node_tree.nodes
p_steel = nodes_steel.get("Principled BSDF")
p_steel.inputs['Base Color'].default_value = (0.04, 0.04, 0.05, 1.0)
p_steel.inputs['Metallic'].default_value = 0.85
p_steel.inputs['Roughness'].default_value = 0.4

# Copper Pipes
mat_copper = bpy.data.materials.new(name="Nostromo_Copper")
mat_copper.use_nodes = True
nodes_copper = mat_copper.node_tree.nodes
p_copper = nodes_copper.get("Principled BSDF")
p_copper.inputs['Base Color'].default_value = (0.58, 0.28, 0.15, 1.0)
p_copper.inputs['Metallic'].default_value = 0.95
p_copper.inputs['Roughness'].default_value = 0.22

# Glowing Warning Light (Amber/Orange)
mat_warn = bpy.data.materials.new(name="Nostromo_WarningLight")
mat_warn.use_nodes = True
nodes_warn = mat_warn.node_tree.nodes
p_warn = nodes_warn.get("Principled BSDF")
# Support both old Principled and new Emission slots
if 'Emission' in p_warn.inputs:
    p_warn.inputs['Emission'].default_value = (1.0, 0.4, 0.02, 1.0)
if 'Emission Strength' in p_warn.inputs:
    p_warn.inputs['Emission Strength'].default_value = 4.0

# 2. Build the structural bulkheads (octagonal arches) every 2 meters
# Corridor bounds: X = [-1.5, 1.5], Z = [-0.65, 1.85], Y = [-3.0, 5.0]
arch_positions = [-2.0, 0.0, 2.0, 4.0]

for y in arch_positions:
    # Left Pillar
    bpy.ops.mesh.primitive_cube_add(location=(-1.45, y, 0.6), scale=(0.1, 0.2, 1.25))
    pillar_l = bpy.context.active_object
    pillar_l.name = f"Nostromo_Pillar_L_{y}"
    pillar_l.data.materials.append(mat_steel)
    
    # Right Pillar
    bpy.ops.mesh.primitive_cube_add(location=(1.45, y, 0.6), scale=(0.1, 0.2, 1.25))
    pillar_r = bpy.context.active_object
    pillar_r.name = f"Nostromo_Pillar_R_{y}"
    pillar_r.data.materials.append(mat_steel)
    
    # Ceiling Beam
    bpy.ops.mesh.primitive_cube_add(location=(0, y, 1.8), scale=(1.5, 0.25, 0.08))
    ceiling_beam = bpy.context.active_object
    ceiling_beam.name = f"Nostromo_Beam_Ceiling_{y}"
    ceiling_beam.data.materials.append(mat_steel)
    
    # Angled Corners (Bulkhead silhouette)
    # Left Angled Corner
    bpy.ops.mesh.primitive_cube_add(location=(-1.1, y, 1.5), scale=(0.08, 0.2, 0.4))
    corner_l = bpy.context.active_object
    corner_l.name = f"Nostromo_Corner_L_{y}"
    corner_l.rotation_euler = (0, math.radians(-45), 0)
    corner_l.data.materials.append(mat_steel)
    
    # Right Angled Corner
    bpy.ops.mesh.primitive_cube_add(location=(1.1, y, 1.5), scale=(0.08, 0.2, 0.4))
    corner_r = bpy.context.active_object
    corner_r.name = f"Nostromo_Corner_R_{y}"
    corner_r.rotation_euler = (0, math.radians(45), 0)
    corner_r.data.materials.append(mat_steel)

# 3. Build Wall Panels (Left and Right)
# Thin metal panels running between the bulkheads
for y_pos in [-1.0, 1.0, 3.0]:
    # Left Wall Panels
    bpy.ops.mesh.primitive_cube_add(location=(-1.5, y_pos, 0.6), scale=(0.02, 0.8, 1.2))
    wpanel_l = bpy.context.active_object
    wpanel_l.name = f"Nostromo_WallPanel_L_{y_pos}"
    wpanel_l.data.materials.append(mat_steel)
    
    # Right Wall Panels
    bpy.ops.mesh.primitive_cube_add(location=(1.5, y_pos, 0.6), scale=(0.02, 0.8, 1.2))
    wpanel_r = bpy.context.active_object
    wpanel_r.name = f"Nostromo_WallPanel_R_{y_pos}"
    wpanel_r.data.materials.append(mat_steel)
    
    # Add decorative electrical boxes on the wall panels
    bpy.ops.mesh.primitive_cube_add(location=(-1.47, y_pos - 0.2, 0.8), scale=(0.03, 0.15, 0.2))
    ebox_l = bpy.context.active_object
    ebox_l.data.materials.append(mat_steel)
    # small blinking indicators
    bpy.ops.mesh.primitive_cube_add(location=(-1.44, y_pos - 0.2, 0.85), scale=(0.01, 0.03, 0.03))
    ind_l = bpy.context.active_object
    ind_l.data.materials.append(mat_warn)

# 4. Build Industrial Pipes (exposed conduits running along the walls)
for side in [-1.4, 1.4]:
    # Running horizontally along the walls
    for z_pos in [0.2, 0.8, 1.3]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=8.0, location=(side, 1.0, z_pos))
        pipe = bpy.context.active_object
        pipe.name = f"Nostromo_Pipe_{side}_{z_pos}"
        pipe.rotation_euler = (math.radians(90), 0, 0)
        # Alternate materials
        if z_pos == 0.8:
            pipe.data.materials.append(mat_copper)
        else:
            pipe.data.materials.append(mat_steel)
        bpy.ops.object.shade_smooth()

# 5. Build Ceiling Ducts
# A heavy ventilation duct down the center of the ceiling
bpy.ops.mesh.primitive_cube_add(location=(0, 1.0, 1.8), scale=(0.4, 4.0, 0.12))
duct = bpy.context.active_object
duct.name = "Nostromo_CeilingDuct"
duct.data.materials.append(mat_steel)

# 6. Build Floor Grates / Plate
bpy.ops.mesh.primitive_cube_add(location=(0, 1.0, -0.66), scale=(1.5, 4.0, 0.01))
floor_plate = bpy.context.active_object
floor_plate.name = "Nostromo_FloorPlate"
floor_plate.data.materials.append(mat_steel)

# 7. Move the photorealistic Xenomorph into the corridor
# Sneaking forward, close to the right bulkhead, looking at the camera
xeno_root = None
for obj in bpy.context.scene.objects:
    if obj.name.startswith("Sketchfab_model"):
        xeno_root = obj
        break

if xeno_root:
    print(f"Repositioning Xenomorph {xeno_root.name} inside Nostromo corridor...")
    # Position sneaking along the right wall (X=0.45, Y=1.8, Z=-0.65)
    xeno_root.location = (0.45, 1.8, -0.65)
    # Face slightly left and forward (towards the camera and egg)
    xeno_root.rotation_euler = (0, 0, math.radians(160))

# 8. Move the Alien Egg inside the corridor
# Nestled in a dark corner on the left
egg = bpy.data.objects.get("Alien_Egg")
if egg:
    print("Repositioning Alien Egg inside Nostromo corridor...")
    egg.location = (-0.6, 2.4, -0.6)
    
egg_sack = bpy.data.objects.get("Egg_Inner_Sack")
if egg_sack:
    egg_sack.location = (-0.6, 2.4, -0.73)

# 9. Set Up Claustrophobic Nostromo Lighting
# Clear old lighting to make room for industrial atmospheric lights
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.select_by_type(type='LIGHT')
bpy.ops.object.delete()

# Ceiling overhead lights (Dim, industrial cool yellow/green casting down pools of light)
light_positions = [-1.0, 1.0, 3.0]
for idx, y_light in enumerate(light_positions):
    light_data = bpy.data.lights.new(name=f"Nostromo_CeilingLight_{idx}", type='POINT')
    light_data.energy = 450
    light_data.color = (0.85, 0.65, 0.45) # Industrial warm/yellow
    light_obj = bpy.data.objects.new(name=f"Nostromo_CeilingLight_{idx}", object_data=light_data)
    bpy.context.collection.objects.link(light_obj)
    light_obj.location = (0.0, y_light, 1.6)

# Creepy flashing warning light (amber) at the end of the corridor
light_warn_data = bpy.data.lights.new(name="Nostromo_EmergencyLight", type='POINT')
light_warn_data.energy = 800
light_warn_data.color = (1.0, 0.22, 0.0) # Intensely warning red/orange
light_warn_obj = bpy.data.objects.new(name="Nostromo_EmergencyLight", object_data=light_warn_data)
bpy.context.collection.objects.link(light_warn_obj)
light_warn_obj.location = (-1.3, 3.5, 0.8)

# Cool blue backlight to catch the slimy reflections on the Xenomorph's crest
light_rim_data = bpy.data.lights.new(name="Nostromo_RimLight", type='POINT')
light_rim_data.energy = 900
light_rim_data.color = (0.1, 0.5, 1.0) # Deep aquatic blue
light_rim_obj = bpy.data.objects.new(name="Nostromo_RimLight", object_data=light_rim_data)
bpy.context.collection.objects.link(light_rim_obj)
light_rim_obj.location = (0.45, 0.5, 0.5)

# 10. Position Camera Down the Corridor (Terrifying claustrophobic perspective)
camera = bpy.data.objects.get("Xeno_Camera")
if camera:
    camera.location = (0.0, -2.6, 0.4)
    # Point straight down the long, spooky corridor
    camera.rotation_euler = (math.radians(82), 0, math.radians(180))
    print("Nostromo corridor camera framing configured.")

print("Nostromo spaceship corridor generation succeeded!")
"""
        
        print("Executing Nostromo spaceship corridor generator...")
        res = send_command(sock, "execute_code", {"code": blender_code})
        print(f"Execute result: {res}")
        
        # 11. Capture viewport screenshot
        print("Capturing viewport screenshot...")
        screenshot_path = r"C:\Users\andre\Desktop\nostromo_scene.png"
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
