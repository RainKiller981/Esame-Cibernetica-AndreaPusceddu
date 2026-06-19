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
        print("Generating a photorealistic H.R. Giger 1979 Xenomorph from scratch...")
        
        xeno_code = """import bpy
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

def create_xeno_material():
    \"\"\"Creates a wet, moisture-glistening, deep obsidian-black biomechanical material.\"\"\"
    mat = bpy.data.materials.new(name="Xeno_Exoskeleton")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    for n in list(nodes): nodes.remove(n)
        
    node_output = nodes.new('ShaderNodeOutputMaterial')
    node_bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    node_bsdf.inputs['Base Color'].default_value = (0.012, 0.015, 0.018, 1.0)
    node_bsdf.inputs['Metallic'].default_value = 0.95
    node_bsdf.inputs['Roughness'].default_value = 0.06 # Glossy, glistening wet finish
    
    node_noise = nodes.new('ShaderNodeTexNoise')
    node_noise.inputs['Scale'].default_value = 24.0
    node_noise.inputs['Detail'].default_value = 6.0
    
    node_bump = nodes.new('ShaderNodeBump')
    node_bump.inputs['Strength'].default_value = 0.12
    
    connect_nodes(links, node_noise, 'Fac', node_bump, 'Height')
    connect_nodes(links, node_bump, 'Normal', node_bsdf, 'Normal')
    connect_nodes(links, node_bsdf, 'BSDF', node_output, 'Surface')
    
    return mat

def create_dome_material():
    \"\"\"Creates a dark glass translucent dome material.\"\"\"
    mat = bpy.data.materials.new(name="Xeno_Glass_Dome")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.015, 0.018, 0.022, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.08
        if 'Transmission Weight' in bsdf.inputs:
            bsdf.inputs['Transmission Weight'].default_value = 0.85
        elif 'Transmission' in bsdf.inputs:
            bsdf.inputs['Transmission'].default_value = 0.85
        bsdf.inputs['Alpha'].default_value = 0.45
    mat.blend_method = 'BLEND'
    return mat

def create_bone_material():
    \"\"\"Aged bone-white material for the inner skull and pharyngeal jaw.\"\"\"
    mat = bpy.data.materials.new(name="Xeno_Inner_Bone")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.68, 0.65, 0.58, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.65
        bsdf.inputs['Metallic'].default_value = 0.0
    return mat

def create_ground_material():
    mat = bpy.data.materials.new(name="Reflective_Floor")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.04, 0.04, 0.05, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.15
        bsdf.inputs['Metallic'].default_value = 0.8
    return mat

def build_big_chap(x_target, y_target, z_target, yaw_deg, xeno_mat, bone_mat, dome_mat):
    \"\"\"Procedurally constructs the authentic 1979 Big Chap Xenomorph with a voxel fused body and separate glass dome.\"\"\"
    parts = []
    
    # A. INNER HUMAN SKULL (visible under dome)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=0.28, location=(0, 0.35, 2.05))
    inner_skull = bpy.context.active_object
    inner_skull.name = "Xeno_Inner_Skull"
    inner_skull.scale = (0.9, 1.3, 0.9)
    inner_skull.rotation_euler = (math.radians(-10), 0, 0)
    inner_skull.data.materials.append(bone_mat)
    
    # Add simple nose/eye socket indentations in inner skull
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.15, location=(-0.08, 0.55, 2.05))
    eye_l = bpy.context.active_object
    eye_l.rotation_euler = (math.radians(90), 0, 0)
    eye_l.data.materials.append(xeno_mat)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.15, location=(0.08, 0.55, 2.05))
    eye_r = bpy.context.active_object
    eye_r.rotation_euler = (math.radians(90), 0, 0)
    eye_r.data.materials.append(xeno_mat)
    
    # B. HEAD MAIN STRUCTURE (to be remeshed)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.32, depth=0.6, location=(0, 0.0, 1.8))
    head_base = bpy.context.active_object
    head_base.name = "Xeno_Head_Base"
    head_base.rotation_euler = (math.radians(70), 0, 0)
    parts.append(head_base)
    
    # Pharyngeal pale jaw
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.45, location=(0, 0.72, 1.62))
    jaw = bpy.context.active_object
    jaw.name = "Xeno_Pharyngeal_Jaw"
    jaw.rotation_euler = (math.radians(78), 0, 0)
    jaw.data.materials.append(bone_mat)
    
    # C. SKELETAL TORSO (to be remeshed)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=1.65, location=(0, -0.22, 1.05))
    torso = bpy.context.active_object
    torso.name = "Xeno_Torso"
    torso.scale = (0.85, 0.65, 1.0)
    parts.append(torso)
    
    # 7-pack Biomechanical Ribs
    for i in range(8):
        z_pos = 1.68 - (i * 0.17)
        y_scale = 1.05 - (i * 0.06)
        bpy.ops.mesh.primitive_torus_add(location=(0, -0.22, z_pos), major_radius=0.28, minor_radius=0.05)
        rib = bpy.context.active_object
        rib.scale = (1.05, y_scale * 1.05, 0.45)
        parts.append(rib)
        
    # Spine vertebrae running down back
    for i in range(12):
        z_pos = 1.75 - (i * 0.14)
        y_pos = -0.36 - (math.sin(i * 0.2) * 0.08)
        bpy.ops.mesh.primitive_cube_add(size=0.12, location=(0, y_pos, z_pos))
        vert = bpy.context.active_object
        vert.scale = (1.2, 0.6, 0.6)
        parts.append(vert)
        
    # D. BIG CHAP'S 4 DORSAL PIPES
    # 1. Main Central exhaust chimney-pipe
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.85, location=(0, -0.48, 1.35))
    pipe_main = bpy.context.active_object
    pipe_main.rotation_euler = (math.radians(-50), 0, 0)
    parts.append(pipe_main)
    
    # 2. Left pipe stack
    bpy.ops.mesh.primitive_cylinder_add(radius=0.048, depth=0.72, location=(-0.16, -0.42, 1.48))
    pipe_l = bpy.context.active_object
    pipe_l.rotation_euler = (math.radians(-35), math.radians(-12), 0)
    parts.append(pipe_l)
    
    # 3. Right pipe stack
    bpy.ops.mesh.primitive_cylinder_add(radius=0.048, depth=0.72, location=(0.16, -0.42, 1.48))
    pipe_r = bpy.context.active_object
    pipe_r.rotation_euler = (math.radians(-35), math.radians(12), 0)
    parts.append(pipe_r)
    
    # 4. Lower central stack
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.6, location=(0, -0.46, 1.08))
    pipe_low = bpy.context.active_object
    pipe_low.rotation_euler = (math.radians(-60), 0, 0)
    parts.append(pipe_low)
    
    # E. GAUNT SKELETAL LIMBS
    # Left Arm
    bpy.ops.mesh.primitive_cylinder_add(radius=0.065, depth=0.62, location=(-0.42, 0.12, 1.38))
    uarm_l = bpy.context.active_object
    uarm_l.rotation_euler = (math.radians(-25), math.radians(35), 0)
    parts.append(uarm_l)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.62, location=(-0.58, 0.48, 1.18))
    farm_l = bpy.context.active_object
    farm_l.rotation_euler = (math.radians(-65), math.radians(15), 0)
    parts.append(farm_l)
    bpy.ops.mesh.primitive_cone_add(radius1=0.042, depth=0.18, location=(-0.68, 0.72, 0.98))
    hand_l = bpy.context.active_object
    hand_l.rotation_euler = (math.radians(-90), 0, 0)
    parts.append(hand_l)
    
    # Right Arm
    bpy.ops.mesh.primitive_cylinder_add(radius=0.065, depth=0.62, location=(0.42, 0.12, 1.38))
    uarm_r = bpy.context.active_object
    uarm_r.rotation_euler = (math.radians(-25), math.radians(-35), 0)
    parts.append(uarm_r)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.62, location=(0.58, 0.48, 1.18))
    farm_r = bpy.context.active_object
    farm_r.rotation_euler = (math.radians(-65), math.radians(-15), 0)
    parts.append(farm_r)
    bpy.ops.mesh.primitive_cone_add(radius1=0.042, depth=0.18, location=(0.72, 0.72, 0.98))
    hand_r = bpy.context.active_object
    hand_r.rotation_euler = (math.radians(-90), 0, 0)
    parts.append(hand_r)
    
    # Left Leg (digitigrade skeletal joints)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.09, depth=0.72, location=(-0.3, -0.1, 0.75))
    thigh_l = bpy.context.active_object
    thigh_l.rotation_euler = (math.radians(40), math.radians(15), 0)
    parts.append(thigh_l)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.062, depth=0.72, location=(-0.38, -0.32, 0.32))
    calf_l = bpy.context.active_object
    calf_l.rotation_euler = (math.radians(-35), math.radians(10), 0)
    parts.append(calf_l)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.048, depth=0.25, location=(-0.38, -0.42, -0.02))
    foot_l = bpy.context.active_object
    foot_l.scale = (1.0, 1.8, 0.4)
    parts.append(foot_l)
    
    # Right Leg
    bpy.ops.mesh.primitive_cylinder_add(radius=0.09, depth=0.72, location=(0.3, -0.1, 0.75))
    thigh_r = bpy.context.active_object
    thigh_r.rotation_euler = (math.radians(40), math.radians(-15), 0)
    parts.append(thigh_r)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.062, depth=0.72, location=(0.38, -0.32, 0.32))
    calf_r = bpy.context.active_object
    calf_r.rotation_euler = (math.radians(-35), math.radians(-10), 0)
    parts.append(calf_r)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.048, depth=0.25, location=(0.38, -0.42, -0.02))
    foot_r = bpy.context.active_object
    foot_r.scale = (1.0, 1.8, 0.4)
    parts.append(foot_r)
    
    # F. VERTEBRAE TAIL
    for i in range(18):
        t = i / 17.0
        y = -0.45 - (t * 1.95)
        z = 0.65 - (math.sin(t * math.pi) * 0.72) - (t * 0.32)
        rad = 0.11 * (1.0 - (t * 0.55))
        bpy.ops.mesh.primitive_uv_sphere_add(radius=rad, location=(0, y, z))
        seg = bpy.context.active_object
        parts.append(seg)
        # Vertebrae spines on tail
        bpy.ops.mesh.primitive_cone_add(radius1=rad * 0.4, depth=rad * 1.5, location=(0, y, z + rad))
        seg_sp = bpy.context.active_object
        seg_sp.rotation_euler = (math.radians(90), 0, 0)
        parts.append(seg_sp)
        
    # Stinger
    bpy.ops.mesh.primitive_cone_add(radius1=0.04, depth=0.2, location=(0, -2.4, 0.35))
    stinger = bpy.context.active_object
    stinger.rotation_euler = (math.radians(90), 0, 0)
    parts.append(stinger)
    
    # G. ORGANIC VOXEL FUSION & REMESHING OF THE BODY
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = torso
    bpy.ops.object.join()
    
    xeno_mesh = bpy.context.active_object
    xeno_mesh.name = "Xenomorph_Body"
    
    # Apply all transforms before remeshing
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    # 1. Add Voxel Remesh to merge discrete primitives
    remesh_mod = xeno_mesh.modifiers.new(name="Voxel_Remesh", type='REMESH')
    remesh_mod.mode = 'VOXEL'
    remesh_mod.voxel_size = 0.035
    remesh_mod.use_smooth_shade = True
    
    # 2. Add Smooth Modifier to make joints flow like muscle/skin
    smooth_mod = xeno_mesh.modifiers.new(name="Organic_Smooth", type='SMOOTH')
    smooth_mod.factor = 1.0
    smooth_mod.iterations = 12
    
    # 3. Add Displacement for H.R. Giger organic-mechanical surface texture
    disp_tex = bpy.data.textures.new(name="Xeno_Skin_Noise", type='CLOUDS')
    disp_tex.noise_scale = 0.15
    disp_mod = xeno_mesh.modifiers.new(name="Organic_Detail", type='DISPLACE')
    disp_mod.texture = disp_tex
    disp_mod.strength = 0.015
    
    # Assign material & apply smooth shading
    xeno_mesh.data.materials.clear()
    xeno_mesh.data.materials.append(xeno_mat)
    bpy.ops.object.shade_smooth()
    
    # H. TRANSLUCENT DOME OVER HEAD
    # Create the iconic smooth cylindrical glass dome on top
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.38, depth=1.85, location=(0, -0.22, 2.02))
    dome = bpy.context.active_object
    dome.name = "Xeno_Glass_Dome"
    dome.scale = (1.0, 1.0, 0.95)
    dome.rotation_euler = (math.radians(72), 0, 0)
    dome.data.materials.append(dome_mat)
    bpy.ops.object.shade_smooth()
    
    # Set final parents using an Empty to transform the entire "Big Chap" unified system!
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    xeno_system = bpy.context.active_object
    xeno_system.name = "Xenomorph_System"
    
    # Parent body, dome, inner skull and inner jaw to Empty
    xeno_mesh.parent = xeno_system
    dome.parent = xeno_system
    inner_skull.parent = xeno_system
    eye_l.parent = xeno_system
    eye_r.parent = xeno_system
    jaw.parent = xeno_system
    
    # Set final pose position and orientation
    xeno_system.location = (x_target, y_target, z_target)
    xeno_system.rotation_euler = (0, 0, math.radians(yaw_deg))
    xeno_system.scale = (1.1, 1.1, 1.1)
    
    return xeno_system

def build_standalone_scene():
    clean_scene()
    
    # Materials
    xeno_mat = create_xeno_material()
    dome_mat = create_dome_material()
    bone_mat = create_bone_material()
    ground_mat = create_ground_material()
    
    # 1. Black Reflective Ground Plane
    bpy.ops.mesh.primitive_plane_add(size=30.0, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "Reflective_Floor"
    floor.data.materials.append(ground_mat)
    
    # 2. Build 1979 Big Chap Xenomorph at the center
    # Set position to (0, 0, 0.05) crouching/standing tall
    xeno = build_big_chap(x_target=0.0, y_target=0.0, z_target=0.05, yaw_deg=180,
                           xeno_mat=xeno_mat, bone_mat=bone_mat, dome_mat=dome_mat)
    
    # 3. MOODY STUDIO Lighting Rig (Dramatic Chiaroscuro)
    # Key Light (Cool Ice White from left)
    key_data = bpy.data.lights.new(name="Studio_Key_Data", type='POINT')
    key_data.energy = 700.0
    key_data.color = (0.85, 0.92, 1.0)
    key_light = bpy.data.objects.new(name="Studio_Key", object_data=key_data)
    bpy.context.scene.collection.objects.link(key_light)
    key_light.location = (-2.5, -2.2, 3.2)
    
    # Rim Light (Warm Orange/Red from behind)
    rim_data = bpy.data.lights.new(name="Studio_Rim_Data", type='POINT')
    rim_data.energy = 550.0
    rim_data.color = (1.0, 0.28, 0.04) # Saturated orange-red
    rim_light = bpy.data.objects.new(name="Studio_Rim", object_data=rim_data)
    bpy.context.scene.collection.objects.link(rim_light)
    rim_light.location = (1.5, 2.5, 2.5)
    
    # Soft Fill Light (Dim cool cyan from right)
    fill_data = bpy.data.lights.new(name="Studio_Fill_Data", type='POINT')
    fill_data.energy = 180.0
    fill_data.color = (0.1, 0.45, 0.65)
    fill_light = bpy.data.objects.new(name="Studio_Fill", object_data=fill_data)
    bpy.context.scene.collection.objects.link(fill_light)
    fill_light.location = (2.2, -1.8, 1.8)
    
    # 4. CAMERA SETUP
    cam_data = bpy.data.cameras.new(name="BigChap_Cam_Data")
    cam_data.lens = 50 # 50mm portrait lens
    cam_obj = bpy.data.objects.new(name="BigChap_Camera", object_data=cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    
    # Position to capture the close-up portrait of the head dome and jaw
    cam_obj.location = (0.6, -2.1, 1.5)
    direction = mathutils.Vector((-0.1, 0.35, 1.95)) - cam_obj.location
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

build_standalone_scene()
print("Authentic 1979 Big Chap Xenomorph generated successfully from scratch!")
"""
        res = send_command(sock, "execute_code", {"code": xeno_code})
        print(f"Result: {res.get('result')}")
        
        target_dir = r"C:\Users\andre\Desktop\Nuova cartella (5)"
        if not os.path.exists(target_dir):
            target_dir = r"C:\Users\andre\OneDrive\Desktop\Nuova cartella (5)"
            os.makedirs(target_dir, exist_ok=True)
        
        # 1. Viewport screenshot (LookDev)
        print("Capturing viewport screenshot of the Xenomorph...")
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
        print("Saving completed scene as xenomorph.blend...")
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
