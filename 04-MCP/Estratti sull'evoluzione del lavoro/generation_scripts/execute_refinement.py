import socket
import json

def send_command(command_type, params=None):
    if params is None:
        params = {}
    host = '127.0.0.1'
    port = 9876
    payload = {"type": command_type, "params": params}
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.sendall(json.dumps(payload).encode('utf-8'))
    response = b""
    while True:
        chunk = s.recv(4096)
        if not chunk:
            break
        response += chunk
    s.close()
    return json.loads(response.decode('utf-8'))

code = """
import bpy
import math
import mathutils

def setup_materials():
    # 1. Xenomorph skin material
    mat_xeno = bpy.data.materials.get("XenomorphSkin")
    if not mat_xeno:
        mat_xeno = bpy.data.materials.new(name="XenomorphSkin")
    mat_xeno.use_nodes = True
    nodes = mat_xeno.node_tree.nodes
    links = mat_xeno.node_tree.links
    nodes.clear()
    
    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (200, 0)
    node_out.location = (500, 0)
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    
    # Biomechanical shiny black/blue
    node_bsdf.inputs['Base Color'].default_value = (0.012, 0.012, 0.02, 1.0)
    node_bsdf.inputs['Metallic'].default_value = 0.55
    node_bsdf.inputs['Roughness'].default_value = 0.14
    
    if 'Specular' in node_bsdf.inputs:
        node_bsdf.inputs['Specular'].default_value = 0.8
    elif 'Specular IOR Level' in node_bsdf.inputs:
        node_bsdf.inputs['Specular IOR Level'].default_value = 0.8
        
    # Bump for biomechanical textures
    node_noise = nodes.new(type='ShaderNodeTexNoise')
    node_noise.inputs['Scale'].default_value = 45.0
    node_noise.inputs['Detail'].default_value = 6.0
    node_noise.location = (-300, -100)
    
    node_bump = nodes.new(type='ShaderNodeBump')
    node_bump.inputs['Strength'].default_value = 0.07
    node_bump.inputs['Distance'].default_value = 0.08
    node_bump.location = (-50, -150)
    
    links.new(node_noise.outputs['Fac'], node_bump.inputs['Height'])
    links.new(node_bump.outputs['Normal'], node_bsdf.inputs['Normal'])

    # 2. Egg material
    mat_egg = bpy.data.materials.get("EggSkin")
    if not mat_egg:
        mat_egg = bpy.data.materials.new(name="EggSkin")
    mat_egg.use_nodes = True
    nodes_egg = mat_egg.node_tree.nodes
    links_egg = mat_egg.node_tree.links
    nodes_egg.clear()
    
    node_out_egg = nodes_egg.new(type='ShaderNodeOutputMaterial')
    node_bsdf_egg = nodes_egg.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf_egg.location = (200, 0)
    node_out_egg.location = (500, 0)
    links_egg.new(node_bsdf_egg.outputs['BSDF'], node_out_egg.inputs['Surface'])
    
    # Dark greenish-brown slimy shader
    node_bsdf_egg.inputs['Base Color'].default_value = (0.035, 0.045, 0.02, 1.0)
    node_bsdf_egg.inputs['Metallic'].default_value = 0.08
    node_bsdf_egg.inputs['Roughness'].default_value = 0.12
    
    if 'Specular' in node_bsdf_egg.inputs:
        node_bsdf_egg.inputs['Specular'].default_value = 1.0
    elif 'Specular IOR Level' in node_bsdf_egg.inputs:
        node_bsdf_egg.inputs['Specular IOR Level'].default_value = 1.0
        
    # Subsurface scattering
    if 'Subsurface' in node_bsdf_egg.inputs:
        node_bsdf_egg.inputs['Subsurface'].default_value = 0.15
        if 'Subsurface Color' in node_bsdf_egg.inputs:
            node_bsdf_egg.inputs['Subsurface Color'].default_value = (0.1, 0.04, 0.02, 1.0)
    elif 'Subsurface Weight' in node_bsdf_egg.inputs:
        node_bsdf_egg.inputs['Subsurface Weight'].default_value = 0.15
        node_bsdf_egg.inputs['Subsurface Radius'].default_value = (0.1, 0.04, 0.02)
        
    # Bump for slimy look
    node_noise_egg = nodes_egg.new(type='ShaderNodeTexNoise')
    node_noise_egg.inputs['Scale'].default_value = 30.0
    node_noise_egg.inputs['Detail'].default_value = 5.0
    node_noise_egg.location = (-300, -100)
    
    node_bump_egg = nodes_egg.new(type='ShaderNodeBump')
    node_bump_egg.inputs['Strength'].default_value = 0.09
    node_bump_egg.inputs['Distance'].default_value = 0.1
    node_bump_egg.location = (-50, -150)
    
    links_egg.new(node_noise_egg.outputs['Fac'], node_bump_egg.inputs['Height'])
    links_egg.new(node_bump_egg.outputs['Normal'], node_bsdf_egg.inputs['Normal'])

    # 3. Inner glowing egg sack material
    mat_inner = bpy.data.materials.get("EggInner")
    if not mat_inner:
        mat_inner = bpy.data.materials.new(name="EggInner")
    mat_inner.use_nodes = True
    nodes_inner = mat_inner.node_tree.nodes
    links_inner = mat_inner.node_tree.links
    nodes_inner.clear()
    
    node_out_inner = nodes_inner.new(type='ShaderNodeOutputMaterial')
    node_bsdf_inner = nodes_inner.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf_inner.location = (200, 0)
    node_out_inner.location = (500, 0)
    links_inner.new(node_bsdf_inner.outputs['BSDF'], node_out_inner.inputs['Surface'])
    
    node_bsdf_inner.inputs['Base Color'].default_value = (1.0, 0.12, 0.02, 1.0)
    node_bsdf_inner.inputs['Roughness'].default_value = 0.25
    
    if 'Emission' in node_bsdf_inner.inputs:
        node_bsdf_inner.inputs['Emission'].default_value = (1.0, 0.15, 0.02, 1.0)
    if 'Emission Strength' in node_bsdf_inner.inputs:
        node_bsdf_inner.inputs['Emission Strength'].default_value = 5.0
        
    print("Materials configured successfully!")

def create_alien_egg():
    # Remove existing Alien Egg objects if any
    for name in ["Alien_Egg", "Egg_Inner_Sack"]:
        obj = bpy.data.objects.get(name)
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)
            
    # Create UV sphere at location (-0.8, -0.3, -0.6)
    loc = (-0.8, -0.3, -0.6)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=0.35, location=loc)
    egg = bpy.context.active_object
    egg.name = "Alien_Egg"
    
    # Deform vertices to make an open egg
    mesh = egg.data
    
    # Need to go in object mode to deform mesh vertices via python
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
        
    for v in mesh.vertices:
        x, y, z = v.co
        
        # 1. Stretch Z to make it elongated
        z_stretch = 1.35
        local_z = z * z_stretch
        v.co.z = local_z
        
        # 2. Taper top, expand bottom
        taper = 1.0 - (local_z * 0.38)
        v.co.x = x * taper
        v.co.y = y * taper
        
        # 3. Flaps opening (local_z > 0.08)
        if local_z > 0.08:
            theta = math.atan2(v.co.y, v.co.x)
            # Four flaps
            weight = (math.cos(4 * theta) + 1.0) / 2.0
            h_factor = (local_z - 0.08) / 0.4
            if h_factor < 0:
                h_factor = 0
                
            r = math.sqrt(v.co.x**2 + v.co.y**2)
            if r > 0.001:
                ux = v.co.x / r
                uy = v.co.y / r
            else:
                ux, uy = 0.0, 0.0
                
            # Push outwards
            push = 0.38 * (h_factor ** 1.6) * weight
            v.co.x += ux * push
            v.co.y += uy * push
            
            # Pull down
            v.co.z -= 0.16 * (h_factor ** 2) * weight
            
    # Add modifiers
    # Solidify
    solid = egg.modifiers.new(name="Solidify", type='SOLIDIFY')
    solid.thickness = 0.03
    solid.offset = 1.0
    
    # Displace for skin folds/veins
    displace = egg.modifiers.new(name="Displace", type='DISPLACE')
    texture = bpy.data.textures.get("EggWrinkles")
    if not texture:
        texture = bpy.data.textures.new(name="EggWrinkles", type='CLOUDS')
    texture.noise_scale = 0.15
    texture.noise_depth = 4
    displace.texture = texture
    displace.strength = 0.022
    
    # Subdivision
    subd = egg.modifiers.new(name="Subdivision", type='SUBSURF')
    subd.levels = 2
    subd.render_levels = 3
    
    # Shade smooth
    bpy.ops.object.shade_smooth()
    
    # Apply material
    egg_mat = bpy.data.materials.get("EggSkin")
    if egg_mat:
        egg.data.materials.append(egg_mat)
        
    # Create the glowing inner sack (facehugger egg contents)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=0.18, location=(-0.8, -0.3, -0.73))
    inner = bpy.context.active_object
    inner.name = "Egg_Inner_Sack"
    inner.scale = (1.0, 1.0, 1.4)
    bpy.ops.object.shade_smooth()
    
    inner_mat = bpy.data.materials.get("EggInner")
    if inner_mat:
        inner.data.materials.append(inner_mat)
        
    print("Alien Egg created successfully!")

def align_xenomorph_joints():
    alignments = [
        ("Xenomorph_ArmUpper_L", "Xenomorph_Shoulder_L", "Xenomorph_Elbow_L", 0.4),
        ("Xenomorph_ArmLower_L", "Xenomorph_Elbow_L", (-0.75, -0.3, -0.7), 0.4),
        
        ("Xenomorph_ArmUpper_R", "Xenomorph_Shoulder_R", "Xenomorph_Elbow_R", 0.4),
        ("Xenomorph_ArmLower_R", "Xenomorph_Elbow_R", (0.75, -0.3, -0.7), 0.4),
        
        ("Xenomorph_LegUpper_L", "Xenomorph_Hip_L", "Xenomorph_Knee_L", 0.5),
        ("Xenomorph_LegLower_L", "Xenomorph_Knee_L", (-0.5, 0.1, -1.45), 0.5),
        
        ("Xenomorph_LegUpper_R", "Xenomorph_Hip_R", "Xenomorph_Knee_R", 0.5),
        ("Xenomorph_LegLower_R", "Xenomorph_Knee_R", (0.5, 0.1, -1.45), 0.5),
    ]
    
    for obj_name, start_ref, end_ref, orig_length in alignments:
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            print(f"Object {obj_name} not found!")
            continue
            
        if isinstance(start_ref, str):
            start_obj = bpy.data.objects.get(start_ref)
            if not start_obj:
                print(f"Start object {start_ref} not found!")
                continue
            p_start = start_obj.location.copy()
        else:
            p_start = mathutils.Vector(start_ref)
            
        if isinstance(end_ref, str):
            end_obj = bpy.data.objects.get(end_ref)
            if not end_obj:
                print(f"End object {end_ref} not found!")
                continue
            p_end = end_obj.location.copy()
        else:
            p_end = mathutils.Vector(end_ref)
            
        # Calculate midpoint, vector and length
        midpoint = (p_start + p_end) / 2.0
        obj.location = midpoint
        
        vec = p_end - p_start
        length = vec.length
        
        # Scale Z to fit the length
        obj.scale[2] = length / orig_length
        
        # Orient segment local Z with the joint vector
        vec.normalize()
        local_z = mathutils.Vector((0, 0, 1))
        q = local_z.rotation_difference(vec)
        obj.rotation_mode = 'XYZ'
        obj.rotation_euler = q.to_euler()
        print(f"Aligned joint {obj_name}")

def add_ribs_to_torso():
    torso = bpy.data.objects.get("Xenomorph_Torso")
    if not torso:
        print("Xenomorph_Torso not found for ribs!")
        return
        
    rib_offsets = [-0.18, -0.09, 0.0, 0.09, 0.18]
    
    # Remove old ribs if any
    for obj in list(bpy.data.objects):
        if obj.name.startswith("Xenomorph_Rib_"):
            bpy.data.objects.remove(obj, do_unlink=True)
            
    skin_mat = bpy.data.materials.get("XenomorphSkin")
    
    for i, z_offset in enumerate(rib_offsets):
        # Create a torus at torso center with Z offset
        loc = (torso.location.x, torso.location.y, torso.location.z + z_offset)
        bpy.ops.mesh.primitive_torus_add(
            align='WORLD', 
            location=loc, 
            major_radius=0.23, 
            minor_radius=0.024,
            abso_major_rad=True
        )
        rib = bpy.context.active_object
        rib.name = f"Xenomorph_Rib_{i}"
        
        # Flatten and stretch to match oval shape of the chest
        rib.scale[0] = 1.05
        rib.scale[1] = 0.85
        rib.scale[2] = 0.55
        
        # Rotate rib forward slightly
        rib.rotation_mode = 'XYZ'
        rib.rotation_euler[0] = math.radians(12)
        
        bpy.ops.object.shade_smooth()
        if skin_mat:
            rib.data.materials.append(skin_mat)
            
        # Parent to Torso and maintain relative transform
        rib.parent = torso
        rib.matrix_parent_inverse = torso.matrix_world.inverted()
        print(f"Added rib {i} to Xenomorph torso")

def setup_dramatic_lighting_and_camera():
    # 1. Colors and energy
    lights_info = {
        "KeyLight": {"color": (0.1, 0.6, 1.0), "energy": 550.0},
        "FillLight": {"color": (0.7, 0.15, 0.7), "energy": 180.0},
        "RimLight": {"color": (0.2, 1.0, 0.65), "energy": 600.0}
    }
    for name, info in lights_info.items():
        light_obj = bpy.data.objects.get(name)
        if light_obj and light_obj.type == 'LIGHT':
            light_obj.data.color = info["color"]
            light_obj.data.energy = info["energy"]
            
    # 2. Point camera at midpoint between Xenomorph and Egg
    camera = bpy.data.objects.get("Camera")
    if camera:
        # Move camera slightly to frame both characters perfectly
        # Xenomorph torso center: (0, 0, -0.2), Egg center: (-0.8, -0.3, -0.6)
        # We can place camera at (1.6, -5.5, 0.5) to zoom in and have beautiful dramatic perspective
        camera.location = (1.5, -5.5, 0.5)
        
        # Remove old trackers
        for c in list(camera.constraints):
            if c.type == 'TRACK_TO':
                camera.constraints.remove(c)
                
        # Create empty camera target
        target_name = "Camera_Target"
        target = bpy.data.objects.get(target_name)
        if not target:
            bpy.ops.object.empty_add(type='PLAIN_AXES', location=(-0.4, -0.15, -0.3))
            target = bpy.context.active_object
            target.name = target_name
        else:
            target.location = (-0.4, -0.15, -0.3)
            
        # Add tracker
        track = camera.constraints.new(type='TRACK_TO')
        track.target = target
        track.track_axis = 'TRACK_NEGATIVE_Z'
        track.up_axis = 'UP_Y'
        print("Camera configured and framed.")

# Run everything
setup_materials()
create_alien_egg()
align_xenomorph_joints()
add_ribs_to_torso()
setup_dramatic_lighting_and_camera()

print("ALL_DONE")
"""

res = send_command("execute_code", {"code": code})
print(res.get("result", {}).get("stdout", ""))
print(res.get("result", {}).get("stderr", ""))
