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
        print("Adding detailed grimy spaceship corridor and biomechanical Xenomorph portrait to the scene...")
        
        temple_code = """import bpy
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

def create_marble_material():
    mat = bpy.data.materials.new(name="Greek_Marble")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    for n in list(nodes): nodes.remove(n)
        
    node_output = nodes.new('ShaderNodeOutputMaterial')
    node_bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    node_bsdf.inputs['Base Color'].default_value = (0.93, 0.91, 0.88, 1.0)
    node_bsdf.inputs['Roughness'].default_value = 0.5
    
    node_noise = nodes.new('ShaderNodeTexNoise')
    node_noise.inputs['Scale'].default_value = 12.0
    node_noise.inputs['Detail'].default_value = 5.0
    node_noise.inputs['Roughness'].default_value = 0.65
    
    node_ramp = nodes.new('ShaderNodeValToRGB')
    node_ramp.color_ramp.elements[0].color = (0.94, 0.92, 0.89, 1.0)
    node_ramp.color_ramp.elements[1].color = (0.82, 0.79, 0.74, 1.0)
    
    node_bump = nodes.new('ShaderNodeBump')
    node_bump.inputs['Strength'].default_value = 0.05
    
    connect_nodes(links, node_noise, 'Fac', node_ramp, 'Fac')
    connect_nodes(links, node_ramp, 'Color', node_bsdf, 'Base Color')
    connect_nodes(links, node_noise, 'Fac', node_bump, 'Height')
    connect_nodes(links, node_bump, 'Normal', node_bsdf, 'Normal')
    connect_nodes(links, node_bsdf, 'BSDF', node_output, 'Surface')
    
    return mat

def create_jointed_stone_material():
    mat = bpy.data.materials.new(name="Stone_Blocks")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    for n in list(nodes): nodes.remove(n)
        
    node_output = nodes.new('ShaderNodeOutputMaterial')
    node_bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    node_bsdf.inputs['Base Color'].default_value = (0.91, 0.89, 0.86, 1.0)
    node_bsdf.inputs['Roughness'].default_value = 0.6
    
    node_brick = nodes.new('ShaderNodeTexBrick')
    node_brick.inputs['Mortar Size'].default_value = 0.006
    node_brick.inputs['Mortar Smooth'].default_value = 0.1
    node_brick.inputs['Scale'].default_value = 3.5
    node_brick.inputs['Color1'].default_value = (0.93, 0.91, 0.88, 1.0)
    node_brick.inputs['Color2'].default_value = (0.88, 0.86, 0.83, 1.0)
    node_brick.inputs['Mortar'].default_value = (0.65, 0.63, 0.60, 1.0)
    
    node_bump = nodes.new('ShaderNodeBump')
    node_bump.inputs['Strength'].default_value = 0.12
    
    connect_nodes(links, node_brick, 'Color', node_bsdf, 'Base Color')
    connect_nodes(links, node_brick, 'Fac', node_bump, 'Height')
    connect_nodes(links, node_bump, 'Normal', node_bsdf, 'Normal')
    connect_nodes(links, node_bsdf, 'BSDF', node_output, 'Surface')
    
    return mat

def create_grimy_metal_material():
    \"\"\"Generates photorealistic grimy, rusty metal material for the spaceship.\"\"\"
    mat = bpy.data.materials.new(name="Grimy_Metal")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    for n in list(nodes): nodes.remove(n)
        
    node_output = nodes.new('ShaderNodeOutputMaterial')
    node_bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    node_bsdf.inputs['Base Color'].default_value = (0.08, 0.08, 0.08, 1.0)
    node_bsdf.inputs['Metallic'].default_value = 1.0
    node_bsdf.inputs['Roughness'].default_value = 0.5
    
    node_noise = nodes.new('ShaderNodeTexNoise')
    node_noise.inputs['Scale'].default_value = 18.0
    node_noise.inputs['Detail'].default_value = 6.0
    
    node_ramp = nodes.new('ShaderNodeValToRGB')
    node_ramp.color_ramp.elements[0].color = (0.04, 0.04, 0.04, 1.0) # Dark industrial iron
    node_ramp.color_ramp.elements[1].color = (0.15, 0.11, 0.07, 1.0) # Rusty grime
    
    node_bump = nodes.new('ShaderNodeBump')
    node_bump.inputs['Strength'].default_value = 0.18
    
    connect_nodes(links, node_noise, 'Color', node_ramp, 'Fac')
    connect_nodes(links, node_ramp, 'Color', node_bsdf, 'Base Color')
    connect_nodes(links, node_noise, 'Fac', node_bump, 'Height')
    connect_nodes(links, node_bump, 'Normal', node_bsdf, 'Normal')
    connect_nodes(links, node_bsdf, 'BSDF', node_output, 'Surface')
    
    return mat

def create_xeno_material():
    \"\"\"Creates bio-mechanical obsidian-black exoskeleton glistening with moisture.\"\"\"
    mat = bpy.data.materials.new(name="Xeno_Exoskeleton")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.012, 0.015, 0.018, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.95
        bsdf.inputs['Roughness'].default_value = 0.05 # Glistening wet specular highlights
    return mat

def create_gold_material():
    mat = bpy.data.materials.new(name="Temple_Gold")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (1.00, 0.78, 0.35, 1.0)
        bsdf.inputs['Metallic'].default_value = 1.0
        bsdf.inputs['Roughness'].default_value = 0.15
    return mat

def create_wood_material():
    mat = bpy.data.materials.new(name="Wood_Door")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.16, 0.09, 0.05, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.7
    return mat

def create_terracotta_material():
    mat = bpy.data.materials.new(name="Terracotta_Clay")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.55, 0.27, 0.15, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.85
    return mat

def create_ground_material():
    mat = bpy.data.materials.new(name="Ground_Stone")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.07, 0.11, 0.06, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.98
    return mat

def create_column(x, y, marble_mat):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, 1.275))
    plinth = bpy.context.active_object
    plinth.scale = (0.95, 0.95, 0.15)
    plinth.data.materials.append(marble_mat)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.48, depth=0.1, location=(x, y, 1.4))
    torus1 = bpy.context.active_object
    torus1.data.materials.append(marble_mat)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.44, depth=0.08, location=(x, y, 1.49))
    torus2 = bpy.context.active_object
    torus2.data.materials.append(marble_mat)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.36, depth=5.2, location=(x, y, 4.13))
    shaft = bpy.context.active_object
    shaft.data.materials.append(marble_mat)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.45, depth=0.15, location=(x, y, 6.805))
    echinus = bpy.context.active_object
    echinus.data.materials.append(marble_mat)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, 6.955))
    abacus = bpy.context.active_object
    abacus.scale = (0.95, 0.95, 0.15)
    abacus.data.materials.append(marble_mat)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

def create_broken_column(x, y, shaft_height, marble_mat):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, 1.275))
    plinth = bpy.context.active_object
    plinth.scale = (0.95, 0.95, 0.15)
    plinth.data.materials.append(marble_mat)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.48, depth=0.1, location=(x, y, 1.4))
    torus1 = bpy.context.active_object
    torus1.data.materials.append(marble_mat)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.44, depth=0.08, location=(x, y, 1.49))
    torus2 = bpy.context.active_object
    torus2.data.materials.append(marble_mat)
    
    z_center = 1.53 + shaft_height / 2.0
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.36, depth=shaft_height, location=(x, y, z_center))
    shaft = bpy.context.active_object
    shaft.data.materials.append(marble_mat)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.36, depth=2.2, location=(x - 1.4, y + 0.9, 1.55))
    piece1 = bpy.context.active_object
    piece1.rotation_euler = (math.radians(84), math.radians(12), math.radians(-35))
    piece1.data.materials.append(marble_mat)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x - 2.4, y + 1.4, 1.35))
    abacus = bpy.context.active_object
    abacus.scale = (0.95, 0.95, 0.15)
    abacus.rotation_euler = (math.radians(14), math.radians(-6), math.radians(30))
    abacus.data.materials.append(marble_mat)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

def create_completely_collapsed_column(x, y, marble_mat):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, 1.275))
    plinth = bpy.context.active_object
    plinth.scale = (0.95, 0.95, 0.15)
    plinth.data.materials.append(marble_mat)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.36, depth=2.8, location=(x + 0.4, y - 1.9, 1.5))
    piece = bpy.context.active_object
    piece.rotation_euler = (math.radians(90), math.radians(0), math.radians(40))
    piece.data.materials.append(marble_mat)

def create_roof_mesh(width, length, height, base_z, marble_mat):
    mesh = bpy.data.meshes.new("RoofMesh")
    obj = bpy.data.objects.new("Temple_Roof", mesh)
    bpy.context.scene.collection.objects.link(obj)
    w, l, h = width / 2.0, length / 2.0, height
    verts = [
        (-w, -l, base_z), (w, -l, base_z), (w, l, base_z), (-w, l, base_z),
        (0, -l, base_z + h), (0, l, base_z + h)
    ]
    faces = [
        (0, 1, 2, 3), (0, 4, 1), (3, 2, 5), (0, 3, 5, 4), (1, 4, 5, 2)
    ]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj.data.materials.append(marble_mat)
    return obj

def create_ancient_throne(x, y, z, wood_mat, gold_mat):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, z + 0.8))
    seat = bpy.context.active_object
    seat.scale = (1.6, 1.6, 0.2)
    seat.data.materials.append(wood_mat)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    for lx, ly in [(-0.7, -0.7), (0.7, -0.7), (-0.7, 0.7), (0.7, 0.7)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.1, depth=0.8, location=(x + lx, y + ly, z + 0.4))
        leg = bpy.context.active_object
        leg.data.materials.append(wood_mat)
        
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y + 0.7, z + 1.9))
    back = bpy.context.active_object
    back.scale = (1.6, 0.18, 2.0)
    back.data.materials.append(wood_mat)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    for ax in [-0.75, 0.75]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x + ax, y, z + 1.2))
        arm = bpy.context.active_object
        arm.scale = (0.15, 1.5, 0.6)
        arm.data.materials.append(wood_mat)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(x - 0.7, y + 0.7, z + 2.9))
    orn1 = bpy.context.active_object
    orn1.data.materials.append(gold_mat)
    
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(x + 0.7, y + 0.7, z + 2.9))
    orn2 = bpy.context.active_object
    orn2.data.materials.append(gold_mat)

def create_ruined_altar(x, y, z, stone_mat):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, z + 0.6))
    altar = bpy.context.active_object
    altar.scale = (2.2, 3.2, 1.2)
    altar.rotation_euler = (math.radians(-5), math.radians(4), math.radians(10))
    altar.data.materials.append(stone_mat)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

def create_amphora(x, y, z, rot_euler, terracotta_mat):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.38, location=(x, y, z + 0.38))
    body = bpy.context.active_object
    body.data.materials.append(terracotta_mat)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.14, depth=0.4, location=(x, y, z + 0.78))
    neck = bpy.context.active_object
    neck.data.materials.append(terracotta_mat)
    
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True)
    neck.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.join()
    
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    body.location = (x, y, z)
    body.rotation_euler = rot_euler

def create_broken_table(x, y, z, wood_mat):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, z + 0.6))
    table = bpy.context.active_object
    table.scale = (2.5, 1.3, 0.08)
    table.rotation_euler = (math.radians(18), math.radians(-12), math.radians(20))
    table.data.materials.append(wood_mat)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.08, depth=0.8, location=(x - 0.9, y - 0.4, z + 0.4))
    leg1 = bpy.context.active_object
    leg1.data.materials.append(wood_mat)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.08, depth=0.8, location=(x + 0.8, y + 0.6, z + 0.04))
    leg2 = bpy.context.active_object
    leg2.rotation_euler = (math.radians(90), math.radians(35), 0)
    leg2.data.materials.append(wood_mat)

def spawn_scattered_debris(stone_mat):
    random.seed(101)
    for i in range(16):
        rx, ry, rz = random.uniform(-9.5, 9.5), random.uniform(-15.5, 15.5), 1.3
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(rx, ry, rz))
        deb = bpy.context.active_object
        deb.scale = (random.uniform(0.3, 0.75), random.uniform(0.3, 0.75), random.uniform(0.15, 0.4))
        deb.rotation_euler = (math.radians(random.uniform(-40, 40)), math.radians(random.uniform(-40, 40)), math.radians(random.uniform(0, 360)))
        deb.data.materials.append(stone_mat)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

def create_xenomorph(x_target, y_target, z_target, yaw_deg, xeno_mat):
    \"\"\"Procedurally constructs the authentic 1979 'Big Chap' designed by H.R. Giger.
    Features: Translucent elongated dome, inner humanoid skull bone structure visible through the dome,
    pale pharyngeal jaw, skeletal ribcage, 4 prominent dorsal exhaust pipes, and a long vertebrae tail.
    Uses Voxel Remesh + Smooth on the body, keeping the outer dome separate and glassy for realistic transmission.\"\"\"
    
    # 1. Create Materials
    # Translucent glass dome material
    dome_mat = bpy.data.materials.new(name="Xeno_Translucent_Dome")
    dome_mat.use_nodes = True
    bsdf_dome = dome_mat.node_tree.nodes.get("Principled BSDF")
    if bsdf_dome:
        bsdf_dome.inputs['Base Color'].default_value = (0.015, 0.018, 0.022, 1.0)
        bsdf_dome.inputs['Roughness'].default_value = 0.08
        if 'Transmission Weight' in bsdf_dome.inputs:
            bsdf_dome.inputs['Transmission Weight'].default_value = 0.85
        elif 'Transmission' in bsdf_dome.inputs:
            bsdf_dome.inputs['Transmission'].default_value = 0.85
        bsdf_dome.inputs['Alpha'].default_value = 0.45
    dome_mat.blend_method = 'BLEND'
    
    # Pale Bone material for the inner skull and jaw
    bone_mat = bpy.data.materials.new(name="Xeno_Inner_Bone")
    bone_mat.use_nodes = True
    bsdf_bone = bone_mat.node_tree.nodes.get("Principled BSDF")
    if bsdf_bone:
        bsdf_bone.inputs['Base Color'].default_value = (0.68, 0.65, 0.58, 1.0)
        bsdf_bone.inputs['Roughness'].default_value = 0.65
        bsdf_bone.inputs['Metallic'].default_value = 0.0
        
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

def build_greek_temple_ruins(stone_blocks_mat, marble_mat, wood_mat, gold_mat):
    \"\"\"Generates the complete detailed temple ruins at (0, 0, 0).\"\"\"
    # Steps
    for i, scale in enumerate([(20.0, 32.0, 0.4), (19.0, 31.0, 0.4), (18.0, 30.0, 0.4)]):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.2 + i * 0.4))
        step = bpy.context.active_object
        step.scale = scale
        step.data.materials.append(stone_blocks_mat)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        
    # Columns Colonnade
    x_coords = [-8.0, -4.8, -1.6, 1.6, 4.8, 8.0]
    y_coords = [-14.0, -11.2, -8.4, -5.6, -2.8, 0.0, 2.8, 5.6, 8.4, 11.2, 14.0]
    for x in x_coords:
        for y in y_coords:
            if x == -8.0 or x == 8.0 or y == -14.0 or y == 14.0:
                if x == -8.0 and y == -5.6:
                    create_broken_column(x, y, shaft_height=1.4, marble_mat=marble_mat)
                elif x == 8.0 and y == 5.6:
                    create_broken_column(x, y, shaft_height=2.3, marble_mat=marble_mat)
                elif x == -4.8 and y == 14.0:
                    create_completely_collapsed_column(x, y, marble_mat=marble_mat)
                else:
                    create_column(x, y, marble_mat)
                    
    create_column(-2.5, -11.2, marble_mat)
    create_column(2.5, -11.2, marble_mat)
    
    # Cella
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 4.1))
    cella = bpy.context.active_object
    cella.scale = (10.0, 21.0, 5.8)
    cella.data.materials.append(stone_blocks_mat)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # Door
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.5, -10.45, 3.1))
    door = bpy.context.active_object
    door.scale = (2.6, 0.1, 4.1)
    door.rotation_euler = (math.radians(14), math.radians(-10), math.radians(22))
    door.data.materials.append(wood_mat)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # Entablature & Frieze
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 7.43))
    arch = bpy.context.active_object
    arch.scale = (17.4, 29.4, 0.8)
    arch.data.materials.append(marble_mat)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 8.13))
    frieze = bpy.context.active_object
    frieze.scale = (17.8, 29.8, 0.6)
    frieze.data.materials.append(marble_mat)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # Roof
    create_roof_mesh(width=18.4, length=30.4, height=3.6, base_z=8.43, marble_mat=marble_mat)
    
    # Pediment Golden Shield
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.9, depth=0.08, location=(0.1, -14.82, 9.95))
    shield = bpy.context.active_object
    shield.rotation_euler = (math.radians(86), math.radians(4), math.radians(8))
    shield.data.materials.append(gold_mat)
    
    # Ornaments & furniture (throne, altar, table, amphorae)
    create_ancient_throne(0.0, 6.5, 1.2, wood_mat=wood_mat, gold_mat=gold_mat)
    create_ruined_altar(0.0, 1.0, 1.2, stone_mat=stone_blocks_mat)
    create_broken_table(-2.8, -7.5, 1.2, wood_mat=wood_mat)
    spawn_scattered_debris(stone_mat=stone_blocks_mat)

def build_spaceship_corridor(grimy_metal_mat):
    \"\"\"Generates a dark, narrow, pipe-filled spaceship corridor at x = -40.\"\"\"
    # Floor
    bpy.ops.mesh.primitive_plane_add(size=40, location=(-40.0, 0.0, 0.0))
    floor = bpy.context.active_object
    floor.name = "Spaceship_Floor"
    floor.scale = (0.1, 1.0, 1.0)
    floor.data.materials.append(grimy_metal_mat)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # Left Wall (Grungy metal box)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-42.05, 0.0, 2.5))
    wall_l = bpy.context.active_object
    wall_l.name = "Spaceship_Wall_L"
    wall_l.scale = (0.1, 40.0, 5.0)
    wall_l.data.materials.append(grimy_metal_mat)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # Right Wall
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-37.95, 0.0, 2.5))
    wall_r = bpy.context.active_object
    wall_r.name = "Spaceship_Wall_R"
    wall_r.scale = (0.1, 40.0, 5.0)
    wall_r.data.materials.append(grimy_metal_mat)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # Pipes and conduits along left wall
    for i in range(4):
        z_pipe = 0.8 + i * 1.1
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.08, depth=40.0, location=(-41.85, 0.0, z_pipe))
        pipe = bpy.context.active_object
        pipe.name = f"L_Wall_Pipe_{i}"
        pipe.rotation_euler = (math.radians(90), 0, 0)
        pipe.data.materials.append(grimy_metal_mat)
        
    # Vertical pipes/support conduits on left wall
    for y in [-8.0, -4.0, 0.0, 4.0, 8.0]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.06, depth=5.0, location=(-41.9, y, 2.5))
        vert_pipe = bpy.context.active_object
        vert_pipe.name = f"L_Wall_VertPipe_{y}"
        vert_pipe.data.materials.append(grimy_metal_mat)

def build_combined_scene():
    clean_scene()
    
    # Materials
    marble_mat = create_marble_material()
    stone_blocks_mat = create_jointed_stone_material()
    grimy_metal_mat = create_grimy_metal_material()
    xeno_mat = create_xeno_material()
    gold_mat = create_gold_material()
    wood_mat = create_wood_material()
    terracotta_mat = create_terracotta_material()
    ground_mat = create_ground_material()
    
    # 1. Build temple ruins at (0, 0, 0)
    build_greek_temple_ruins(stone_blocks_mat, marble_mat, wood_mat, gold_mat)
    
    # 2. Build spaceship corridor at x = -40
    build_spaceship_corridor(grimy_metal_mat)
    
    # 3. Build Xenomorph inside the spaceship corridor, crouching low, clinging to the pipe-filled wall!
    # Placed at x=-39.8, y=1.2, z=0.4 (tilted towards left wall to look like it's clinging!)
    xeno = create_xenomorph(x_target=-40.5, y_target=1.8, z_target=0.4, yaw_deg=180, xeno_mat=xeno_mat)
    # Tilt slightly to make it cling dynamically to the wall pipes
    xeno.rotation_euler = (math.radians(15), math.radians(-10), math.radians(165))
    
    # 4. CHIAROSCURO LIGHTING RIG (Pulsing Red Emergency lights)
    # Red Emergency Light 1 (front of Xenomorph)
    red1_data = bpy.data.lights.new(name="Red_Emergency_1_Data", type='POINT')
    red1_data.energy = 550.0
    red1_data.color = (1.0, 0.02, 0.02) # Saturated blood red
    red1 = bpy.data.objects.new(name="Red_Emergency_1", object_data=red1_data)
    bpy.context.scene.collection.objects.link(red1)
    red1.location = (-40.0, -1.5, 3.2)
    
    # Red Emergency Light 2 (behind Xenomorph)
    red2_data = bpy.data.lights.new(name="Red_Emergency_2_Data", type='POINT')
    red2_data.energy = 350.0
    red2_data.color = (1.0, 0.02, 0.02)
    red2 = bpy.data.objects.new(name="Red_Emergency_2", object_data=red2_data)
    bpy.context.scene.collection.objects.link(red2)
    red2.location = (-40.0, 5.0, 3.0)
    
    # Dim, cool twilight rim light (contrast highlights on exoskeleton)
    cool_rim_data = bpy.data.lights.new(name="Cool_Rim_Data", type='POINT')
    cool_rim_data.energy = 150.0
    cool_rim_data.color = (0.05, 0.6, 0.8) # Cold cyan/blue
    cool_rim = bpy.data.objects.new(name="Cool_Rim", object_data=cool_rim_data)
    bpy.context.scene.collection.objects.link(cool_rim)
    cool_rim.location = (-41.2, 3.0, 2.0)
    
    # 5. HYPER-REALISTIC PORTRAIT CAMERA (Close-up)
    # Positioned close to Xenomorph head at x=-40, y=-0.5, looking straight up at its elongated skull
    cam_data = bpy.data.cameras.new(name="Xeno_Portrait_Cam_Data")
    cam_data.lens = 50 # 50mm portrait lens
    cam_obj = bpy.data.objects.new(name="Xeno_Portrait_Cam", object_data=cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    
    # Position camera very close for extreme dramatic close-up portrait!
    cam_obj.location = (-39.8, -0.6, 1.4)
    # Look slightly up towards xeno's head (at x=-40.5, y=1.8, z=1.8)
    direction = mathutils.Vector((-40.5, 1.6, 1.95)) - cam_obj.location
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

build_combined_scene()
print("Cinematic spaceship corridor and Xenomorph close-up portrait generated successfully alongside temple ruins!")
"""
        res = send_command(sock, "execute_code", {"code": temple_code})
        print(f"Result: {res.get('result')}")
        
        target_dir = r"C:\Users\andre\Desktop\Nuova cartella (5)"
        if not os.path.exists(target_dir):
            target_dir = r"C:\Users\andre\OneDrive\Desktop\Nuova cartella (5)"
            os.makedirs(target_dir, exist_ok=True)
        
        # 1. Viewport screenshot (LookDev)
        print("Capturing viewport screenshot of the Xenomorph Close-up Portrait...")
        screenshot_path = os.path.join(target_dir, "tempio_greco.png")
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
