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
        
    output_path = os.path.join(target_dir, "nostromo_exterior.png")

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
        print("Modeling the USCSS Nostromo Spaceship Exterior from scratch...")
        
        blender_code = f"""import bpy
import math
import random

print("Deleting all existing objects to start fresh...")
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 1. Materials for the spaceship
# Dark industrial spaceship steel (weathered)
mat_hull = bpy.data.materials.new(name="Nostromo_Exterior_Hull")
mat_hull.use_nodes = True
nodes_hull = mat_hull.node_tree.nodes
p_hull = nodes_hull.get("Principled BSDF")
p_hull.inputs['Base Color'].default_value = (0.07, 0.075, 0.08, 1.0)
p_hull.inputs['Metallic'].default_value = 0.9
p_hull.inputs['Roughness'].default_value = 0.45

# Slightly lighter/alternate metal panels
mat_panel = bpy.data.materials.new(name="Nostromo_Exterior_Panels")
mat_panel.use_nodes = True
nodes_panel = mat_panel.node_tree.nodes
p_panel = nodes_panel.get("Principled BSDF")
p_panel.inputs['Base Color'].default_value = (0.05, 0.055, 0.06, 1.0)
p_panel.inputs['Metallic'].default_value = 0.85
p_panel.inputs['Roughness'].default_value = 0.5

# Copper Pipes
mat_copper = bpy.data.materials.new(name="Nostromo_Exterior_Copper")
mat_copper.use_nodes = True
nodes_copper = mat_copper.node_tree.nodes
p_copper = nodes_copper.get("Principled BSDF")
p_copper.inputs['Base Color'].default_value = (0.58, 0.28, 0.15, 1.0)
p_copper.inputs['Metallic'].default_value = 0.95
p_copper.inputs['Roughness'].default_value = 0.22

# Intensely glowing Engine Thrust
mat_thruster = bpy.data.materials.new(name="Nostromo_Thruster_Fire")
mat_thruster.use_nodes = True
nodes_thrust = mat_thruster.node_tree.nodes
p_thrust = nodes_thrust.get("Principled BSDF")
if 'Emission' in p_thrust.inputs:
    p_thrust.inputs['Emission'].default_value = (1.0, 0.25, 0.01, 1.0) # Nuclear bright orange
if 'Emission Strength' in p_thrust.inputs:
    p_thrust.inputs['Emission Strength'].default_value = 25.0

# 2. Build the USCSS Nostromo Hull
# Main Central Cargo Box (Commercial Refinery Hull)
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0), scale=(1.8, 3.8, 0.8))
main_hull = bpy.context.active_object
main_hull.name = "Nostromo_Hull"
main_hull.data.materials.append(mat_hull)

# Forward Command Deck (Wedge Nose)
bpy.ops.mesh.primitive_cube_add(location=(0, 4.4, 0.1), scale=(1.2, 0.8, 0.45))
command_deck = bpy.context.active_object
command_deck.name = "Nostromo_Bridge"
command_deck.scale = (1.0, 1.0, 0.7)
# Angle the nose slightly down for aerodynamical space look
command_deck.rotation_euler = (math.radians(-10), 0, 0)
command_deck.data.materials.append(mat_hull)

# Propulsion Block (Rear engine housing)
bpy.ops.mesh.primitive_cube_add(location=(0, -4.2, 0), scale=(2.2, 0.8, 1.0))
prop_block = bpy.context.active_object
prop_block.name = "Nostromo_PropulsionBlock"
prop_block.data.materials.append(mat_hull)

# 3. Create the 3 Massive Engine Thrusters (Cones arranged in a triangle at the rear)
# Top Thruster
bpy.ops.mesh.primitive_cone_add(radius1=0.6, radius2=0.45, depth=1.5, location=(0, -5.3, 0.55))
eng_top = bpy.context.active_object
eng_top.name = "Thruster_Top"
eng_top.rotation_euler = (math.radians(-90), 0, 0)
eng_top.data.materials.append(mat_hull)
bpy.ops.object.shade_smooth()

# Top Thruster Glow
bpy.ops.mesh.primitive_cylinder_add(radius=0.38, depth=0.1, location=(0, -6.0, 0.55))
glow_top = bpy.context.active_object
glow_top.rotation_euler = (math.radians(-90), 0, 0)
glow_top.data.materials.append(mat_thruster)

# Left Bottom Thruster
bpy.ops.mesh.primitive_cone_add(radius1=0.55, radius2=0.4, depth=1.5, location=(-0.9, -5.3, -0.45))
eng_left = bpy.context.active_object
eng_left.name = "Thruster_Left"
eng_left.rotation_euler = (math.radians(-90), 0, 0)
eng_left.data.materials.append(mat_hull)
bpy.ops.object.shade_smooth()

# Left Thruster Glow
bpy.ops.mesh.primitive_cylinder_add(radius=0.34, depth=0.1, location=(-0.9, -6.0, -0.45))
glow_left = bpy.context.active_object
glow_left.rotation_euler = (math.radians(-90), 0, 0)
glow_left.data.materials.append(mat_thruster)

# Right Bottom Thruster
bpy.ops.mesh.primitive_cone_add(radius1=0.55, radius2=0.4, depth=1.5, location=(0.9, -5.3, -0.45))
eng_right = bpy.context.active_object
eng_right.name = "Thruster_Right"
eng_right.rotation_euler = (math.radians(-90), 0, 0)
eng_right.data.materials.append(mat_hull)
bpy.ops.object.shade_smooth()

# Right Thruster Glow
bpy.ops.mesh.primitive_cylinder_add(radius=0.34, depth=0.1, location=(0.9, -6.0, -0.45))
glow_right = bpy.context.active_object
glow_right.rotation_euler = (math.radians(-90), 0, 0)
glow_right.data.materials.append(mat_thruster)

# 4. Procedural Greebles (Spawning industrial towers, panels, solar arrays and pipes)
random.seed(42) # Safe deterministic seed for gorgeous industrial composition

# Top Towers/Refinery towers along the spine
for i in range(4):
    y_pos = -2.5 + (i * 1.6)
    # Tower 1
    bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=1.0, location=(-0.7, y_pos, 1.1))
    t1 = bpy.context.active_object
    t1.data.materials.append(mat_panel)
    bpy.ops.object.shade_smooth()
    
    # Tower 2
    bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=1.0, location=(0.7, y_pos, 1.1))
    t2 = bpy.context.active_object
    t2.data.materials.append(mat_panel)
    bpy.ops.object.shade_smooth()

# Side Support Structures / Cargo Pods
for side in [-1.95, 1.95]:
    for y_pos in [-2.0, 0.0, 2.0]:
        bpy.ops.mesh.primitive_cube_add(location=(side, y_pos, 0), scale=(0.2, 0.6, 0.5))
        pod = bpy.context.active_object
        pod.data.materials.append(mat_panel)

# Surface Panel Plates (Greebles)
# Create 60 small, slightly overlapping raised detail plates across all faces
for _ in range(60):
    gx = random.uniform(-1.8, 1.8)
    gy = random.uniform(-3.5, 4.0)
    gz = random.choice([-0.81, 0.81])
    
    sw = random.uniform(0.15, 0.45)
    sl = random.uniform(0.2, 0.6)
    sh = random.uniform(0.01, 0.06)
    
    bpy.ops.mesh.primitive_cube_add(location=(gx, gy, gz + (sh if gz > 0 else -sh)), scale=(sw, sl, sh))
    plate = bpy.context.active_object
    plate.data.materials.append(mat_panel)

# Pipes and Conduits running along the ship hull
for _ in range(12):
    px = random.choice([-1.85, 1.85])
    pz = random.uniform(-0.6, 0.6)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=6.0, location=(px, 0.5, pz))
    pipe = bpy.context.active_object
    pipe.rotation_euler = (math.radians(90), 0, 0)
    pipe.data.materials.append(mat_copper)
    bpy.ops.object.shade_smooth()

# Nose Antenna arrays at the front
for ax in [-0.5, 0.5]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=1.5, location=(ax, 5.4, 0.1))
    ant = bpy.context.active_object
    ant.rotation_euler = (math.radians(80), 0, 0)
    ant.data.materials.append(mat_panel)

# 5. Cinematic Deep Space Lighting Setup
# Single massive sun light (Directional/Sun) to simulate high-contrast starlight
light_data = bpy.data.lights.new(name="Space_Sun", type='SUN')
light_data.energy = 8.0
light_data.color = (1.0, 0.98, 0.92) # Crisp starlight
light_obj = bpy.data.objects.new(name="Space_Sun", object_data=light_data)
bpy.context.collection.objects.link(light_obj)
# Angle it dramatically from the front-left and high above, creating strong shadow contrast
light_obj.rotation_euler = (math.radians(65), math.radians(15), math.radians(-50))

# Ambient Fill Light (Soft cool blue reflecting the cosmic nebula)
light_fill_data = bpy.data.lights.new(name="Nebula_Fill", type='POINT')
light_fill_data.energy = 2500
light_fill_data.color = (0.05, 0.2, 0.5) # Soft cosmic teal
light_fill = bpy.data.objects.new(name="Nebula_Fill", object_data=light_fill_data)
bpy.context.collection.objects.link(light_fill)
light_fill.location = (-6.0, 2.0, -3.0)

# 6. Deep Space Camera Setup (Dramatic perspective looking up at the colossal vessel)
cam_data = bpy.data.cameras.new(name="Camera_Space_Nostromo")
cam_data.lens = 32 # Wide-angle for massive scale
cam_obj = bpy.data.objects.new(name="Camera_Space_Nostromo", object_data=cam_data)
bpy.context.collection.objects.link(cam_obj)
# Positioned far back, slightly left and below, looking up towards the ship
cam_obj.location = (-7.5, 9.5, -3.5)
cam_obj.rotation_euler = (math.radians(160), 0, math.radians(-145))
bpy.context.scene.camera = cam_obj

# Set dark background in World properties
if bpy.context.scene.world:
    bpy.context.scene.world.use_nodes = True
    nodes = bpy.context.scene.world.node_tree.nodes
    bg_node = nodes.get("Background")
    if bg_node:
        bg_node.inputs['Strength'].default_value = 0.0
        bg_node.inputs['Color'].default_value = (0.0, 0.0, 0.0, 1.0)

print("USCSS Nostromo exterior modeling completed! Starting ray-traced rendering...")

# 7. Render high-quality Cycles image
scene = bpy.context.scene
scene.render.engine = 'CYCLES'

# Configure GPU rendering if available
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
print("Space Render Completed!")

# Restore Eevee for viewport performance
scene.render.engine = 'BLENDER_EEVEE'
"""
        res = send_command(sock, "execute_code", {"code": blender_code})
        print(f"Cycles script execution result: {res.get('result')}")
        
        # 4. Copy the rendered file to the conversation's main artifact folder
        artifact_dir = r"C:\Users\andre\.gemini\antigravity-cli\brain\bf0fdf96-df65-451f-a3dd-ee395072dc69"
        dest_path = os.path.join(artifact_dir, "nostromo_exterior.png")
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
