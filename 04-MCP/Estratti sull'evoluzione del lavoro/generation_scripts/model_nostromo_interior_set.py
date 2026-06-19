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
        
    output_path = os.path.join(target_dir, "nostromo_interior_set.png")

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
        print("Modeling the USCSS Nostromo Massive Interior Film Set...")
        
        blender_code = f"""import bpy
import math

print("Clearing the space scene...")
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 1. Premium Interior Materials
# Dark Refinery Steel
mat_steel = bpy.data.materials.new(name="Nostromo_Int_Steel")
mat_steel.use_nodes = True
p_steel = mat_steel.node_tree.nodes.get("Principled BSDF")
p_steel.inputs['Base Color'].default_value = (0.04, 0.04, 0.045, 1.0)
p_steel.inputs['Metallic'].default_value = 0.85
p_steel.inputs['Roughness'].default_value = 0.42

# Retro High-Tech White Plastic (Chairs and Mess table)
mat_plastic = bpy.data.materials.new(name="Nostromo_Int_Plastic")
mat_plastic.use_nodes = True
p_plastic = mat_plastic.node_tree.nodes.get("Principled BSDF")
p_plastic.inputs['Base Color'].default_value = (0.85, 0.85, 0.82, 1.0)
p_plastic.inputs['Roughness'].default_value = 0.28

# Glossy black padding/leather
mat_leather = bpy.data.materials.new(name="Nostromo_Int_Leather")
mat_leather.use_nodes = True
p_leather = mat_leather.node_tree.nodes.get("Principled BSDF")
p_leather.inputs['Base Color'].default_value = (0.01, 0.01, 0.015, 1.0)
p_leather.inputs['Roughness'].default_value = 0.35

# Glowing CRT Screens (Green phosphor)
mat_crt = bpy.data.materials.new(name="Nostromo_Int_CRT")
mat_crt.use_nodes = True
p_crt = mat_crt.node_tree.nodes.get("Principled BSDF")
if 'Emission' in p_crt.inputs:
    p_crt.inputs['Emission'].default_value = (0.0, 1.0, 0.2, 1.0)
if 'Emission Strength' in p_crt.inputs:
    p_crt.inputs['Emission Strength'].default_value = 5.0

# 2. Floor and Back Walls (Massive Set)
# Floor plate
bpy.ops.mesh.primitive_cube_add(location=(0, 0, -0.65), scale=(8.0, 10.0, 0.02))
floor = bpy.context.active_object
floor.name = "Set_Floor"
floor.data.materials.append(mat_steel)

# Back Wall paneling
bpy.ops.mesh.primitive_cube_add(location=(0, 9.8, 1.5), scale=(8.0, 0.1, 2.2))
back_wall = bpy.context.active_object
back_wall.name = "Set_BackWall"
back_wall.data.materials.append(mat_steel)

# 3. Massive Double-Beam Support Pillars (Industrial scale)
pillar_positions = [
    (-4.5, -3.0), (-4.5, 1.0), (-4.5, 5.0),
    (4.5, -3.0), (4.5, 1.0), (4.5, 5.0)
]
for idx, (px, py) in enumerate(pillar_positions):
    # Left girder
    bpy.ops.mesh.primitive_cube_add(location=(px - 0.2, py, 1.5), scale=(0.1, 0.15, 2.2))
    g1 = bpy.context.active_object
    g1.data.materials.append(mat_steel)
    
    # Right girder
    bpy.ops.mesh.primitive_cube_add(location=(px + 0.2, py, 1.5), scale=(0.1, 0.15, 2.2))
    g2 = bpy.context.active_object
    g2.data.materials.append(mat_steel)
    
    # Cross braces
    for hz in [0.0, 1.0, 2.0, 3.0]:
        bpy.ops.mesh.primitive_cube_add(location=(px, py, hz - 0.6), scale=(0.3, 0.12, 0.04))
        brace = bpy.context.active_object
        brace.data.materials.append(mat_steel)

# 4. The Bridge / Pilot Area (Command Platform & Curved Console)
# Raised Platform
bpy.ops.mesh.primitive_cube_add(location=(0, 6.5, -0.45), scale=(3.5, 2.2, 0.2))
bridge_plat = bpy.context.active_object
bridge_plat.name = "Bridge_Platform"
bridge_plat.data.materials.append(mat_steel)

# Curved Command Console Desk
bpy.ops.mesh.primitive_cube_add(location=(0, 7.6, 0.2), scale=(2.8, 0.45, 0.5))
console_desk = bpy.context.active_object
console_desk.name = "Command_Console"
console_desk.data.materials.append(mat_steel)

# CRT Monitors embedded in console (8 glowing panels)
for i in range(8):
    x_pos = -2.1 + (i * 0.6)
    # angled monitor screen
    bpy.ops.mesh.primitive_cube_add(location=(x_pos, 7.25, 0.45), scale=(0.2, 0.02, 0.16))
    mon = bpy.context.active_object
    mon.name = f"CRT_Screen_{{i}}"
    mon.rotation_euler = (math.radians(-25), 0, 0)
    mon.data.materials.append(mat_crt)

# Pilot Chairs (2 Detailed swivel bucket seats)
for cx in [-1.0, 1.0]:
    # Chair base pedestal
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=0.4, location=(cx, 5.6, -0.15))
    base = bpy.context.active_object
    base.data.materials.append(mat_steel)
    
    # Pedestal neck
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.4, location=(cx, 5.6, 0.2))
    neck = bpy.context.active_object
    neck.data.materials.append(mat_steel)
    
    # Curved bucket seat cushion
    bpy.ops.mesh.primitive_cube_add(location=(cx, 5.6, 0.45), scale=(0.35, 0.38, 0.08))
    seat = bpy.context.active_object
    seat.name = f"Pilot_Seat_{{cx}}"
    seat.data.materials.append(mat_plastic)
    
    # Padded cushion inside
    bpy.ops.mesh.primitive_cube_add(location=(cx, 5.6, 0.49), scale=(0.3, 0.32, 0.05))
    cushion = bpy.context.active_object
    cushion.data.materials.append(mat_leather)
    
    # Backrest
    bpy.ops.mesh.primitive_cube_add(location=(cx, 5.25, 0.95), scale=(0.35, 0.06, 0.5))
    backrest = bpy.context.active_object
    backrest.rotation_euler = (math.radians(10), 0, 0)
    backrest.data.materials.append(mat_plastic)
    
    # Backrest padding
    bpy.ops.mesh.primitive_cube_add(location=(cx, 5.29, 0.95), scale=(0.3, 0.03, 0.42))
    back_pad = bpy.context.active_object
    back_pad.rotation_euler = (math.radians(10), 0, 0)
    back_pad.data.materials.append(mat_leather)

# 5. The Mess Hall / Dining Area (Circular Lounge)
# Circular Mess Table
bpy.ops.mesh.primitive_cylinder_add(radius=1.3, depth=0.8, location=(0, -0.5, -0.25))
table = bpy.context.active_object
table.name = "Mess_Table"
table.data.materials.append(mat_plastic)
bpy.ops.object.shade_smooth()

# Circular centerpiece console
bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=0.4, location=(0, -0.5, 0.25))
center_con = bpy.context.active_object
center_con.data.materials.append(mat_steel)
bpy.ops.object.shade_smooth()

# Small canisters and cups on the table (Mess details)
for idx in range(6):
    theta = idx * (2 * math.pi / 6)
    cx = 0.8 * math.cos(theta)
    cy = -0.5 + 0.8 * math.sin(theta)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.15, location=(cx, cy, 0.22))
    cup = bpy.context.active_object
    cup.data.materials.append(mat_steel)

# Mess Hall Swivel Chairs (4 rounded seats arranged radially)
chair_angles = [0.0, math.radians(90), math.radians(180), math.radians(270)]
for idx, angle in enumerate(chair_angles):
    cx = 2.0 * math.cos(angle)
    cy = -0.5 + 2.0 * math.sin(angle)
    
    # Base pedestal
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.4, location=(cx, cy, -0.45))
    cbase = bpy.context.active_object
    cbase.data.materials.append(mat_steel)
    
    # Neck
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.4, location=(cx, cy, -0.1))
    cneck = bpy.context.active_object
    cneck.data.materials.append(mat_steel)
    
    # Rounded Mess Chair
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.35, location=(cx, cy, 0.35))
    mchair = bpy.context.active_object
    mchair.name = f"Mess_Chair_{{idx}}"
    mchair.scale = (1.0, 1.0, 0.8)
    mchair.data.materials.append(mat_plastic)
    bpy.ops.object.shade_smooth()
    
    # Inner padding
    bpy.ops.mesh.primitive_cube_add(location=(cx, cy, 0.4), scale=(0.28, 0.28, 0.2))
    mpad = bpy.context.active_object
    mpad.data.materials.append(mat_leather)

# 6. Overhead Film Set Studio Lighting Grid (Trusses)
# Grid of black truss bars hanging at Z=3.6
for ty in [-4.0, 0.0, 4.0, 8.0]:
    # Transverse truss bars
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=10.0, location=(0, ty, 3.6))
    bar = bpy.context.active_object
    bar.name = f"Set_Truss_Y_{{ty}}"
    bar.rotation_euler = (0, math.radians(90), 0)
    bar.data.materials.append(mat_steel)

for tx in [-4.0, 0.0, 4.0]:
    # Longitudinal truss bars
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=14.0, location=(tx, 2.0, 3.6))
    bar = bpy.context.active_object
    bar.name = f"Set_Truss_X_{{tx}}"
    bar.rotation_euler = (math.radians(90), 0, 0)
    bar.data.materials.append(mat_steel)

# 7. Dramatic Set Studio Spotlight Rig
# Hang 4 physical spotlight models pointing down at the key set elements
spot_locations = [
    (-2.2, 5.2, "Spot_Bridge_L"), (2.2, 5.2, "Spot_Bridge_R"),
    (-1.8, -1.0, "Spot_Mess_L"), (1.8, -1.0, "Spot_Mess_R")
]

for sx, sy, sname in spot_locations:
    # Physical Studio Light Model
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=0.4, location=(sx, sy, 3.4))
    lamp = bpy.context.active_object
    lamp.name = sname + "_Model"
    lamp.data.materials.append(mat_steel)
    
    # Actual Point/Spot Light
    light_data = bpy.data.lights.new(name=sname, type='POINT')
    light_data.energy = 2200
    
    # Warm spotlights for Mess, cool cyan for Bridge
    if "Bridge" in sname:
        light_data.color = (0.1, 0.55, 1.0) # Cool blue/cyan
        light_data.energy = 2600
    else:
        light_data.color = (1.0, 0.72, 0.45) # Warm industrial halogen
        
    light_obj = bpy.data.objects.new(name=sname, object_data=light_data)
    bpy.context.collection.objects.link(light_obj)
    light_obj.location = (sx, sy, 3.1)

# Add a subtle green ambient starlight glow leaking from the front wind shield
light_leak_data = bpy.data.lights.new(name="Windshield_Leak", type='POINT')
light_leak_data.energy = 1500
light_leak_data.color = (0.05, 0.8, 0.2) # Deep toxic green
light_leak = bpy.data.objects.new(name="Windshield_Leak", object_data=light_leak_data)
bpy.context.collection.objects.link(light_leak)
light_leak.location = (0.0, 8.5, 0.8)

# 8. Master Film Set Cameras
# Camera 1: Set Wide (Master View from behind framing the entire studio set)
cam1_data = bpy.data.cameras.new(name="Camera_Set_Wide")
cam1_data.lens = 28 # Dramatic wide-angle lens
cam1_obj = bpy.data.objects.new(name="Camera_Set_Wide", object_data=cam1_data)
bpy.context.collection.objects.link(cam1_obj)
cam1_obj.location = (0.0, -7.0, 1.25)
cam1_obj.rotation_euler = (math.radians(82), 0, math.radians(180))
bpy.context.scene.camera = cam1_obj

# Camera 2: Bridge Close (Close-up of the pilot consoles and glowing CRTs)
cam2_data = bpy.data.cameras.new(name="Camera_Bridge_Close")
cam2_data.lens = 38
cam2_obj = bpy.data.objects.new(name="Camera_Bridge_Close", object_data=cam2_data)
bpy.context.collection.objects.link(cam2_obj)
cam2_obj.location = (0.0, 3.8, 0.95)
cam2_obj.rotation_euler = (math.radians(78), 0, math.radians(180))

print("USCSS Nostromo interior set modeling completed! Starting Cycles Ray-Traced Render...")

# 9. Professional Cycles Render
scene = bpy.context.scene
scene.render.engine = 'CYCLES'

# Configure GPU
try:
    preferences = bpy.context.preferences
    addons = preferences.addons
    cycles_addon = addons.get('cycles')
    if cycles_addon:
        cycles_preferences = cycles_addon.preferences
        cycles_preferences.compute_device_type = 'CUDA'
        bpy.context.scene.cycles.device = 'GPU'
        cycles_preferences.get_devices()
except:
    pass

scene.cycles.samples = 64
if hasattr(scene.cycles, "use_denoising"):
    scene.cycles.use_denoising = True

scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.filepath = r"{output_path}"

bpy.ops.render.render(write_still=True)
print("Interior Render Completed!")

# Restore Eevee and the primary master camera
scene.render.engine = 'BLENDER_EEVEE'
scene.camera = cam1_obj
"""
        res = send_command(sock, "execute_code", {"code": blender_code})
        print(f"Cycles script execution result: {res.get('result')}")
        
        # 4. Copy the rendered file to the conversation's main artifact folder
        artifact_dir = r"C:\Users\andre\.gemini\antigravity-cli\brain\bf0fdf96-df65-451f-a3dd-ee395072dc69"
        dest_path = os.path.join(artifact_dir, "nostromo_interior_set.png")
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
