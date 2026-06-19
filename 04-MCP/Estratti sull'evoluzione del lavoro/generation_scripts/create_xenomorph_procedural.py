import socket
import json
import sys
import os

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

print("Starting Xenomorph generation...")

# 1. Clear existing mesh objects and lights
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.select_by_type(type='MESH')
bpy.ops.object.delete()

bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.select_by_type(type='LIGHT')
bpy.ops.object.delete()

bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.select_by_type(type='CAMERA')
bpy.ops.object.delete()

# 2. Create the Xenomorph Material (Glossy Bio-mechanical Black)
mat = bpy.data.materials.new(name="XenomorphMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
principled = nodes.get("Principled BSDF")
if principled:
    principled.inputs['Base Color'].default_value = (0.015, 0.02, 0.025, 1.0)
    principled.inputs['Metallic'].default_value = 0.95
    principled.inputs['Roughness'].default_value = 0.1
    if 'Specular' in principled.inputs:
        principled.inputs['Specular'].default_value = 0.8
    if 'Roughness' in principled.inputs:
        principled.inputs['Roughness'].default_value = 0.1

# 3. Create Head (Elongated Ellipsoid)
bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=1.0, location=(0, -0.3, 1.4))
head = bpy.context.active_object
head.name = "Xeno_Head"
head.scale = (0.42, 1.85, 0.45)
head.rotation_euler = (math.radians(-15), 0, 0)
head.data.materials.append(mat)
bpy.ops.object.shade_smooth()

# Inner Jaw (slightly sticking out)
bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.4, location=(0, 0.8, 1.0))
jaw = bpy.context.active_object
jaw.name = "Xeno_Jaw"
jaw.rotation_euler = (math.radians(75), 0, 0)
jaw.data.materials.append(mat)
bpy.ops.object.shade_smooth()

# 4. Create Torso and Ribs
bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=1.6, location=(0, -0.2, 0.5))
torso = bpy.context.active_object
torso.name = "Xeno_Torso"
torso.scale = (0.9, 0.7, 1.0)
torso.data.materials.append(mat)
bpy.ops.object.shade_smooth()

# Ribs (Loop of toruses)
for i in range(7):
    z_pos = 1.1 - (i * 0.18)
    y_scale = 1.0 - (i * 0.07)
    bpy.ops.mesh.primitive_torus_add(align='WORLD', location=(0, -0.2, z_pos), major_radius=0.32, minor_radius=0.06)
    rib = bpy.context.active_object
    rib.name = f"Xeno_Rib_{i}"
    rib.scale = (1.1, y_scale * 1.1, 0.5)
    rib.data.materials.append(mat)
    bpy.ops.object.shade_smooth()

# 5. Create Back Tubes (Dorsal pipes)
# Middle pipe
bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.7, location=(0, -0.45, 0.8))
tube_mid = bpy.context.active_object
tube_mid.name = "Xeno_Tube_Mid"
tube_mid.rotation_euler = (math.radians(-45), 0, 0)
tube_mid.data.materials.append(mat)
bpy.ops.object.shade_smooth()

# Left pipe
bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.6, location=(-0.18, -0.4, 0.9))
tube_l = bpy.context.active_object
tube_l.name = "Xeno_Tube_L"
tube_l.rotation_euler = (math.radians(-30), math.radians(-15), 0)
tube_l.data.materials.append(mat)
bpy.ops.object.shade_smooth()

# Right pipe
bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.6, location=(0.18, -0.4, 0.9))
tube_r = bpy.context.active_object
tube_r.name = "Xeno_Tube_R"
tube_r.rotation_euler = (math.radians(-30), math.radians(15), 0)
tube_r.data.materials.append(mat)
bpy.ops.object.shade_smooth()

# 6. Create Long Segmented Tail
for i in range(15):
    t = i / 14.0
    y = -0.5 - (t * 1.8)
    z = 0.1 - (math.sin(t * math.pi) * 0.7) - (t * 0.3)
    rad = 0.12 * (1.0 - (t * 0.5))
    
    bpy.ops.mesh.primitive_uv_sphere_add(radius=rad, location=(0, y, z))
    seg = bpy.context.active_object
    seg.name = f"Xeno_Tail_{i}"
    seg.data.materials.append(mat)
    bpy.ops.object.shade_smooth()

# Tail Spade/Stinger
bpy.ops.mesh.primitive_cone_add(radius1=0.05, depth=0.22, location=(0, -2.3, -0.2))
stinger = bpy.context.active_object
stinger.name = "Xeno_Stinger"
stinger.rotation_euler = (math.radians(90), 0, 0)
stinger.data.materials.append(mat)
bpy.ops.object.shade_smooth()

# 7. Legs (Crouched posture)
# Left Leg
bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.75, location=(-0.35, -0.1, 0.2))
thigh_l = bpy.context.active_object
thigh_l.rotation_euler = (math.radians(40), math.radians(15), 0)
thigh_l.data.materials.append(mat)
bpy.ops.object.shade_smooth()

bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.75, location=(-0.45, -0.35, -0.25))
calf_l = bpy.context.active_object
calf_l.rotation_euler = (math.radians(-35), math.radians(10), 0)
calf_l.data.materials.append(mat)
bpy.ops.object.shade_smooth()

bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.25, location=(-0.45, -0.45, -0.6))
foot_l = bpy.context.active_object
foot_l.scale = (1.0, 2.0, 0.4)
foot_l.data.materials.append(mat)
bpy.ops.object.shade_smooth()

# Right Leg
bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.75, location=(0.35, -0.1, 0.2))
thigh_r = bpy.context.active_object
thigh_r.rotation_euler = (math.radians(40), math.radians(-15), 0)
thigh_r.data.materials.append(mat)
bpy.ops.object.shade_smooth()

bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.75, location=(0.45, -0.35, -0.25))
calf_r = bpy.context.active_object
calf_r.rotation_euler = (math.radians(-35), math.radians(-10), 0)
calf_r.data.materials.append(mat)
bpy.ops.object.shade_smooth()

bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.25, location=(0.45, -0.45, -0.6))
foot_r = bpy.context.active_object
foot_r.scale = (1.0, 2.0, 0.4)
foot_r.data.materials.append(mat)
bpy.ops.object.shade_smooth()

# 8. Arms (Menacing pose)
# Left Arm
bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.6, location=(-0.45, 0.15, 0.8))
uarm_l = bpy.context.active_object
uarm_l.rotation_euler = (math.radians(-25), math.radians(35), 0)
uarm_l.data.materials.append(mat)
bpy.ops.object.shade_smooth()

bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.6, location=(-0.62, 0.5, 0.6))
farm_l = bpy.context.active_object
farm_l.rotation_euler = (math.radians(-65), math.radians(15), 0)
farm_l.data.materials.append(mat)
bpy.ops.object.shade_smooth()

bpy.ops.mesh.primitive_cone_add(radius1=0.05, depth=0.18, location=(-0.72, 0.75, 0.4))
hand_l = bpy.context.active_object
hand_l.rotation_euler = (math.radians(-90), 0, 0)
hand_l.data.materials.append(mat)
bpy.ops.object.shade_smooth()

# Right Arm
bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.6, location=(0.45, 0.15, 0.8))
uarm_r = bpy.context.active_object
uarm_r.rotation_euler = (math.radians(-25), math.radians(-35), 0)
uarm_r.data.materials.append(mat)
bpy.ops.object.shade_smooth()

bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.6, location=(0.62, 0.5, 0.6))
farm_r = bpy.context.active_object
farm_r.rotation_euler = (math.radians(-65), math.radians(-15), 0)
farm_r.data.materials.append(mat)
bpy.ops.object.shade_smooth()

bpy.ops.mesh.primitive_cone_add(radius1=0.05, depth=0.18, location=(0.72, 0.75, 0.4))
hand_r = bpy.context.active_object
hand_r.rotation_euler = (math.radians(-90), 0, 0)
hand_r.data.materials.append(mat)
bpy.ops.object.shade_smooth()

# 9. Lighting Setup
# Ambient lighting (Sci-fi lab style)
light_key_data = bpy.data.lights.new(name="Xeno_KeyLight", type='POINT')
light_key_data.energy = 600
light_key_data.color = (0.0, 0.4, 1.0) # Cool Sci-fi Blue
light_key = bpy.data.objects.new(name="Xeno_KeyLight", object_data=light_key_data)
bpy.context.collection.objects.link(light_key)
light_key.location = (-1.8, 2.5, 2.2)

light_fill_data = bpy.data.lights.new(name="Xeno_FillLight", type='POINT')
light_fill_data.energy = 250
light_fill_data.color = (0.5, 0.05, 0.8) # Deep Violet
light_fill = bpy.data.objects.new(name="Xeno_FillLight", object_data=light_fill_data)
bpy.context.collection.objects.link(light_fill)
light_fill.location = (1.8, 1.8, 1.4)

light_rim_data = bpy.data.lights.new(name="Xeno_RimLight", type='POINT')
light_rim_data.energy = 900
light_rim_data.color = (0.05, 1.0, 0.1) # Glowing Toxic Acid Green
light_rim = bpy.data.objects.new(name="Xeno_RimLight", object_data=light_rim_data)
bpy.context.collection.objects.link(light_rim)
light_rim.location = (0.0, -2.5, 1.8)

# 10. Camera Setup
camera_data = bpy.data.cameras.new(name="Xeno_Camera")
camera = bpy.data.objects.new(name="Xeno_Camera", object_data=camera_data)
bpy.context.collection.objects.link(camera)
camera.location = (1.6, 3.2, 1.1)
camera.rotation_euler = (math.radians(78), 0, math.radians(150))
bpy.context.scene.camera = camera

print("Xenomorph generation succeeded!")
"""
        
        print("Executing procedural Xenomorph generator in Blender...")
        res = send_command(sock, "execute_code", {"code": blender_code})
        print(f"Execute result: {res}")
        
        # 11. Capture viewport screenshot
        print("Capturing viewport screenshot...")
        # Path where we want to save it
        screenshot_path = r"C:\Users\andre\Desktop\xenomorph_render.png"
        screenshot_result = send_command(sock, "get_viewport_screenshot", {
            "max_size": 800,
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
