import bpy
import math
import mathutils

# Retrieve the wardrobe collection and materials
wardrobe_coll = bpy.data.collections.get("Stile_Liberty_Wardrobe")
wood_mat = bpy.data.materials.get("Walnut_Wood")
brass_mat = bpy.data.materials.get("Antique_Brass")

if not wardrobe_coll:
    # Fallback to active collection
    wardrobe_coll = bpy.context.collection

if not wood_mat:
    # Recreate wood mat if missing
    wood_mat = bpy.data.materials.new(name="Walnut_Wood")
    wood_mat.use_nodes = True
    principled = wood_mat.node_tree.nodes.get("Principled BSDF")
    if principled:
        principled.inputs['Base Color'].default_value = (0.24, 0.12, 0.06, 1.0)
        principled.inputs['Roughness'].default_value = 0.28

# Helper to apply material
def apply_material(obj, mat):
    if len(obj.data.materials) == 0:
        obj.data.materials.append(mat)
    else:
        obj.data.materials[0] = mat

# Cabinet Dimensions (same as wardrobe creation script)
w_width = 1.6
w_depth = 0.6
w_height = 2.2
base_h = 0.15
door_w = w_width / 2 - 0.015
door_h = w_height - 0.08
door_d = 0.03

# Position references
panel_y = w_depth/2 + door_d + 0.004  # Lay flat against panel surface
panel_z_center = w_height/2 + base_h  # 1.25

# 1. LEAF GENERATOR
def create_wood_leaf(name, location, rotation, scale=(0.04, 0.012, 0.08)):
    # Create a leaf shape using a scaled ico-sphere
    bpy.ops.mesh.primitive_ico_sphere_add(radius=1.0, subdivisions=2, location=location)
    leaf = bpy.context.active_object
    leaf.name = f"Carved_Leaf_{name}"
    leaf.scale = scale
    leaf.rotation_euler = rotation
    apply_material(leaf, wood_mat)
    
    # Add a subtle bevel for realistic carved wood edges
    bevel = leaf.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.002
    bevel.segments = 2
    
    # Add to wardrobe collection
    if leaf.name in bpy.context.scene.collection.objects:
        try:
            bpy.context.scene.collection.objects.unlink(leaf)
        except:
            pass
    if leaf.name not in wardrobe_coll.objects:
        wardrobe_coll.objects.link(leaf)
        
    return leaf

# 2. FLOWER BUD GENERATOR
def create_wood_bud(name, location, rotation):
    # A floral bud composed of a cup and petals
    # 1. Bud Cup
    bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.03, location=location)
    cup = bpy.context.active_object
    cup.name = f"Carved_Cup_{name}"
    cup.rotation_euler = rotation
    cup.scale = (1.0, 1.0, 0.8)
    bpy.ops.object.transform_apply(scale=True)
    apply_material(cup, wood_mat)
    
    # 2. Bud Petals (Cone)
    # Calculate offset along local Z axis of cup
    rot_matrix = cup.rotation_euler.to_matrix()
    z_offset = rot_matrix @ mathutils.Vector((0, 0, 0.025))
    petals_loc = (location[0] + z_offset.x, location[1] + z_offset.y, location[2] + z_offset.z)
    
    bpy.ops.mesh.primitive_cone_add(radius1=0.022, radius2=0.003, depth=0.04, location=petals_loc)
    petals = bpy.context.active_object
    petals.name = f"Carved_Petals_{name}"
    petals.rotation_euler = rotation
    apply_material(petals, wood_mat)
    
    # Link objects to collection
    for obj in [cup, petals]:
        if obj.name in bpy.context.scene.collection.objects:
            try:
                bpy.context.scene.collection.objects.unlink(obj)
            except:
                pass
        if obj.name not in wardrobe_coll.objects:
            wardrobe_coll.objects.link(obj)

