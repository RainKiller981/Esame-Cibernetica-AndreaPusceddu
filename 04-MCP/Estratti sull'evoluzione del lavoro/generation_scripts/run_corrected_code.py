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
        print("Setting up beautifully illuminated and compatible Geometry Nodes scene...")
        
        user_code = """import bpy
import math
import mathutils

def clean_scene():
    \"\"\"Safe and thorough cleanup of all objects, meshes, materials, and node groups.\"\"\"
    for obj in list(bpy.data.objects): 
        bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in list(bpy.data.meshes): 
        bpy.data.meshes.remove(mesh, do_unlink=True)
    for mat in list(bpy.data.materials): 
        bpy.data.materials.remove(mat, do_unlink=True)
    for node_group in list(bpy.data.node_groups): 
        bpy.data.node_groups.remove(node_group, do_unlink=True)
    for light in list(bpy.data.lights):
        bpy.data.lights.remove(light, do_unlink=True)
    for cam in list(bpy.data.cameras):
        bpy.data.cameras.remove(cam, do_unlink=True)

def create_geometry_nodes_instancer(base_obj, instance_obj):
    \"\"\"Builds a robust, version-compatible Geometry Nodes tree to instance objects on points.\"\"\"
    modifier = base_obj.modifiers.new(name="Geo_Instancer", type='NODES')
    
    # Initialize the Node Group
    node_tree = bpy.data.node_groups.new(name="Instancer_Tree", type='GeometryNodeTree')
    modifier.node_group = node_tree
    
    # API Compatibility: Blender 4.0+ uses 'interface', Blender 3.x uses 'inputs/outputs'
    if hasattr(node_tree, "interface"): 
        node_tree.interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
        node_tree.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    else:
        node_tree.inputs.new('NodeSocketGeometry', "Geometry")
        node_tree.outputs.new('NodeSocketGeometry', "Geometry")
        
    nodes = node_tree.nodes
    links = node_tree.links
    
    # Node Creation
    node_in = nodes.new('NodeGroupInput')
    node_out = nodes.new('NodeGroupOutput')
    node_inst = nodes.new('GeometryNodeInstanceOnPoints')
    node_info = nodes.new('GeometryNodeObjectInfo')
    
    # Positional Layout
    node_in.location = (-300, 0)
    node_info.location = (-300, -200)
    node_inst.location = (0, 0)
    node_out.location = (300, 0)
    
    # Assign the instanced object
    node_info.inputs[0].default_value = instance_obj
    node_info.transform_space = 'ORIGINAL' # Use original transforms so original object hiding works
    
    # Logic Connections using index-based references (cross-version safe)
    # 1. Base Geometry (outputs[0]) -> Points Input (inputs[0])
    links.new(node_in.outputs[0], node_inst.inputs[0])
    
    # 2. Object Info Geometry (outputs[4]) -> Instance Input (inputs[2])
    links.new(node_info.outputs[4], node_inst.inputs[2])
    
    # 3. Instance Output (outputs[0]) -> Geometry Group Output (inputs[0])
    links.new(node_inst.outputs[0], node_out.inputs[0])
    
    return modifier

def create_sci_fi_materials():
    \"\"\"Creates professional dark metallic and warning glow materials.\"\"\"
    # 1. Dark Metal
    metal_mat = bpy.data.materials.new(name="Metal_Dark")
    metal_mat.use_nodes = True
    bsdf = metal_mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.06, 0.07, 0.09, 1.0)
        bsdf.inputs['Metallic'].default_value = 1.0
        bsdf.inputs['Roughness'].default_value = 0.35
        
    # 2. Emissive Orange
    glow_mat = bpy.data.materials.new(name="Glow_Orange")
    glow_mat.use_nodes = True
    bsdf_glow = glow_mat.node_tree.nodes.get("Principled BSDF")
    if bsdf_glow:
        bsdf_glow.inputs['Base Color'].default_value = (1.0, 0.3, 0.0, 1.0)
        # In newer Principled BSDF, Emission Color and Strength are inputs
        if 'Emission' in bsdf_glow.inputs:
            bsdf_glow.inputs['Emission'].default_value = (1.0, 0.3, 0.0, 1.0)
        if 'Emission Strength' in bsdf_glow.inputs:
            bsdf_glow.inputs['Emission Strength'].default_value = 5.0
            
    return metal_mat, glow_mat

def generate_nostromo_props():
    clean_scene()
    
    # Create Materials
    metal_mat, glow_mat = create_sci_fi_materials()
    
    # 1. Distribution base (Corridor floor grid)
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=8, y_subdivisions=4, size=15)
    corridor_floor = bpy.context.active_object
    corridor_floor.name = "Base_Corridor"
    corridor_floor.data.materials.append(metal_mat)
    
    # 2. Instance prop creation (Terminal cylinder)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.3, depth=1.4, location=(0, 0, 0))
    terminal_prop = bpy.context.active_object
    terminal_prop.name = "Prop_Terminal"
    terminal_prop.data.materials.append(metal_mat)
    terminal_prop.data.materials.append(glow_mat)
    
    # Add a glowing strip to the cylinder to make it look like a prop
    # We assign the glow material to a few faces
    for i, face in enumerate(terminal_prop.data.polygons):
        if i in [2, 5, 8]:
            face.material_index = 1
            
    # Apply all transforms prior to hiding/instancing
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    # Move original prop to a hidden collection to avoid cluttering scene center
    hidden_coll = bpy.data.collections.new("Hidden_Props")
    bpy.context.scene.collection.children.link(hidden_coll)
    bpy.context.scene.collection.objects.unlink(terminal_prop)
    hidden_coll.objects.link(terminal_prop)
    hidden_coll.hide_viewport = True
    hidden_coll.hide_render = True
    
    # 3. Apply the instancer modifier
    create_geometry_nodes_instancer(corridor_floor, terminal_prop)
    
    # 4. Cinematic Sci-Fi Lighting Setup
    # Overhead soft ambient light
    light_top_data = bpy.data.lights.new(name="Light_Top_Data", type='POINT')
    light_top_data.energy = 300.0
    light_top_data.color = (0.8, 0.9, 1.0)
    light_top = bpy.data.objects.new(name="Light_Top", object_data=light_top_data)
    bpy.context.scene.collection.objects.link(light_top)
    light_top.location = (0, 0, 6)
    
    # Deep blue key light (corridor shadows)
    light_blue_data = bpy.data.lights.new(name="Light_Blue_Data", type='POINT')
    light_blue_data.energy = 900.0
    light_blue_data.color = (0.05, 0.2, 1.0)
    light_blue = bpy.data.objects.new(name="Light_Blue", object_data=light_blue_data)
    bpy.context.scene.collection.objects.link(light_blue)
    light_blue.location = (-6, -4, 3)
    
    # Industrial amber warning light
    light_orange_data = bpy.data.lights.new(name="Light_Orange_Data", type='POINT')
    light_orange_data.energy = 600.0
    light_orange_data.color = (1.0, 0.35, 0.02)
    light_orange = bpy.data.objects.new(name="Light_Orange", object_data=light_orange_data)
    bpy.context.scene.collection.objects.link(light_orange)
    light_orange.location = (6, 4, 3.5)

    # 5. Active Camera setup looking at the setup
    cam_data = bpy.data.cameras.new(name="Camera_Data")
    cam_obj = bpy.data.objects.new(name="Camera", object_data=cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    
    # Position camera and point it at the grid center (0, 0, 0.8)
    cam_obj.location = (11, -11, 7.5)
    direction = mathutils.Vector((0, 0, 0.8)) - cam_obj.location
    cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam_obj
    
    # Set viewport shading to MATERIAL (LookDev) to ensure it uses active light + HDRI environment maps
    # and is NEVER black in the 3D viewport interface!
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'
                        space.shading.use_scene_lights = True
                        space.shading.use_scene_world = True

generate_nostromo_props()
print("Scene setup completed successfully with lights and materials!")
"""
        res = send_command(sock, "execute_code", {"code": user_code})
        print(f"Result: {res.get('result')}")
        
        # Capture viewport screenshot to verify
        print("Capturing viewport screenshot of generated setup...")
        target_dir = r"C:\Users\andre\Desktop\Nuova cartella (5)"
        if not os.path.exists(target_dir):
            target_dir = r"C:\Users\andre\OneDrive\Desktop\Nuova cartella (5)"
            os.makedirs(target_dir, exist_ok=True)
        
        screenshot_path = os.path.join(target_dir, "geonodes_test.png")
        screenshot_result = send_command(sock, "get_viewport_screenshot", {
            "max_size": 1024,
            "filepath": screenshot_path,
            "format": "png"
        })
        print(f"Screenshot result: {screenshot_result}")
        
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        sock.close()
        print("Socket closed.")

if __name__ == "__main__":
    main()
