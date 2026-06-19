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
    print("Connecting to Blender...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
        print("Connected!")
    except Exception as e:
        print(f"Failed to connect to Blender: {e}")
        sys.exit(1)

    try:
        print("Generating a photorealistic organic tree in Blender...")
        
        tree_code = """import bpy
import math
import mathutils
import random

def clean_scene():
    \"\"\"Thoroughly cleans the active Blender scene database.\"\"\"
    for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in list(bpy.data.meshes): bpy.data.meshes.remove(mesh, do_unlink=True)
    for mat in list(bpy.data.materials): bpy.data.materials.remove(mat, do_unlink=True)
    for node_group in list(bpy.data.node_groups): bpy.data.node_groups.remove(node_group, do_unlink=True)
    for light in list(bpy.data.lights):
        bpy.data.lights.remove(light, do_unlink=True)
    for cam in list(bpy.data.cameras):
        bpy.data.cameras.remove(cam, do_unlink=True)
    for coll in list(bpy.data.collections):
        if coll.name != "Collection": bpy.data.collections.remove(coll)

def connect_nodes(links, from_node, from_socket_name, to_node, to_socket_name):
    \"\"\"Version-safe node connection helper.\"\"\"
    from_socket = None
    if isinstance(from_socket_name, int):
        from_socket = from_node.outputs[from_socket_name]
    else:
        for out in from_node.outputs:
            if out.name.lower() == from_socket_name.lower() or out.identifier.lower() == from_socket_name.lower():
                from_socket = out
                break
        if not from_socket:
            from_socket = from_node.outputs[0]
            
    to_socket = None
    if isinstance(to_socket_name, int):
        to_socket = to_node.inputs[to_socket_name]
    else:
        for inp in to_node.inputs:
            if inp.name.lower() == to_socket_name.lower() or inp.identifier.lower() == to_socket_name.lower():
                to_socket = inp
                break
        if not to_socket:
            if to_socket_name.lower() == 'normal':
                to_socket = to_node.inputs[-1]
            else:
                to_socket = to_node.inputs[0]
                
    links.new(from_socket, to_socket)

def create_bark_material():
    \"\"\"Generates a photorealistic rough bark material with procedural grooves.\"\"\"
    mat = bpy.data.materials.new(name="Tree_Bark")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    for n in list(nodes): nodes.remove(n)
        
    node_output = nodes.new('ShaderNodeOutputMaterial')
    node_bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    node_bsdf.inputs['Base Color'].default_value = (0.16, 0.11, 0.08, 1.0) # Organic dark brown
    node_bsdf.inputs['Roughness'].default_value = 0.92
    
    node_noise = nodes.new('ShaderNodeTexNoise')
    node_noise.inputs['Scale'].default_value = 22.0
    node_noise.inputs['Detail'].default_value = 8.0
    node_noise.inputs['Roughness'].default_value = 0.75
    
    node_ramp = nodes.new('ShaderNodeValToRGB')
    node_ramp.color_ramp.elements[0].color = (0.12, 0.08, 0.06, 1.0) # Dark bark
    node_ramp.color_ramp.elements[1].color = (0.22, 0.16, 0.12, 1.0) # Light bark highlight
    
    node_bump = nodes.new('ShaderNodeBump')
    node_bump.inputs['Strength'].default_value = 0.55
    
    connect_nodes(links, node_noise, 'Color', node_ramp, 'Fac')
    connect_nodes(links, node_ramp, 'Color', node_bsdf, 'Base Color')
    connect_nodes(links, node_noise, 'Fac', node_bump, 'Height')
    connect_nodes(links, node_bump, 'Normal', node_bsdf, 'Normal')
    connect_nodes(links, node_bsdf, 'BSDF', node_output, 'Surface')
    
    return mat

def create_leaves_material():
    \"\"\"Generates a lush organic green leaf material with subtle color variations.\"\"\"
    mat = bpy.data.materials.new(name="Tree_Leaves")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    for n in list(nodes): nodes.remove(n)
        
    node_output = nodes.new('ShaderNodeOutputMaterial')
    node_bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    node_bsdf.inputs['Base Color'].default_value = (0.06, 0.28, 0.04, 1.0) # Deep foliage green
    node_bsdf.inputs['Roughness'].default_value = 0.45
    
    node_noise = nodes.new('ShaderNodeTexNoise')
    node_noise.inputs['Scale'].default_value = 14.0
    node_noise.inputs['Detail'].default_value = 4.0
    
    node_ramp = nodes.new('ShaderNodeValToRGB')
    node_ramp.color_ramp.elements[0].color = (0.04, 0.22, 0.03, 1.0) # Shadowed leaves
    node_ramp.color_ramp.elements[1].color = (0.12, 0.38, 0.08, 1.0) # Sunny leaves
    
    node_bump = nodes.new('ShaderNodeBump')
    node_bump.inputs['Strength'].default_value = 0.2
    
    connect_nodes(links, node_noise, 'Color', node_ramp, 'Fac')
    connect_nodes(links, node_ramp, 'Color', node_bsdf, 'Base Color')
    connect_nodes(links, node_noise, 'Fac', node_bump, 'Height')
    connect_nodes(links, node_bump, 'Normal', node_bsdf, 'Normal')
    connect_nodes(links, node_bsdf, 'BSDF', node_output, 'Surface')
    
    return mat

def create_ground_material():
    mat = bpy.data.materials.new(name="Mossy_Ground")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.05, 0.09, 0.04, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.98
    return mat

def recursive_branch(x, y, z, angle_x, angle_y, angle_z, length, radius, depth, max_depth, branch_parts, leaf_parts):
    \"\"\"Recursively spawns bark branches and places foliage at terminal nodes.\"\"\"
    # 1. Create Cylinder Segment
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, location=(0, 0, length / 2.0))
    branch = bpy.context.active_object
    branch.name = f"Branch_D{depth}"
    
    # 2. Orient and Position
    branch.rotation_euler = (angle_x, angle_y, angle_z)
    rot_matrix = mathutils.Euler((angle_x, angle_y, angle_z)).to_matrix()
    end_point = rot_matrix @ mathutils.Vector((0, 0, length))
    
    # Base at (x,y,z), center of cylinder translated accordingly
    branch.location = mathutils.Vector((x, y, z)) + rot_matrix @ mathutils.Vector((0, 0, length / 2.0))
    branch_parts.append(branch)
    
    # 3. Base Case: Spawns leaf sphere canopy
    if depth >= max_depth:
        # Spawn leaf canopy cluster sphere
        bpy.ops.mesh.primitive_uv_sphere_add(radius=length * 1.5, location=(x + end_point.x, y + end_point.y, z + end_point.z))
        leaf = bpy.context.active_object
        leaf.name = f"Leaves_Cluster"
        leaf_parts.append(leaf)
        return
        
    # 4. Recursive Step: Spawn two smaller branches with randomized natural angles
    # Branch 1
    new_angle_x = angle_x + math.radians(random.uniform(15, 30))
    new_angle_z = angle_z + math.radians(random.uniform(0, 360))
    recursive_branch(x + end_point.x, y + end_point.y, z + end_point.z,
                     new_angle_x, angle_y, new_angle_z,
                     length * 0.72, radius * 0.65, depth + 1, max_depth, branch_parts, leaf_parts)
                     
    # Branch 2
    new_angle_x2 = angle_x - math.radians(random.uniform(15, 30))
    new_angle_z2 = angle_z + math.radians(random.uniform(0, 360))
    recursive_branch(x + end_point.x, y + end_point.y, z + end_point.z,
                     new_angle_x2, angle_y, new_angle_z2,
                     length * 0.72, radius * 0.65, depth + 1, max_depth, branch_parts, leaf_parts)

def build_organic_tree():
    clean_scene()
    random.seed(42)
    
    # Materials
    bark_mat = create_bark_material()
    leaves_mat = create_leaves_material()
    ground_mat = create_ground_material()
    
    # 1. Create Mossy Ground Plane
    bpy.ops.mesh.primitive_plane_add(size=40.0, location=(0, 0, 0))
    ground = bpy.context.active_object
    ground.name = "Ground"
    ground.data.materials.append(ground_mat)
    
    # 2. Build Branches Skeleton Recursively
    branch_parts = []
    leaf_parts = []
    
    # Start at origin (0, 0, 0), branching straight up
    recursive_branch(x=0.0, y=0.0, z=0.0,
                     angle_x=0.0, angle_y=0.0, angle_z=0.0,
                     length=3.5, radius=0.48, depth=1, max_depth=4,
                     branch_parts=branch_parts, leaf_parts=leaf_parts)
                     
    # Add a few thick roots at the base pointing downwards into the ground
    for i in range(4):
        yaw = math.radians(i * 90 + random.uniform(-15, 15))
        pitch = math.radians(random.uniform(70, 85)) # sloping down
        bpy.ops.mesh.primitive_cylinder_add(radius=0.38, depth=1.8, location=(0, 0, 0))
        root = bpy.context.active_object
        root.name = f"Root_{i}"
        root.rotation_euler = (pitch, 0, yaw)
        rot_matrix = mathutils.Euler((pitch, 0, yaw)).to_matrix()
        root.location = rot_matrix @ mathutils.Vector((0, 0, 0.9)) # center offset
        branch_parts.append(root)
        
    # 3. Fuse Branches via Voxel Remesh and Smooth for organic flow
    bpy.ops.object.select_all(action='DESELECT')
    for b in branch_parts:
        b.select_set(True)
    bpy.context.view_layer.objects.active = branch_parts[0]
    bpy.ops.object.join()
    
    trunk_mesh = bpy.context.active_object
    trunk_mesh.name = "Tree_Trunk_And_Branches"
    
    # Apply all scale/rotations
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    # Voxel Remesh to bind limbs seamlessly
    remesh_mod = trunk_mesh.modifiers.new(name="Voxel_Remesh", type='REMESH')
    remesh_mod.mode = 'VOXEL'
    remesh_mod.voxel_size = 0.05
    remesh_mod.use_smooth_shade = True
    
    # Laplacian Smooth for natural branch joints
    smooth_mod = trunk_mesh.modifiers.new(name="Wood_Smooth", type='SMOOTH')
    smooth_mod.factor = 1.0
    smooth_mod.iterations = 8
    
    # Subtle displacement for rough wood bark grooves
    disp_tex = bpy.data.textures.new(name="Bark_Grooves", type='CLOUDS')
    disp_tex.noise_scale = 0.08
    disp_mod = trunk_mesh.modifiers.new(name="Bark_Detail", type='DISPLACE')
    disp_mod.texture = disp_tex
    disp_mod.strength = 0.035
    
    trunk_mesh.data.materials.clear()
    trunk_mesh.data.materials.append(bark_mat)
    bpy.ops.object.shade_smooth()
    
    # 4. Fuse Leaf Spheres into a single lush canopy
    bpy.ops.object.select_all(action='DESELECT')
    for l in leaf_parts:
        l.select_set(True)
    bpy.context.view_layer.objects.active = leaf_parts[0]
    bpy.ops.object.join()
    
    canopy_mesh = bpy.context.active_object
    canopy_mesh.name = "Tree_Canopy"
    
    # Apply transforms
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    # Voxel remesh to join leaves clusters
    remesh_canopy = canopy_mesh.modifiers.new(name="Canopy_Remesh", type='REMESH')
    remesh_canopy.mode = 'VOXEL'
    remesh_canopy.voxel_size = 0.08
    remesh_canopy.use_smooth_shade = True
    
    # Smooth slightly
    smooth_canopy = canopy_mesh.modifiers.new(name="Canopy_Smooth", type='SMOOTH')
    smooth_canopy.factor = 0.8
    smooth_canopy.iterations = 4
    
    # Strong noise displacement to simulate millions of tiny detailed leaves!
    leaves_tex = bpy.data.textures.new(name="Leaves_Density", type='VORONOI')
    leaves_tex.noise_scale = 0.05
    disp_canopy = canopy_mesh.modifiers.new(name="Foliage_Detail", type='DISPLACE')
    disp_canopy.texture = leaves_tex
    disp_canopy.strength = 0.28
    
    canopy_mesh.data.materials.clear()
    canopy_mesh.data.materials.append(leaves_mat)
    bpy.ops.object.shade_smooth()
    
    # 5. SUNNY OUTDOOR LIGHTING RIG
    # Sun Light
    sun_data = bpy.data.lights.new(name="Sun_Data", type='SUN')
    sun_data.energy = 8.0
    sun_data.color = (1.0, 0.98, 0.95) # warm sun
    sun_obj = bpy.data.objects.new(name="Sun", object_data=sun_data)
    bpy.context.scene.collection.objects.link(sun_obj)
    sun_obj.location = (12, -15, 18)
    direction = mathutils.Vector((0, 0, 4.0)) - sun_obj.location
    sun_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    
    # Blue Sky Ambient Fill Light
    sky_data = bpy.data.lights.new(name="Sky_Data", type='SUN')
    sky_data.energy = 2.0
    sky_data.color = (0.72, 0.86, 1.0) # cool ambient sky
    sky_obj = bpy.data.objects.new(name="Sky_Ambient", object_data=sky_data)
    bpy.context.scene.collection.objects.link(sky_obj)
    sky_obj.location = (-12, 15, 12)
    direction = mathutils.Vector((0, 0, 4.0)) - sky_obj.location
    sky_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    
    # 6. CAMERA FRAME
    cam_data = bpy.data.cameras.new(name="Tree_Cam_Data")
    cam_data.lens = 32 # wide angle
    cam_obj = bpy.data.objects.new(name="Tree_Camera", object_data=cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    
    # Position to capture the whole majestic tree
    cam_obj.location = (8.5, -12.0, 4.5)
    direction = mathutils.Vector((0.0, 0.0, 3.8)) - cam_obj.location
    cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam_obj
    
    # Viewport setup
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'
                        space.shading.use_scene_lights = True
                        space.shading.use_scene_world = True

build_organic_tree()
print("Realistic organic tree generated successfully!")
"""
        res = send_command(sock, "execute_code", {"code": tree_code})
        print(f"Result: {res.get('result')}")
        
        target_dir = r"C:\Users\andre\Desktop\Nuova cartella (5)"
        if not os.path.exists(target_dir):
            target_dir = r"C:\Users\andre\OneDrive\Desktop\Nuova cartella (5)"
            os.makedirs(target_dir, exist_ok=True)
        
        # 1. Viewport screenshot (LookDev)
        print("Capturing viewport screenshot of the organic tree...")
        screenshot_path = os.path.join(target_dir, "tempio_greco.png") # overwrite for lookdev preview
        screenshot_result = send_command(sock, "get_viewport_screenshot", {
            "max_size": 1280,
            "filepath": screenshot_path,
            "format": "png"
        })
        print(f"Screenshot result: {screenshot_result}")
        
        # 2. Production Render
        print("Rendering high quality Eevee screenshot...")
        render_path = os.path.join(target_dir, "tempio_greco_render.png")
        render_code = f"""import bpy
import os

render_path = r"{os.path.join(target_dir, 'tempio_greco_render.png')}"
bpy.context.scene.render.engine = 'BLENDER_EEVEE'
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.context.scene.render.filepath = render_path
# Set resolution
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.resolution_percentage = 100

# Execute render
bpy.ops.render.render(write_still=True)
print("Eevee render completed successfully and saved to " + render_path)
"""
        render_res = send_command(sock, "execute_code", {"code": render_code})
        print(f"Render script result: {render_res.get('result')}")
        
        # 3. Save as blend file
        print("Saving completed scene as xenomorph.blend...") # overwrite target mainfile
        blend_path = os.path.join(target_dir, "xenomorph.blend")
        save_code = f"""import bpy
bpy.ops.wm.save_as_mainfile(filepath=r"{blend_path}", copy=True)
print("Scene saved to " + r"{blend_path}")
"""
        save_res = send_command(sock, "execute_code", {"code": save_code})
        print(f"Save blend result: {save_res.get('result')}")
        
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        sock.close()
        print("Socket closed.")

if __name__ == "__main__":
    main()