# 3. ORGANIC VINE GENERATOR
def create_wood_vine(name, points_data, mirror_x=False):
    # Create a Bezier curve representing the swirling stems of Liberty style
    curve_data = bpy.data.curves.new(name=f"Vine_Curve_{name}", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.fill_mode = 'FULL'
    curve_data.bevel_depth = 0.008  # Thin elegant vine relief
    curve_data.bevel_resolution = 3
    
    polyline = curve_data.splines.new('BEZIER')
    # Start with 1 point, add rest
    polyline.bezier_points.add(len(points_data) - 1)
    
    for idx, pt in enumerate(points_data):
        bp = polyline.bezier_points[idx]
        x = -pt["co"][0] if mirror_x else pt["co"][0]
        y = pt["co"][1]
        z = pt["co"][2]
        bp.co = (x, y, z)
        
        # Mirror handle directions on X axis if mirrored
        hl = pt["hl"]
        hr = pt["hr"]
        if mirror_x:
            bp.handle_left = (-hl[0], hl[1], hl[2])
            bp.handle_right = (-hr[0], hr[1], hr[2])
        else:
            bp.handle_left = (hl[0], hl[1], hl[2])
            bp.handle_right = (hr[0], hr[1], hr[2])
            
    vine_obj = bpy.data.objects.new(f"Vine_{name}", curve_data)
    wardrobe_coll.objects.link(vine_obj)
    apply_material(vine_obj, wood_mat)
    return vine_obj

# Define the vine paths
# Vine A: Main upward sweeping stem
vine_a_points = [
    {"co": (-0.6, panel_y, 0.4), "hl": (-0.6, panel_y, 0.3), "hr": (-0.55, panel_y, 0.5)},
    {"co": (-0.3, panel_y, 0.8), "hl": (-0.45, panel_y, 0.7), "hr": (-0.2, panel_y, 0.9)},
    {"co": (-0.5, panel_y, 1.4), "hl": (-0.25, panel_y, 1.25), "hr": (-0.6, panel_y, 1.5)},
    {"co": (-0.2, panel_y, 1.8), "hl": (-0.4, panel_y, 1.7), "hr": (-0.1, panel_y, 1.9)},
    {"co": (-0.45, panel_y, 2.1), "hl": (-0.25, panel_y, 2.05), "hr": (-0.55, panel_y, 2.15)}
]

# Vine B: Side branch twisting towards the center
vine_b_points = [
    {"co": (-0.5, panel_y, 1.4), "hl": (-0.55, panel_y, 1.35), "hr": (-0.45, panel_y, 1.45)},
    {"co": (-0.2, panel_y, 1.2), "hl": (-0.35, panel_y, 1.3), "hr": (-0.15, panel_y, 1.15)},
    {"co": (-0.35, panel_y, 0.95), "hl": (-0.18, panel_y, 1.05), "hr": (-0.45, panel_y, 0.9)}
]

# Generate Left Door Vine Carvings
create_wood_vine("Left_Main", vine_a_points, mirror_x=False)
create_wood_vine("Left_Branch", vine_b_points, mirror_x=False)

# Generate Right Door Vine Carvings (Symmetrical)
create_wood_vine("Right_Main", vine_a_points, mirror_x=True)
create_wood_vine("Right_Branch", vine_b_points, mirror_x=True)

# Generate Symmetrical Leaves and Buds on Left and Right Doors
# We define positions for the left side and place them on both left and right (mirrored X)
decorations = [
    # Main stem base leaf
    {"loc": (-0.56, panel_y, 0.5), "rot": (0, math.radians(15), math.radians(45)), "type": "leaf"},
    # Mid-stem leaf
    {"loc": (-0.35, panel_y, 0.9), "rot": (0, -math.radians(15), math.radians(-30)), "type": "leaf"},
    # Branch intersection leaf
    {"loc": (-0.45, panel_y, 1.35), "rot": (0, math.radians(20), math.radians(60)), "type": "leaf"},
    # Upper-stem leaf
    {"loc": (-0.28, panel_y, 1.75), "rot": (0, -math.radians(15), math.radians(-25)), "type": "leaf"},
    # Tip flower bud
    {"loc": (-0.45, panel_y, 2.1), "rot": (math.radians(90), 0, math.radians(45)), "type": "bud"},
    # Side branch tip flower bud
    {"loc": (-0.35, panel_y, 0.95), "rot": (math.radians(90), 0, -math.radians(120)), "type": "bud"},
    # Extra leaf on side branch
    {"loc": (-0.22, panel_y, 1.15), "rot": (0, math.radians(10), math.radians(15)), "type": "leaf"}
]

for idx, dec in enumerate(decorations):
    lx, ly, lz = dec["loc"]
    rx, ry, rz = -lx, ly, lz  # Mirrored coordinates
    
    # Left Door decorations
    if dec["type"] == "leaf":
        create_wood_leaf(f"L_{idx}", (lx, ly, lz), dec["rot"])
        # Symmetrical Right Door
        r_rot = (dec["rot"][0], -dec["rot"][1], -dec["rot"][2])
        create_wood_leaf(f"R_{idx}", (rx, ry, rz), r_rot)
    elif dec["type"] == "bud":
        create_wood_bud(f"L_{idx}", (lx, ly, lz), dec["rot"])
        # Symmetrical Right Door
        r_rot = (dec["rot"][0], -dec["rot"][1], math.radians(180) - dec["rot"][2])
        create_wood_bud(f"R_{idx}", (rx, ry, rz), r_rot)

# 4. CARVED TOP CREST ON THE UPPER ARCH (Central floral crest)
# Beautiful floral centerpiece on the arch top
bpy.ops.mesh.primitive_ico_sphere_add(radius=0.07, subdivisions=3, location=(0, w_depth/2 + 0.02, w_height + base_h + 0.12))
top_center = bpy.context.active_object
top_center.name = "Crest_Center"
top_center.scale = (1.2, 0.3, 1.2)
bpy.ops.object.transform_apply(scale=True)
apply_material(top_center, wood_mat)
if top_center.name in bpy.context.scene.collection.objects:
    try:
        bpy.context.scene.collection.objects.unlink(top_center)
    except:
        pass
if top_center.name not in wardrobe_coll.objects:
    wardrobe_coll.objects.link(top_center)

# Add beautiful leaves sweeping outward from center crest
crest_leaves = [
    {"loc": (0.15, w_depth/2 + 0.02, w_height + base_h + 0.09), "rot": (0, math.radians(-15), math.radians(-10)), "scale": (0.15, 0.02, 0.06)},
    {"loc": (-0.15, w_depth/2 + 0.02, w_height + base_h + 0.09), "rot": (0, math.radians(15), math.radians(190)), "scale": (0.15, 0.02, 0.06)},
    {"loc": (0.35, w_depth/2 + 0.015, w_height + base_h + 0.05), "rot": (0, math.radians(-30), math.radians(-25)), "scale": (0.18, 0.02, 0.05)},
    {"loc": (-0.35, w_depth/2 + 0.015, w_height + base_h + 0.05), "rot": (0, math.radians(30), math.radians(205)), "scale": (0.18, 0.02, 0.05)}
]

for idx, cl in enumerate(crest_leaves):
    create_wood_leaf(f"Crest_{idx}", cl["loc"], cl["rot"], cl["scale"])

print("Floral carvings and wood details added successfully!")
